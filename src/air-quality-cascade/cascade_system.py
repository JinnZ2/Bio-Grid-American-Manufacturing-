"""
cascade_system.py  --  CC0

Coupled cascade simulation:

  air_quality → cooling_efficiency → thermal_load → electrical_demand → grid_stability
       ↑                                                                        ↓
       └────────────── (feedback: grid heat → local temp rise) ────────────────┘
                                                    ↑
                                     geomagnetic forcing

Purpose: not to predict the exact failure date, but to MAP BOTTLENECKS:
where does the system become brittle? Where is the leverage point where
small upstream changes (air chemistry, cooling efficiency, transformer
thermal margin) produce outsized downstream failures?

Nonlinear regime collapse: the system doesn't fail additively — it hits
a threshold (transformer overload + GIC + degraded conductor + heat dome)
and enters a qualitatively different state.

stdlib only. CC0.
"""

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from materials_degradation_cascade import (
    AirQualityState, ConductorSpec, effective_corrosion_rate,
    resistance_increase_factor, i2r_loss_increase,
    stagnant_episode_multiplier,
)


# ---------------------------------------------------------------------------
# Layer 1: Cooling system degradation from air quality
# ---------------------------------------------------------------------------

@dataclass
class CoolingSystemSpec:
    """Data center or industrial cooling unit."""
    facility_id:           str
    design_capacity_kw:    float   # rated heat rejection capacity
    heat_exchanger_area_m2: float  # effective surface area
    airside_design_dp_pa:  float   # design pressure drop (clean coils)
    age_years:             float


def cooling_efficiency_loss(
        aq: AirQualityState,
        spec: CoolingSystemSpec,
        fouling_rate_base: float = 0.002) -> dict:
    """
    Air quality degrades heat exchanger efficiency through fouling:
      - PM + aerosols (H2SO4, smoke organics) coat fin surfaces
      - Ozone oxidises polymer fin coatings → surface roughness increase
      - Efficiency loss raises thermal resistance → reduced heat rejection
      - Reduced heat rejection → data centre (or industrial) thermal stress

    Returns fractional cooling capacity loss and thermal headroom remaining.
    """
    # Aerosol fouling rate: H2SO4 + smoke organics stick to heat exchanger fins
    h2so4_foul = aq.h2so4_concentration / 10.0  # normalised fouling index
    o3_foul    = aq.o3_concentration / 100.0     # ozone oxidises fin coating
    humidity_foul = 1.0 + (aq.relative_humidity - 50.0) / 100.0  # hygroscopic growth

    annual_fouling_rate = fouling_rate_base * (h2so4_foul + o3_foul) * humidity_foul

    # Cumulative fouling over facility age (simplified integral)
    cumulative_fouling_fraction = 1.0 - math.exp(-annual_fouling_rate * spec.age_years)

    # Efficiency loss: pressure-drop model (Darcy-Weisbach)
    # As fin surface fouls, pressure drop increases → reduced airflow if fan-limited
    dp_ratio = 1.0 / max(0.05, 1.0 - cumulative_fouling_fraction * 0.8)
    airflow_reduction = max(0.0, 1.0 - 1.0 / math.sqrt(dp_ratio))  # sqrt(ΔP) ∝ flow

    # Heat rejection capacity loss ≈ proportional to airflow reduction
    capacity_loss_fraction = airflow_reduction * 0.7   # partial compensation from temp delta

    # During high-ozone + high-temp: thermal headroom shrinks further
    ambient_temp_penalty = max(0.0, (aq.temperature_c - 35.0) / 20.0)
    total_capacity_loss  = min(0.95, capacity_loss_fraction + ambient_temp_penalty)

    return {
        'facility_id':               spec.facility_id,
        'cumulative_fouling_frac':   round(cumulative_fouling_fraction, 3),
        'airflow_reduction_frac':    round(airflow_reduction, 3),
        'capacity_loss_frac':        round(total_capacity_loss, 3),
        'effective_capacity_kw':     round(spec.design_capacity_kw * (1.0 - total_capacity_loss), 1),
        'risk': ('CRITICAL' if total_capacity_loss > 0.60 else
                 'HIGH'     if total_capacity_loss > 0.35 else
                 'ELEVATED' if total_capacity_loss > 0.15 else
                 'NORMAL'),
    }


