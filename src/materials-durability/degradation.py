"""
degradation.py  --  CC0

Two simulation paths for a single structure's life:

  simulate_life()       — analytical: uses failure_modes time-to-failure rates
                          summed as annual damage fractions; R0 + LSF govern
                          load-concentration cascade (archetypeRedundancy.js logic).

  simulate_life_graph() — graph-based: uses graph.LoadGraph edge damage
                          accumulation; edges fail when damage > capacity;
                          collapse = graph.connected() == False.
                          More physically detailed; slower per run.

Both return the same dict schema so callers are interchangeable.
"""

import math
from typing import Optional

from failure_modes import failure_times
from archetypes import load_sharing_factor, make_instance

CAPACITY_THRESHOLD = 0.0

_SAMPLE_YEARS = [1, 5, 10, 25, 50, 100, 150, 200, 300, 500, 750, 1000]

# All 18 archetype names match their graph topology key directly.
_GRAPH_KEY = {a: a for a in [
    "granite", "field_stone", "roman_pozzolan", "massive_arch", "concrete",
    "modern_reinforced", "lumber", "dry_stone",
    "timber_laced", "treehouse", "ice", "snow", "cob", "bamboo",
    "bamboo_and_clay", "willow_and_clay", "sod", "straw",
]}

# Annual edge damage scale factor (calibrated so critical edges fail in ~200–600yr)
_DAMAGE_SCALE = 0.005


# ─── analytical path ─────────────────────────────────────────────────────────

def simulate_life(archetype_name: str, env, years: int = 1000,
                  quality_factor: float = 1.0) -> dict:
    """
    Analytical simulation using failure_modes time-to-failure rates.

    Annual damage per mode = 1 / time_to_failure.
    Redundancy (R0 = columns) buffers load concentration as columns fail.
    Lateral ties (LSF) dampen the per-column overload spike.
    """
    from archetypes import make
    s          = make(archetype_name, env, quality_factor=quality_factor)
    inst       = make_instance(archetype_name, env, quality_factor)
    r0         = inst.initial_redundancy
    lsf        = load_sharing_factor(inst.props)

    times      = failure_times(s)
    base_rates = {m: (1.0 / t if t < 1e9 else 0.0) for m, t in times.items()}
    base_annual = sum(base_rates.values())

    capacity   = 1.0
    redundancy = r0
    collapse_yr: Optional[int] = None
    trajectory  = []
    sample_set  = set(_SAMPLE_YEARS)

    for yr in range(1, years + 1):
        surviving   = max(redundancy, 1)
        load_conc   = r0 / surviving
        shared_conc = load_conc * (1.0 - lsf * (1.0 - 1.0 / surviving))
        annual_dmg  = base_annual * shared_conc
        capacity   -= annual_dmg

        for k in range(r0, 0, -1):
            if capacity < (k / r0) and redundancy >= k:
                redundancy = k - 1
                break

        if yr in sample_set or capacity <= CAPACITY_THRESHOLD:
            trajectory.append((yr, max(redundancy, 0), max(0.0, capacity)))

        if capacity <= CAPACITY_THRESHOLD and collapse_yr is None:
            collapse_yr = yr
            break

    return {
        "initial_redundancy": r0,
        "collapse_year":      collapse_yr,
        "trajectory":         trajectory,
    }


# ─── graph-based path ────────────────────────────────────────────────────────

def _annual_edge_damage(meta: dict, env) -> float:
    """
    Annual damage fraction for one edge given its rates and the environment.

    water_rate and ft_rate are per-edge material properties set in graph.py.
    Environmental drivers: humidity+groundwater, freeze_thaw cycles, salinity,
    seismic factor applied to shear-weak edges (1 - shear_cap).
    """
    water = meta["water_rate"] * (env.humidity_pct / 100.0 + env.groundwater_level) / 2.0
    ft    = meta["ft_rate"]    * env.freeze_thaw_cycles / 60.0
    salt  = env.salinity       * meta["water_rate"] * 0.4
    seis  = env.seismic_factor * (1.0 - meta["shear_cap"])
    return (water + ft + salt + seis) * _DAMAGE_SCALE


def simulate_life_graph(archetype_name: str, env, years: int = 1000,
                        quality_factor: float = 1.0) -> dict:
    """
    Graph-based simulation via LoadGraph edge damage accumulation.

    Each alive edge accumulates annual damage from environmental rates.
    When damage exceeds its (jittered) capacity the edge is removed.
    Collapse = no source→sink path (graph.connected() == False).

    Thermal-melt branch: ice/snow use the analytical thermal_melt time
    (from failure_modes) instead of edge damage, since their failure is
    driven by temperature rather than material fatigue.

    Load concentration: as edges on a column are lost, surviving edges carry
    more load (moderated by g.load_share from lateral ties).
    """
    from graph import build_graph
    from archetypes import make as make_struct
    from failure_modes import thermal_melt as _thermal_melt

    gkey = _GRAPH_KEY.get(archetype_name)
    if gkey is None:
        raise ValueError(f"No graph topology for '{archetype_name}'")

    # Thermal-melt branch: structure dissolves at a fixed year
    s_probe = make_struct(archetype_name, env, quality_factor)
    melt_yr = _thermal_melt(s_probe)
    if melt_yr < float("inf"):
        melt_int = max(1, int(math.ceil(melt_yr)))
        trajectory = [(yr, 0, 0.0) for yr in _SAMPLE_YEARS if yr <= melt_int]
        if not trajectory or trajectory[-1][0] != melt_int:
            trajectory.append((melt_int, 0, 0.0))
        return {
            "initial_redundancy": 0,
            "collapse_year":      melt_int,
            "trajectory":         trajectory,
        }

    g           = build_graph(gkey)
    initial_r0  = g.redundancy()
    load_share  = g.load_share   # 1/(1 + 1.5*lateral) from _layered()

    collapse_yr: Optional[int] = None
    trajectory  = []
    sample_set  = set(_SAMPLE_YEARS)

    for yr in range(1, years + 1):
        current_r0  = g.redundancy()
        # Load concentration rises as paths are lost; load_share dampens it
        if initial_r0 > 0:
            raw_conc    = initial_r0 / max(current_r0, 1)
            load_factor = 1.0 + (raw_conc - 1.0) * (1.0 - load_share)
        else:
            load_factor = 1.0

        for key in list(g.alive_edges()):
            meta       = g.edge_meta[key]
            annual_dmg = _annual_edge_damage(meta, env) * load_factor / quality_factor
            meta["damage"] += annual_dmg
            if meta["damage"] >= meta["capacity"]:
                g.kill_edge(key)

        current_r0 = g.redundancy()
        cap_frac   = current_r0 / max(initial_r0, 1)

        if yr in sample_set or not g.connected():
            trajectory.append((yr, current_r0, max(0.0, cap_frac)))

        if not g.connected() and collapse_yr is None:
            collapse_yr = yr
            break

    return {
        "initial_redundancy": initial_r0,
        "collapse_year":      collapse_yr,
        "trajectory":         trajectory,
    }
