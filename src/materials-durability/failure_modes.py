"""
failure_modes.py  --  CC0

CALIBRATION CORRECTION (from source doc):
  The draft used  critical_mode = min(failure_modes, key=get)  over raw scores.
  Raw scores mix units and directions (some "bigger = worse", some not), so the
  min is not well-defined as "occurs first". Here each mode emits a
  TIME-TO-FAILURE in years (when its accumulated demand reaches capacity).
  critical_mode = the mode with the SHORTEST time. That is "fails first",
  unambiguously.

Each function returns years-to-failure (float). inf = effectively never under
these conditions. stdlib + math only.
"""

import math
from structure import Structure

INF = float("inf")


def _safe(years):
    return years if years > 0 else INF


def compression_crushing(s: Structure) -> float:
    """
    Instantaneous demand/capacity. If load >= capacity -> fails at year 0
    (returns small epsilon). Otherwise creep + strength decay set a clock.
    """
    load = s.loads.dead_load + s.loads.live_load
    capacity = s.material.compressive_strength * s.geometry.thickness_m
    if capacity <= 0:
        return 0.001
    util = load / capacity
    if util >= 1.0:
        return 0.001                      # already crushing
    # strength decays ~0.1%/yr; year when decayed capacity meets load
    # capacity(t) = capacity * 0.999**t ; solve 0.999**t = util
    return _safe(math.log(util) / math.log(0.999))


def joint_shear(s: Structure) -> float:
    """
    Shear at block joints. Driven by seismic + thrust. Tensile/friction limited.
    Lower tensile strength + higher seismic -> shorter time.
    """
    drive = (s.loads.seismic_factor + s.environment.seismic_factor) * \
            (s.loads.dead_load + s.loads.live_load)
    resist = s.material.tensile_strength * s.geometry.block_height_m + 1.0
    if drive <= 0:
        return INF
    ratio = drive / resist
    # map stress ratio to a time clock: high ratio -> fast
    return _safe(100.0 / (ratio + 1e-6))


def foundation_settlement(s: Structure) -> float:
    """
    Differential settlement accumulates; failure when it exceeds a tolerance
    set by span (longer span tolerates less angular distortion before cracking).
    tolerance angular distortion ~ 1/500 for masonry.
    """
    rate = s.environment.settlement_rate
    if rate <= 0:
        return INF
    allow = s.geometry.span_m / 500.0     # meters of differential before damage
    return _safe(allow / rate)


def freeze_thaw_damage(s: Structure) -> float:
    """
    Cyclic ice expansion. Damage per year ~ cycles * saturation. Failure when
    cumulative spall depth reaches a fraction of thickness.
    """
    cycles = s.environment.freeze_thaw_cycles
    sat = s.environment.humidity_pct / 100.0
    per_year = cycles * sat * 1.0e-4      # m of spall per year (EST)
    if per_year <= 0:
        return INF
    budget = 0.30 * s.geometry.thickness_m  # lose 30% thickness -> fail
    return _safe(budget / per_year)


def water_intrusion(s: Structure) -> float:
    """
    Saturation + hydrostatic pressure drive matrix degradation / wash-out and
    (for reinforced) corrosion. salinity accelerates.
    """
    drive = s.environment.groundwater_level * (1.0 + 2.0 * s.environment.salinity)
    if drive <= 0:
        return INF
    # better water resistance is captured upstream in archetype params via
    # material strength; here drive sets a clock scaled to thickness
    per_year = drive * 1.0e-3
    budget = 0.40 * s.geometry.thickness_m
    return _safe(budget / per_year)


def material_creep(s: Structure) -> float:
    """
    Creep strain accumulates; failure when total creep strain exceeds a limit
    (~0.5% for masonry before cracking redistributes load).
    """
    rate = s.material.creep_rate
    if rate <= 0:
        return INF
    creep_limit = 0.005
    return _safe(creep_limit / rate)


def erosion(s: Structure) -> float:
    """
    Surface loss from wind/water flux. Slow unless saturated + exposed.
    """
    flux = s.loads.wind_factor + s.environment.groundwater_level
    if flux <= 0:
        return INF
    per_year = flux * 5.0e-5
    budget = 0.50 * s.geometry.thickness_m
    return _safe(budget / per_year)


MODES = {
    "compression_crushing":   compression_crushing,
    "joint_shear":            joint_shear,
    "foundation_settlement":  foundation_settlement,
    "freeze_thaw_damage":     freeze_thaw_damage,
    "water_intrusion":        water_intrusion,
    "material_creep":         material_creep,
    "erosion":                erosion,
}


def failure_times(s) -> dict:
    """
    Returns {mode_name: years_to_failure}.
    Accepts any object with material/geometry/loads/environment attributes.
    If the object carries a _quality_factor attribute (set by archetypes.make),
    all finite times are scaled by it — better workmanship extends life.
    """
    q = getattr(s, "_quality_factor", 1.0)
    raw = {name: fn(s) for name, fn in MODES.items()}
    return {n: (t * q if t < INF else INF) for n, t in raw.items()}


def critical_mode(s):
    """Returns (mode_name, years_to_failure) for the mode that occurs FIRST."""
    times = failure_times(s)
    name = min(times, key=times.get)      # shortest time = fails first
    return name, times[name]
