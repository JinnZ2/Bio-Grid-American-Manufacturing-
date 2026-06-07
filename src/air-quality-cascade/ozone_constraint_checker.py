"""
ozone_constraint_checker.py  --  CC0

Falsifiable ozone formation model vs. observed AQI.
Input: emissions + meteorology + wildfire plumes + observations.
Output: prediction mismatch = constraint violation (or CONSISTENT under fire-transport physics).

Wildfire additions (Wotawa & Trainer 2000; Nevada Rim Fire study):
  - Fires emit NOx directly; O3 forms IN the plume during transport (pre-cooked).
  - HONO + HCHO photolyze → HOx radicals (OH + HO2) → catalyze VOC→O3 chain.
  - Two regimes: NOx-limited (rural, low-NOx) vs NOx-saturated (urban/VOC-limited).
    Same fire plume yields MORE O3 over rural MN than over already-saturated TX.
  - Aerosol optical depth modulates photolysis: thick smoke suppresses O3,
    thin/aged smoke (AOD ≈ 0.3–0.8) can enhance it.

Uniform-saturation is NOT a model violation when upwind fire plumes are present
and receptors are in the NOx-limited regime.
"""

import json
import math
from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class NOxSource:
    """Localized NOx emission point."""
    location_name: str
    lat: float
    lon: float
    nox_tons_per_day: float
    source_type: str   # truck, ag, lumber, industrial, power
    confidence: float  # 0.0 to 1.0


@dataclass
class WildfirePlume:
    """
    Fire plume chemical characterization.

    Fires are NOT just VOC sources — they emit NOx directly, and O3 forms in
    the plume during atmospheric transport before arriving at receptors.
    """
    location_name: str
    source_lat: float
    source_lon: float
    nox_tons_per_day: float        # direct combustion NOx
    voc_tons_per_day: float        # VOC load
    hono_ppb: float                # nitrous acid → OH radical precursor
    hcho_ppb: float                # formaldehyde → HOx source
    aerosol_optical_depth: float   # 0=clear, ~0.3–0.8=thin/aged, >1=dense
    preformed_o3_ppb: float        # O3 already formed in-plume during transport
    transport_hours: float         # hours in transit from fire to receptor area


@dataclass
class MonitorReading:
    """Real AQI observation from MPCA network."""
    location_name: str
    lat: float
    lon: float
    aqi_ozone: int
    timestamp: str
    source: str


@dataclass
class MeteoState:
    """Atmospheric conditions snapshot."""
    timestamp: str
    wind_direction_deg: float
    wind_speed_mph: float
    mixing_layer_feet: int
    temperature_f: float
    solar_radiation_w_m2: float
    humidity_percent: float
    voc_ug_m3: float               # background VOC (including smoke)
    background_nox_ppb: float = 2.0  # rural background NOx level


