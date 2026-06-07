"""
materials_degradation_cascade.py  --  CC0

Conductor and infrastructure corrosion under compounded air-quality stress.

Stressor chain:
  wildfire smoke + NOx saturation
    → SO2 oxidation → H2SO4 aerosols (secondary sulfate)
    → copper/aluminum conductor pitting
    → resistance increase → I²R losses
    → voltage drop → reactive power demand → grid instability

Cascade dynamics:
  - Baseline corrosion ~0.1 mm/yr (clean air)
  - H2SO4 plume: 2–5× multiplier
  - Temperature spike: 2× faster kinetics (Q10 rule)
  - High humidity: 3–5× faster
  - Combined stagnant episode: 30–75× baseline
  - A 50-year-design distribution line can fail in 6–12 months
    under compound conditions.
  - Pitting runaway: once depth exceeds oxide layer, galvanic
    current accelerates corrosion 5× further.
"""

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional


# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------

@dataclass
class AirQualityState:
    h2so4_concentration: float   # µg/m³ secondary sulfate aerosol
    o3_concentration:    float   # ppb
    salt_aerosol:        float   # µg/m³ (coastal exposure)
    relative_humidity:   float   # percent (0–100)
    temperature_c:       float


@dataclass
class ConductorSpec:
    """Physical description of a transmission or distribution line segment."""
    conductor_id:       str
    material:           str     # 'Cu', 'Al', 'ACSR' (Al conductor steel-reinforced)
    diameter_mm:        float   # total conductor diameter
    age_years:          float
    oxide_layer_um:     float   # initial protective oxide thickness in µm
    current_density:    float   # A/mm² (higher = more I²R heat)
    voltage_class:      str     # 'distribution' (< 69kV) vs 'transmission' (≥ 69kV)


@dataclass
class ConductorState:
    """Evolving state of a conductor segment over time."""
    spec:                ConductorSpec
    pitting_depth_um:    float = 0.0   # current pitting depth
    pitting_active:      bool  = False  # True once oxide layer breached
    resistance_ratio:    float = 1.0   # R / R_baseline
    hours_elapsed:       float = 0.0


# ---------------------------------------------------------------------------
# Corrosion physics
# ---------------------------------------------------------------------------

# Baseline corrosion rates in mm/yr (clean air, 50% RH, 20°C)
_BASELINE_CORROSION_MM_YR: Dict[str, float] = {
    'Cu':   0.002,   # copper is resistant; forms protective patina
    'Al':   0.005,   # aluminum oxide is protective but thin; more sensitive to acid
    'ACSR': 0.010,   # steel core more vulnerable once Al outer strands thin
}

# Oxide layer thickness (µm) — below this depth pitting runaway begins
_OXIDE_LAYER_UM: Dict[str, float] = {
    'Cu':   10.0,    # CuO/Cu2O patina ~ 5–15 µm on aged conductor
    'Al':   4.0,     # Al2O3 native oxide ~ 2–6 µm
    'ACSR': 6.0,     # zinc coating on steel varies
}


def h2so4_factor(h2so4_ug_m3: float) -> float:
    """
    H2SO4 aerosol corrosion multiplier.
    Nonlinear: acid attack accelerates as proton activity rises.
    Reference: 10 µg/m³ ≈ typical polluted urban; 50+ µg/m³ during episodes.
    """
    return 1.0 + (h2so4_ug_m3 / 10.0) ** 1.5


def o3_factor(o3_ppb: float) -> float:
    """Ozone oxidises metal surfaces; sub-linear above ~50 ppb."""
    return 1.0 + (o3_ppb / 50.0) ** 0.8


def humidity_factor(rh_percent: float) -> float:
    """
    Exponential humidity dependence — thin electrolyte film forms above ~70% RH.
    Below 50% RH: near-dry; above 80%: thin film continuously present.
    """
    return math.exp(rh_percent / 30.0) / math.exp(50.0 / 30.0)  # normalised to RH=50%


def temperature_factor(temp_c: float) -> float:
    """Arrhenius approximation: corrosion kinetics double every 10°C (Q10 rule)."""
    return 2.0 ** ((temp_c - 20.0) / 10.0)


def salt_factor(salt_ug_m3: float, material: str) -> float:
    """
    Chloride aerosol — highly aggressive especially to aluminium.
    Al forms AlCl3 which is soluble (unlike Al2O3) → breaks passive layer.
    """
    if material in ('Al', 'ACSR'):
        return 1.0 + (salt_ug_m3 / 5.0) ** 1.2  # Al is more sensitive
    return 1.0 + (salt_ug_m3 / 20.0) ** 0.8     # Cu more resistant