# ---------------------------------------------------------------------------
# Layer 2: Thermal load → electrical demand spike
# ---------------------------------------------------------------------------

@dataclass
class GridZoneSpec:
    """Electrical grid zone characteristics."""
    zone_id:                  str
    peak_load_mw:             float   # historical peak demand
    base_ac_fraction:         float   # fraction of load that is air conditioning
    data_center_load_mw:      float   # committed data centre load
    industrial_load_mw:       float   # industrial process load
    transformer_capacity_mw:  float   # substation transformer nameplate
    transformer_age_years:    float   # older = lower thermal withstand


def demand_spike(
        zone: GridZoneSpec,
        temp_c: float,
        cooling_capacity_loss_frac: float,
        data_center_headroom_frac: float) -> dict:
    """
    Model load increase from:
      1. Ambient temperature → AC demand rise (nonlinear above ~32°C)
      2. Degraded data-centre cooling → backup cooling electrical load
      3. Industrial process load increase from elevated inlet temperatures

    Returns estimated demand delta and transformer loading fraction.
    """
    # AC load: nonlinear above 32°C (base case)
    ac_sensitivity = 1.0 + max(0.0, (temp_c - 32.0) / 5.0) ** 1.5
    ac_demand = zone.peak_load_mw * zone.base_ac_fraction * ac_sensitivity

    # Data centre supplemental cooling: degraded primary → backup kicks in
    dc_supplemental = (zone.data_center_load_mw
                       * cooling_capacity_loss_frac   # fractional degradation
                       * 0.15)                        # ~15% power overhead for backup

    # Industrial: elevated temperatures increase process cooling demand
    industrial_extra = zone.industrial_load_mw * max(0.0, (temp_c - 30.0) / 40.0)

    total_demand = ac_demand + dc_supplemental + industrial_extra
    transformer_loading = total_demand / max(1.0, zone.transformer_capacity_mw)

    # Transformer thermal withstand degrades with age
    age_derate = max(0.60, 1.0 - 0.008 * zone.transformer_age_years)

    return {
        'zone_id':                    zone.zone_id,
        'ac_demand_mw':               round(ac_demand, 2),
        'dc_supplemental_mw':         round(dc_supplemental, 2),
        'industrial_extra_mw':        round(industrial_extra, 2),
        'total_demand_mw':            round(total_demand, 2),
        'transformer_loading_frac':   round(transformer_loading, 3),
        'transformer_age_derate':     round(age_derate, 3),
        'effective_loading_frac':     round(transformer_loading / age_derate, 3),
        'overload_risk': ('TRIP'     if transformer_loading / age_derate > 1.20 else
                          'CRITICAL' if transformer_loading / age_derate > 1.00 else
                          'HIGH'     if transformer_loading / age_derate > 0.85 else
                          'NORMAL'),
    }


# ---------------------------------------------------------------------------
# Layer 3: Geomagnetic forcing
# ---------------------------------------------------------------------------

@dataclass
class GeomagneticState:
    """
    Space weather state driving geomagnetically induced currents (GIC).
    GIC bias transformers toward saturation → extra reactive power consumption
    and harmonic distortion; in severe events, winding overheating.
    """
    kp_index:          float   # Kp 0–9; ≥ 7 = major storm
    dst_nt:            float   # Dst (nT); < -100 = severe storm
    solar_wind_bz_nt:  float   # IMF Bz (southward negative → geoeffective)
    local_latitude:    float   # degrees; higher latitude = stronger GIC
    ground_resistivity: float  # Ω·m; low-resistivity soils amplify GIC