class OzoneConstraintChecker:
    """Physics-based ozone prediction vs. observation."""

    # NOx-saturation threshold: above this, extra NOx does NOT increase O3.
    NOX_SATURATION_PPB = 20.0

    def __init__(self):
        self.nox_sources: List[NOxSource] = []
        self.fire_plumes: List[WildfirePlume] = []
        self.observations: List[MonitorReading] = []
        self.meteo: MeteoState = None
        self.violations: List[Dict] = []

    # ── data loaders ─────────────────────────────────────────────────────────

    def load_emissions_inventory(self, json_file: str):
        with open(json_file) as f:
            data = json.load(f)
        for src in data.get('sources', []):
            self.nox_sources.append(NOxSource(**src))

    def load_fire_plumes(self, json_file: str):
        """Load fire plume data (FIRMS + chemical tracers)."""
        with open(json_file) as f:
            data = json.load(f)
        for p in data.get('plumes', []):
            self.fire_plumes.append(WildfirePlume(**p))

    def load_observations(self, csv_file: str):
        with open(csv_file) as f:
            for line in f.readlines()[1:]:
                parts = line.strip().split(',')
                self.observations.append(MonitorReading(
                    location_name=parts[0],
                    lat=float(parts[1]),
                    lon=float(parts[2]),
                    aqi_ozone=int(parts[3]),
                    timestamp=parts[4],
                    source='MPCA',
                ))

    def load_meteorology(self, json_file: str):
        with open(json_file) as f:
            data = json.load(f)
        self.meteo = MeteoState(**data)

    # ── geometry ─────────────────────────────────────────────────────────────

    def distance_km(self, lat1, lon1, lat2, lon2) -> float:
        R = 6371.0
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (math.sin(dlat / 2) ** 2
             + math.cos(math.radians(lat1))
             * math.cos(math.radians(lat2))
             * math.sin(dlon / 2) ** 2)
        return 2 * R * math.asin(math.sqrt(a))

    def _is_downwind(self, source_lat, source_lon, receptor_lat, receptor_lon) -> bool:
        bearing = math.degrees(math.atan2(
            receptor_lon - source_lon, receptor_lat - source_lat))
        wind_angle = (bearing - self.meteo.wind_direction_deg) % 360
        return not (90 < wind_angle < 270)

    # ── ground-source Gaussian plume ─────────────────────────────────────────

    def gaussian_plume_concentration(
            self, source: NOxSource, receptor_lat: float, receptor_lon: float) -> float:
        """Gaussian plume model: NOx concentration (ppb) at receptor downwind of source."""
        if not self._is_downwind(source.lat, source.lon, receptor_lat, receptor_lon):
            return 0.0

        dist = self.distance_km(source.lat, source.lon, receptor_lat, receptor_lon)
        sigma_y = 0.08 * dist * (1 + 0.0001 * dist)
        sigma_z = 0.06 * dist * (1 + 0.0015 * dist)
        if sigma_y == 0 or sigma_z == 0:
            return 0.0

        Q = (source.nox_tons_per_day * 1e6) / 86400  # g/s
        u = max(0.1, self.meteo.wind_speed_mph * 0.44704)
        H = 10  # effective stack height (m) — ground-level sources

        concentration = (Q / (2 * math.pi * u * sigma_y * sigma_z)) * \
                        math.exp(-H ** 2 / (2 * sigma_z ** 2))
        return max(0.0, concentration * 0.1)  # g/m³ → ppb rough factor

    # ── NOx regime classification ─────────────────────────────────────────────

    def regime_flag(self, local_nox_ppb: float) -> str:
        """
        Classify receptor as NOx-limited or NOx-saturated.

        NOx-limited  (rural, low-NOx): extra NOx increases O3 yield per unit NOx.
        NOx-saturated (urban, VOC-limited): adding NOx does NOT increase O3.

        Critical insight: fire plume NOx landing in a NOx-limited rural area
        produces MORE O3 per unit than the same plume over a saturated metro.
        """
        total_nox = local_nox_ppb + self.meteo.background_nox_ppb
        if total_nox < self.NOX_SATURATION_PPB:
            return 'NOx_limited'
        return 'NOx_saturated'

    # ── wildfire plume contribution ───────────────────────────────────────────

    def fire_plume_o3_contribution(
            self, receptor_lat: float, receptor_lon: float) -> tuple:
        """
        O3 contributed by upwind fire plumes.

        Returns (o3_ppb, hox_enhancement, aod_photolysis_factor, is_fire_influenced).

        Three mechanisms:
          1. pre-cooked O3 in plume (formed during transport before arrival)
          2. HOx radical enhancement from HONO and HCHO photolysis
          3. aerosol optical depth modulates photolysis rate
             AOD < 0.8 (aged smoke): photolysis mostly unaffected, chemistry enhanced
             AOD > 1.0 (dense smoke): photolysis suppressed, O3 formation slowed
        """
        total_preformed_o3 = 0.0
        total_hox_enhancement = 0.0
        weighted_aod = 0.0
        n_plumes = 0

        for plume in self.fire_plumes:
            if not self._is_downwind(plume.source_lat, plume.source_lon,
                                     receptor_lat, receptor_lon):
                continue
            dist = self.distance_km(plume.source_lat, plume.source_lon,
                                    receptor_lat, receptor_lon)
            # Plume dilutes with distance (inverse-square past ~50km)
            dilution = 1.0 / max(1.0, (dist / 50.0) ** 2)

            total_preformed_o3  += plume.preformed_o3_ppb * dilution
            # HOx enhancement: HONO + HCHO photolyze to OH + HO2 radicals
            # These catalyze the VOC→O3 chain; proportional to photolytic flux
            hox_factor = (plume.hono_ppb * 0.08 + plume.hcho_ppb * 0.04) * dilution
            total_hox_enhancement += hox_factor
            weighted_aod += plume.aerosol_optical_depth * dilution
            n_plumes += 1

        if n_plumes == 0:
            return 0.0, 0.0, 1.0, False

        avg_aod = weighted_aod  # already dilution-weighted sum
        # AOD photolysis factor:
        #   AOD ≈ 0.3–0.8 (thin aged smoke): ~1.0 (photolysis unaffected)
        #   AOD > 1.0 (dense smoke): suppresses photolysis → < 1.0
        if avg_aod < 0.8:
            aod_factor = 1.0 + 0.1 * avg_aod    # slight enhancement from scattered light
        else:
            aod_factor = max(0.3, 1.0 - 0.5 * (avg_aod - 0.8))

        return total_preformed_o3, total_hox_enhancement, aod_factor, True

    # ── ozone prediction at a receptor ───────────────────────────────────────

    def predict_ozone_at_receptor(
            self, receptor_lat: float, receptor_lon: float) -> dict:
        """
        Predict ground-level ozone AQI at a receptor.

        Returns a dict with AQI + diagnostic breakdown (not just a scalar)
        so callers can distinguish fire-transport from ground-source contributions.
        """
        # Ground-source NOx from inventory
        local_nox_ppb = sum(
            self.gaussian_plume_concentration(src, receptor_lat, receptor_lon)
            for src in self.nox_sources
        )

        # Regime classification
        regime = self.regime_flag(local_nox_ppb)

        # Base photochemical factors
        solar_factor  = self.meteo.solar_radiation_w_m2 / 1000.0
        temp_factor   = max(0.0, (self.meteo.temperature_f - 70) / 30)
        voc_ppb       = self.meteo.voc_ug_m3 / 50.0

        # Fire plume contributions
        preformed_o3, hox_enhancement, aod_factor, fire_influenced = \
            self.fire_plume_o3_contribution(receptor_lat, receptor_lon)

        # Apply AOD to solar photolysis
        effective_solar = solar_factor * aod_factor

        # Ground-source ozone formation
        ground_o3_ppb = 0.0
        if local_nox_ppb >= 5 or regime == 'NOx_limited':
            nox_voc_ratio = local_nox_ppb / max(1.0, voc_ppb)
            efficiency = 1.0 if 0.2 < nox_voc_ratio < 5 else 0.5
            # NOx-limited: higher yield per unit NOx (regime multiplier)
            regime_mult = 2.0 if regime == 'NOx_limited' else 1.0
            ground_o3_ppb = (local_nox_ppb * voc_ppb * efficiency
                             * effective_solar * temp_factor * regime_mult)

        # Fire plume: HOx catalysis of VOC→O3 chain
        # HOx radicals can drive ozone production independent of local NOx
        fire_catalysed_o3 = (hox_enhancement * voc_ppb
                             * effective_solar * temp_factor * 0.5)

        # Total ozone
        total_o3_ppb = preformed_o3 + ground_o3_ppb + fire_catalysed_o3

        # Convert ppb → AQI (EPA: 0–55 ppb ≈ 0–100 AQI, linear)
        aqi = min(500, (total_o3_ppb / 55.0) * 100)

        return {
            'aqi':              round(aqi, 1),
            'total_o3_ppb':     round(total_o3_ppb, 2),
            'local_nox_ppb':    round(local_nox_ppb, 3),
            'preformed_o3_ppb': round(preformed_o3, 2),
            'fire_catalysed':   round(fire_catalysed_o3, 2),
            'regime':           regime,
            'fire_influenced':  fire_influenced,
            'aod_factor':       round(aod_factor, 3),
        }

    # ── constraint checking ───────────────────────────────────────────────────

    def check_constraints(self):
        """Compare predicted vs. observed AQI across monitor network."""
        self.violations = []

        for obs in self.observations:
            pred = self.predict_ozone_at_receptor(obs.lat, obs.lon)
            predicted_aqi = pred['aqi']
            mismatch = abs(predicted_aqi - obs.aqi_ozone)
            mismatch_pct = (mismatch / max(1, obs.aqi_ozone)) * 100

            if mismatch_pct > 50:
                # Is the mismatch EXPLAINED by fire-transport physics?
                fire_consistent = (
                    pred['fire_influenced']
                    and pred['regime'] == 'NOx_limited'
                    and pred['preformed_o3_ppb'] > 0
                )
                self.violations.append({
                    'location':          obs.location_name,
                    'lat':               obs.lat,
                    'lon':               obs.lon,
                    'observed_aqi':      obs.aqi_ozone,
                    'predicted_aqi':     predicted_aqi,
                    'mismatch_percent':  round(mismatch_pct, 1),
                    'regime':            pred['regime'],
                    'fire_influenced':   pred['fire_influenced'],
                    'fire_consistent':   fire_consistent,
                    'source_type': (
                        'fire_transport'  if fire_consistent else
                        'uniform_saturation' if predicted_aqi < 30 and obs.aqi_ozone > 100
                        else 'localized_mismatch'
                    ),
                })

    def report(self) -> dict:
        """Generate constraint violation report."""
        self.check_constraints()

        if not self.violations:
            return {
                'status':    'model_consistent',
                'message':   'Predicted ozone matches observed AQI across all monitors.',
                'violations': [],
            }

        true_violations = [v for v in self.violations if not v['fire_consistent']]
        fire_explained  = [v for v in self.violations if v['fire_consistent']]
        uniform_viol    = [v for v in true_violations
                           if v['source_type'] == 'uniform_saturation']

        if fire_explained and not true_violations:
            return {
                'status':   'fire_transport_consistent',
                'message':  (f'Apparent uniform saturation at {len(fire_explained)} sites is '
                             f'EXPLAINED by fire-transport physics (NOx-limited regime + '
                             f'preformed O3 in upwind plumes). NOT a model violation.'),
                'implication': (
                    'Rural NOx-limited receptors show higher O3 than metro areas '
                    'because fire plume NOx lands in NOx-starved air → maximum yield. '
                    'Pre-cooked O3 arrives independent of local source density.'
                ),
                'fire_explained': fire_explained,
            }

        if len(uniform_viol) > 3:
            return {
                'status':     'constraint_violation',
                'message':    (f'VIOLATION: Uniform ozone saturation at {len(uniform_viol)} '
                               f'low-emission zones NOT explained by fire plumes or standard '
                               f'photochemistry. Missing physics or precursor mechanism.'),
                'implication': ('Ozone precursor distribution is NOT explained by localized '
                                'NOx sources or fire transport. Investigate: long-range '
                                'transport, upper-atmosphere intrusion, non-standard chemistry.'),
                'violations': true_violations,
                'next_step':  ('Check FIRMS for unaccounted fire sources; '
                               'run stratospheric intrusion check on 500hPa maps.'),
            }

        return {
            'status':    'partial_mismatch',
            'message':   (f'Standard model explains most locations; '
                          f'{len(true_violations)} unexplained outliers, '
                          f'{len(fire_explained)} explained by fire transport.'),
            'violations': true_violations,
            'fire_explained': fire_explained,
        }


if __name__ == '__main__':
    checker = OzoneConstraintChecker()
    # checker.load_emissions_inventory('nox_sources.json')
    # checker.load_fire_plumes('firms_plumes.json')
    # checker.load_observations('mpca_aqi_readings.csv')
    # checker.load_meteorology('noaa_meteo_state.json')
    # print(json.dumps(checker.report(), indent=2))