def effective_corrosion_rate(
        spec: ConductorSpec, aq: AirQualityState,
        pitting_active: bool = False) -> float:
    """
    Effective corrosion rate in mm/yr for a conductor in given air quality.

    Returns rate that can be used to advance pitting_depth over a timestep.
    Once pitting breaches the oxide layer, a 5× runaway multiplier applies.
    """
    baseline = _BASELINE_CORROSION_MM_YR.get(spec.material, 0.005)

    stressor = (h2so4_factor(aq.h2so4_concentration)
                * o3_factor(aq.o3_concentration)
                * humidity_factor(aq.relative_humidity)
                * temperature_factor(aq.temperature_c)
                * salt_factor(aq.salt_aerosol, spec.material))

    rate = baseline * stressor

    if pitting_active:
        rate *= 5.0  # galvanic acceleration once oxide layer is breached

    return rate


def time_to_failure(spec: ConductorSpec, aq: AirQualityState) -> float:
    """
    Estimated time to conductor failure (mm depth reaches failure criterion).
    Failure criterion: pitting reaches 30% of conductor radius.
    Accounts for the pitting-runaway phase transition.

    Returns time in years.
    """
    radius_mm = spec.diameter_mm / 2.0
    failure_depth_mm = 0.30 * radius_mm          # 30% radius → structural failure
    oxide_um = spec.oxide_layer_um or _OXIDE_LAYER_UM.get(spec.material, 5.0)
    oxide_mm = oxide_um / 1000.0

    # Phase 1: pre-runaway (0 → oxide layer depth)
    rate1 = effective_corrosion_rate(spec, aq, pitting_active=False)
    if rate1 <= 0:
        return float('inf')
    t1 = oxide_mm / rate1  # years to breach oxide

    if oxide_mm >= failure_depth_mm:
        return t1  # failure happens before runaway activates

    # Phase 2: post-runaway (oxide layer → failure depth)
    rate2 = effective_corrosion_rate(spec, aq, pitting_active=True)
    remaining_mm = failure_depth_mm - oxide_mm
    t2 = remaining_mm / rate2

    return t1 + t2


def design_life_remaining(spec: ConductorSpec, aq: AirQualityState,
                          nominal_design_life_yr: float = 50.0) -> dict:
    """
    Compare actual time-to-failure vs. nominal design life.
    Reports the fraction of design life remaining under current conditions.
    """
    ttf = time_to_failure(spec, aq)
    age_fraction_consumed = spec.age_years / nominal_design_life_yr
    fraction_remaining    = max(0.0, (ttf - spec.age_years) / nominal_design_life_yr)

    rate = effective_corrosion_rate(spec, aq)
    baseline = _BASELINE_CORROSION_MM_YR.get(spec.material, 0.005)
    stressor_mult = rate / baseline if baseline > 0 else 1.0

    return {
        'conductor_id':          spec.conductor_id,
        'material':              spec.material,
        'time_to_failure_yr':    round(ttf, 2),
        'design_life_fraction_remaining': round(fraction_remaining, 3),
        'stressor_multiplier':   round(stressor_mult, 1),
        'in_runaway_phase':      spec.oxide_layer_um < 1.0,
        'risk_level': (
            'CRITICAL' if ttf < 1.0 else
            'HIGH'     if ttf < 5.0 else
            'ELEVATED' if ttf < 15.0 else
            'NORMAL'
        ),
    }


# ---------------------------------------------------------------------------
# Resistance increase model
# ---------------------------------------------------------------------------

def resistance_increase_factor(pitting_depth_mm: float,
                                conductor_radius_mm: float) -> float:
    """
    Effective resistance ratio R / R_baseline as pitting reduces cross-section.

    Pitting doesn't uniformly reduce the cross-section — it concentrates
    current through a smaller effective area, so resistance rises faster than
    the simple area-fraction formula.

    Uses an empirical cubic correction.
    """
    area_fraction_lost = min(1.0, (pitting_depth_mm / conductor_radius_mm) ** 2)
    effective_area_fraction = max(0.01, 1.0 - area_fraction_lost)
    return 1.0 / effective_area_fraction   # R ∝ 1/A


def i2r_loss_increase(resistance_ratio: float, baseline_i2r_kw: float) -> float:
    """I²R losses increase linearly with resistance (at constant current)."""
    return baseline_i2r_kw * (resistance_ratio - 1.0)


# ---------------------------------------------------------------------------
# Batch assessment
# ---------------------------------------------------------------------------

def assess_conductor_fleet(
        conductors: List[ConductorSpec],
        aq: AirQualityState,
        nominal_design_life_yr: float = 50.0) -> List[dict]:
    """
    Assess all conductors in a fleet and return sorted risk list.
    """
    results = [design_life_remaining(s, aq, nominal_design_life_yr)
               for s in conductors]
    results.sort(key=lambda r: r['time_to_failure_yr'])
    return results


def stagnant_episode_multiplier(aq: AirQualityState) -> float:
    """
    Combined stressor multiplication during a stagnant pollution episode.
    During extended stagnation (heat dome + fire smoke + no mixing):
      H2SO4 builds up, temp rises, RH stays high → 30–75× baseline corrosion.
    """
    return (h2so4_factor(aq.h2so4_concentration)
            * o3_factor(aq.o3_concentration)
            * humidity_factor(aq.relative_humidity)
            * temperature_factor(aq.temperature_c))