def gic_transformer_stress(geo: GeomagneticState, zone: GridZoneSpec) -> dict:
    """
    Estimate transformer GIC stress from geomagnetic state.

    GIC amplitude scales with:
      - Kp / Dst magnitude
      - Latitude (cosine-law to geomagnetic pole)
      - Ground resistivity (lower = higher GIC)
      - Transmission line length / orientation

    Returns normalised GIC stress factor and risk level.
    """
    # Geoeffectiveness: Bz southward + high Kp
    geo_driver = max(0.0, -geo.solar_wind_bz_nt) / 10.0 + max(0.0, geo.kp_index - 5) / 4.0

    # Latitude weighting (peak GIC at ~65° geomagnetic latitude)
    lat_weight = math.cos(math.radians(abs(geo.local_latitude - 65.0) * 0.5))

    # Ground conductivity: lower resistivity → higher GIC
    conductivity_factor = 1.0 / math.log(max(10.0, geo.ground_resistivity))

    gic_stress = geo_driver * lat_weight * conductivity_factor * 10.0  # normalise to ~0–5 scale

    # Extra reactive power demand from half-cycle saturation
    reactive_demand_pct = gic_stress * 3.0  # rough: 1 unit GIC → 3% extra reactive demand

    return {
        'gic_stress':              round(gic_stress, 3),
        'reactive_demand_pct':     round(reactive_demand_pct, 2),
        'transformer_heating_mult': round(1.0 + gic_stress * 0.2, 3),
        'risk': ('CRITICAL' if gic_stress > 3.0 else
                 'HIGH'     if gic_stress > 1.5 else
                 'ELEVATED' if gic_stress > 0.5 else
                 'LOW'),
    }


# ---------------------------------------------------------------------------
# Compound failure model
# ---------------------------------------------------------------------------

@dataclass
class CascadeScenario:
    """All inputs for a compound failure assessment."""
    air_quality:       AirQualityState
    conductors:        List[ConductorSpec]
    cooling_systems:   List[CoolingSystemSpec]
    grid_zones:        List[GridZoneSpec]
    geomagnetic:       GeomagneticState
    ambient_temp_c:    float


