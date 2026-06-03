"""
renewal.py  --  CC0

The second axis. Longevity-to-horizon is the wrong yardstick for cultures that
built for RENEWAL. This module scores each system against ITS OWN design intent
and computes lifecycle cost as a FLUX (per shelter-year), not a stock.

Two regimes, two fitness definitions:

  PERMANENT intent : fitness = did it reach its design life?  (longevity matters)
  RENEWAL intent   : fitness = does it deliver its designed lifecycle cheaply and
                     return to substrate?  early "collapse" is not failure if it
                     was the planned rebuild cadence.

Lifecycle quantities over a horizon H (rebuild each time it ends):
  rebuilds            = H / actual_life
  build_burden_flux   = renewal_cost / actual_life          (effort per shelter-yr)
  substrate_debt_flux = (1 - return_to_substrate) / actual_life
                        (un-returned material accumulated per shelter-yr)
  A granite wall: one build, huge renewal_cost, near-zero return -> LOW build flux
    (amortized over 1000yr) but HIGH persistent substrate debt per shelter-yr.
  A sod house: many rebuilds, tiny renewal_cost, return ~1.0 -> modest build flux,
    near-ZERO substrate debt. Different instrument, different verdict.
"""

from archetypes import philosophy, REGISTRY


def lifecycle(archetype_key, actual_life_yr, horizon=500):
    """
    Compute lifecycle fluxes for one archetype given its SIMULATED actual life
    in some environment. actual_life_yr None means it survived the horizon.
    """
    p = philosophy(archetype_key)
    life = actual_life_yr if actual_life_yr else horizon
    life = max(life, 1e-3)

    rebuilds = horizon / life
    build_burden_flux = p["renewal_cost"] / life
    substrate_debt_flux = (1.0 - p["return_to_substrate"]) / life

    # fitness-by-intent
    if p["intent"] == "permanent":
        # reached design life? ratio capped at 1
        fitness = min(1.0, life / p["design_life_yr"])
        verdict = "reached design life" if life >= p["design_life_yr"] else "fell short"
    else:
        # renewal: met the planned cadence is enough; reward clean+cheap return
        met = 1.0 if life >= 0.6 * p["design_life_yr"] else life / (0.6 * p["design_life_yr"])
        cleanliness = p["return_to_substrate"]
        cheapness = 1.0 - p["renewal_cost"]
        fitness = met * (0.5 * cleanliness + 0.5 * cheapness)
        verdict = ("renews clean+cheap" if (cleanliness > 0.8 and cheapness > 0.8)
                   else "renews" if met >= 1.0 else "under-built for cadence")

    return {
        "intent": p["intent"],
        "design_life_yr": p["design_life_yr"],
        "actual_life_yr": round(life, 2),
        "rebuilds_over_horizon": round(rebuilds, 2),
        "build_burden_flux": build_burden_flux,
        "substrate_debt_flux": substrate_debt_flux,
        "return_to_substrate": p["return_to_substrate"],
        "renewal_cost": p["renewal_cost"],
        "fitness": round(fitness, 3),
        "verdict": verdict,
    }


def compare(results_by_archetype, horizon=500):
    """
    results_by_archetype: {key: median_collapse_or_None}
    Returns a list of lifecycle dicts sorted by substrate_debt_flux ascending
    (lowest lifecycle debt first -- the renewal lens).
    """
    out = []
    for k, life in results_by_archetype.items():
        lc = lifecycle(k, life, horizon=horizon)
        lc["archetype"] = k
        out.append(lc)
    out.sort(key=lambda d: d["substrate_debt_flux"])
    return out
