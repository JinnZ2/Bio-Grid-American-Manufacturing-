"""
degradation.py  --  CC0

Year-by-year capacity trajectory for a single structure.

Capacity starts at 1.0 and decays as each active failure mode contributes
annual damage. Redundancy (graph-theory R0 = columns) provides a structural
buffer: losing one column shifts more load onto survivors, accelerating
subsequent degradation.

Lateral ties (load_sharing_factor) reduce the load-concentration spike after
each column loss — they don't add columns (R0 unchanged) but they slow the
cascade. This is the physical recast from archetypeRedundancy.js.
"""

import math
from typing import Optional

from failure_modes import failure_times
from archetypes import load_sharing_factor

CAPACITY_THRESHOLD = 0.0

_SAMPLE_YEARS = [1, 5, 10, 25, 50, 100, 150, 200, 300, 500, 750, 1000]


def simulate_life(archetype_name: str, env, years: int = 1000, quality_factor: float = 1.0) -> dict:
    """
    Simulate a single structure from t=0 to collapse or `years`.

    Parameters
    ----------
    archetype_name  : one of ARCHETYPES
    env             : Environment (from simulate.draw_env)
    years           : simulation horizon
    quality_factor  : lognormal workmanship multiplier (default 1.0 = mean quality)

    Returns
    -------
    dict with:
        initial_redundancy : int    — R0 (columns)
        collapse_year      : int or None
        trajectory         : list of (year, redundancy, capacity_frac)
                             sampled at _SAMPLE_YEARS + collapse year
    """
    from archetypes import make
    s          = make(archetype_name, env, quality_factor=quality_factor)
    r0         = s.initial_redundancy
    lsf        = load_sharing_factor(s.props)

    # Annual damage rate per mode = 1 / time_to_failure (modes are independent)
    times      = failure_times(s)
    base_rates = {m: (1.0 / t if t < 1e9 else 0.0) for m, t in times.items()}
    base_annual = sum(base_rates.values())

    capacity    = 1.0
    redundancy  = r0
    collapse_yr: Optional[int] = None
    trajectory  = []
    sample_set  = set(_SAMPLE_YEARS)

    for yr in range(1, years + 1):
        # Load concentration: as columns are lost, survivors bear more
        surviving    = max(redundancy, 1)
        load_conc    = r0 / surviving

        # Lateral ties reduce the concentration spike on any single column.
        # (The sharing factor is a property of the intact archetype; after
        # column loss the remaining ties still help the survivors.)
        shared_conc  = load_conc * (1.0 - lsf * (1.0 - 1.0 / surviving))

        annual_dmg   = base_annual * shared_conc
        capacity    -= annual_dmg

        # Step down redundancy as capacity crosses column-loss thresholds
        # (each 1/R0 drop in capacity ≈ one column effectively failed)
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