def compound_failure_probability(scenario: CascadeScenario) -> dict:
    """
    Estimate compound failure probability from simultaneous stressors.

    Nonlinear aggregation: the cascade doesn't fail additively. The
    critical insight is REGIME COLLAPSE — when multiple subsystems
    approach their limits simultaneously, small perturbations can tip
    the whole system.

    Returns a risk scorecard with bottleneck identification.
    """
    results = {}

    # ── L1: Air quality → conductor corrosion ────────────────────────────────
    stressor = stagnant_episode_multiplier(scenario.air_quality)
    worst_conductor = None
    min_ttf = float('inf')
    for c in scenario.conductors:
        rate = effective_corrosion_rate(c, scenario.air_quality)
        baseline_rate = 0.005
        ttf = c.diameter_mm / 2 * 0.30 / rate  # rough time to 30% radius failure
        if ttf < min_ttf:
            min_ttf, worst_conductor = ttf, c.conductor_id
    results['conductor'] = {
        'stressor_mult':     round(stressor, 1),
        'min_ttf_years':     round(min_ttf, 2),
        'worst_conductor':   worst_conductor,
        'risk': 'CRITICAL' if min_ttf < 1 else 'HIGH' if min_ttf < 5 else 'NORMAL',
    }

    # ── L2: Cooling degradation ───────────────────────────────────────────────
    cooling_results = [cooling_efficiency_loss(scenario.air_quality, cs)
                       for cs in scenario.cooling_systems]
    max_loss = max((r['capacity_loss_frac'] for r in cooling_results), default=0.0)
    worst_cooling = next((r['facility_id'] for r in cooling_results
                          if r['capacity_loss_frac'] == max_loss), None)
    results['cooling'] = {
        'max_capacity_loss_frac': round(max_loss, 3),
        'worst_facility':        worst_cooling,
        'risk': cooling_results[0]['risk'] if cooling_results else 'UNKNOWN',
    }

    # ── L3: Demand spike → transformer loading ────────────────────────────────
    demand_results = [demand_spike(z, scenario.ambient_temp_c,
                                   max_loss, 1.0 - max_loss)
                      for z in scenario.grid_zones]
    max_loading = max((r['effective_loading_frac'] for r in demand_results), default=0.0)
    worst_zone = next((r['zone_id'] for r in demand_results
                       if r['effective_loading_frac'] == max_loading), None)
    results['grid_demand'] = {
        'max_transformer_loading': round(max_loading, 3),
        'worst_zone':             worst_zone,
        'risk': demand_results[0]['overload_risk'] if demand_results else 'UNKNOWN',
    }

    # ── L4: Geomagnetic forcing ───────────────────────────────────────────────
    gic_results = [gic_transformer_stress(scenario.geomagnetic, z)
                   for z in scenario.grid_zones]
    max_gic = max((r['gic_stress'] for r in gic_results), default=0.0)
    results['geomagnetic'] = {
        'max_gic_stress': round(max_gic, 3),
        'risk': gic_results[0]['risk'] if gic_results else 'LOW',
    }

    # ── Compound risk: nonlinear aggregation ─────────────────────────────────
    # Risk layers are not additive — they compound multiplicatively when
    # multiple systems are near their thresholds simultaneously.
    #
    # Each layer above threshold contributes a multiplier:
    #   conductor near failure + transformer near overload + GIC stress
    #   → regime collapse probability rises steeply

    layer_stress = []
    if min_ttf < 5:
        layer_stress.append(min(3.0, 5.0 / max(0.1, min_ttf)))   # conductor stress
    if max_loss > 0.35:
        layer_stress.append(1.0 + max_loss * 2.0)                 # cooling stress
    if max_loading > 0.85:
        layer_stress.append(1.0 + (max_loading - 0.85) * 6.0)     # transformer stress
    if max_gic > 1.0:
        layer_stress.append(1.0 + max_gic * 0.5)                  # GIC stress

    # Compound factor: product of simultaneous stressors (not sum)
    compound_factor = 1.0
    for s in layer_stress:
        compound_factor *= s
    # Normalise to 0–1 probability via logistic
    compound_prob = 1.0 / (1.0 + math.exp(-0.3 * (compound_factor - 5.0)))

    results['compound'] = {
        'layers_stressed':       len(layer_stress),
        'compound_factor':       round(compound_factor, 2),
        'cascade_probability':   round(compound_prob, 3),
        'regime': ('CASCADE_IMMINENT'  if compound_prob > 0.80 else
                   'HIGH_RISK'         if compound_prob > 0.50 else
                   'BRITTLE'           if compound_prob > 0.20 else
                   'RESILIENT'),
        'bottleneck': (
            'CONDUCTOR_FAILURE'  if (layer_stress and min_ttf < 2) else
            'TRANSFORMER_OVERLOAD' if max_loading > 1.0 else
            'COOLING_COLLAPSE'   if max_loss > 0.6 else
            'GIC_SATURATION'     if max_gic > 3.0 else
            'DISTRIBUTED_STRESS'
        ),
    }

    return results


def bottleneck_report(scenario: CascadeScenario) -> str:
    """Human-readable bottleneck analysis."""
    result = compound_failure_probability(scenario)
    comp   = result['compound']
    lines  = [
        "=" * 60,
        "CASCADE RISK ASSESSMENT",
        "=" * 60,
        f"Regime:              {comp['regime']}",
        f"Cascade probability: {comp['cascade_probability']:.1%}",
        f"Primary bottleneck:  {comp['bottleneck']}",
        f"Layers stressed:     {comp['layers_stressed']} / 4",
        f"Compound factor:     {comp['compound_factor']:.1f}×",
        "",
        "Layer breakdown:",
        f"  Conductor: ttf={result['conductor']['min_ttf_years']:.1f}yr"
          f"  stressor={result['conductor']['stressor_mult']:.0f}×"
          f"  [{result['conductor']['risk']}]",
        f"  Cooling:   loss={result['cooling']['max_capacity_loss_frac']:.0%}"
          f"  [{result['cooling']['risk']}]",
        f"  Grid:      loading={result['grid_demand']['max_transformer_loading']:.0%}"
          f"  [{result['grid_demand']['risk']}]",
        f"  GeoMag:    GIC={result['geomagnetic']['max_gic_stress']:.2f}"
          f"  [{result['geomagnetic']['risk']}]",
        "=" * 60,
    ]
    return "\n".join(lines)
