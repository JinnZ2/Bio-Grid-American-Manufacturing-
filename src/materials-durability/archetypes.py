"""
archetypes.py  --  CC0

Material archetype definitions grounded in construction history.

`columns` carries the graph-theory R0 concept from archetypeRedundancy.js:
  R0 = min-cut of load-path graph = independent vertical load paths.
  lateral_ties = load-sharing factor input (slows per-column damage, not redundancy).

Rankings reference (encoded in material constants):
  freeze_thaw  : roman_pozzolan best — porosity 10.5%, legendary FT durability
  coastal_salt : roman_pozzolan best — C-A-S-H self-heals in seawater
  wet_clay     : dry_stone longest   — free drainage + settlement tolerance
  seismic      : pozzolan 0%         — rigid → brittle fracture
  stable       : dry_stone ~91%      — redundancy dominates benign conditions
"""

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class MaterialProps:
    name:          str
    porosity:      float   # [0,1]  — governs FT + moisture penetration
    rigidity:      float   # [0,1]  — governs seismic brittle-fracture risk
    drainage:      float   # [0,1]  — governs wet-clay settlement tolerance
    has_rebar:     bool    # True → chloride depassivation multiplier active
    columns:       int     # R0: independent load paths (min-cut; lateral ties excluded)
    lateral_ties:  int     # tie count: slows per-column damage, does NOT add R0
    bond_strength: float   # [0,1]  — mortar/joint cohesion (0 = friction-only)
    self_healing:  float   # [0,1]  — pozzolanic / re-carbonation repair capacity


_CATALOGUE: dict[str, MaterialProps] = {

    # ── opus caementicium: volcanic-ash / lime concrete ──────────────────────
    # Portus Cosanus seawall still standing 2000yr; Caesarea Maritima breakwater.
    # Porosity 10–11% measured at Baianus Sinus (Jackson et al. 2017).
    # Zero rebar → no chloride pathway; tobermorite self-heals hairline cracks.
    # Extreme rigidity (E≈20–25 GPa, no ductility) → catastrophic in seismic.
    "roman_pozzolan": MaterialProps(
        name="roman_pozzolan",
        porosity=0.105,
        rigidity=0.88,
        drainage=0.12,
        has_rebar=False,
        columns=3,
        lateral_ties=2,
        bond_strength=0.92,
        self_healing=0.70,
    ),

    # ── mortarless dry-stone masonry ─────────────────────────────────────────
    # Open joints drain freely → no ice-lens accumulation → good FT tolerance.
    # Friction-only joints act as energy-dissipating fuses → seismic resilient.
    # High R0 (redundant load paths through many stones) → stable-condition king.
    # Wet clay: drainage near-perfect → foundation stays stable for centuries.
    "dry_stone": MaterialProps(
        name="dry_stone",
        porosity=0.38,
        rigidity=0.22,       # flexible friction joints — seismic ductile
        drainage=0.95,
        has_rebar=False,
        columns=4,           # many redundant stone paths
        lateral_ties=6,      # interlocking header courses
        bond_strength=0.18,  # friction only; no mortar to leach
        self_healing=0.00,
    ),

    # ── modern reinforced concrete ───────────────────────────────────────────
    # Rebar provides ductility vs. seismic but creates the chloride pathway
    # that kills coastal/wet structures (depassivation → expansive corrosion).
    "reinforced_concrete": MaterialProps(
        name="reinforced_concrete",
        porosity=0.14,
        rigidity=0.82,       # stirrups add some ductility vs. plain concrete
        drainage=0.06,
        has_rebar=True,
        columns=2,
        lateral_ties=4,
        bond_strength=0.84,
        self_healing=0.08,
    ),

    # ── traditional lime-mortar masonry ──────────────────────────────────────
    # Moderate flexibility (re-carbonation softens joints slightly).
    # Mortar leaches in sustained wet → wet-clay and coastal weakness.
    # Re-carbonation provides modest self-repair at exposed faces.
    "lime_mortar": MaterialProps(
        name="lime_mortar",
        porosity=0.24,
        rigidity=0.40,       # just below brittle threshold → marginally seismic
        drainage=0.42,
        has_rebar=False,
        columns=3,
        lateral_ties=2,
        bond_strength=0.62,
        self_healing=0.22,
    ),

    # ── modern Portland cement, unreinforced ─────────────────────────────────
    # Higher w/c ratio than pozzolan → more porosity → weaker FT.
    # No rebar avoids salt corrosion path but high rigidity → seismic brittle.
    "portland_unreinforced": MaterialProps(
        name="portland_unreinforced",
        porosity=0.19,
        rigidity=0.86,
        drainage=0.09,
        has_rebar=False,
        columns=2,
        lateral_ties=2,
        bond_strength=0.78,
        self_healing=0.04,
    ),
}

ARCHETYPES: list[str] = list(_CATALOGUE.keys())

# Full registry: callers can iterate REGISTRY.keys() to enumerate archetypes.
REGISTRY: dict = _CATALOGUE

# ---------------------------------------------------------------------------
# Design-philosophy table — consumed by renewal.py
# ---------------------------------------------------------------------------
# intent           "permanent" | "renewal"
# design_life_yr   intended lifespan at original specification
# renewal_cost     [0,1] fractional effort to fully rebuild (1 = most costly)
# return_to_substrate [0,1] fraction of materials that return to natural cycle
# ---------------------------------------------------------------------------

_PHILOSOPHY: dict[str, dict] = {
    # Opus caementicium was engineered for permanence: Pantheon, Pantheon dome,
    # Caesarea breakwater — all designed once, maintained minimally for millennia.
    # Demolition is essentially impossible without explosives; volcanic ash matrix
    # locks up permanently.
    "roman_pozzolan": {
        "intent":               "permanent",
        "design_life_yr":       2000,
        "renewal_cost":         0.95,   # most expensive to source volcanic pozzolan + mass labour
        "return_to_substrate":  0.05,   # tobermorite matrix inert; near-zero return
    },
    # Dry-stone traditions (Inca, Celtic field walls, Scottish dykes) are explicitly
    # renewal-oriented: walls are re-stacked every few generations, stones returned
    # to the field. No binding material; full substrate return.
    "dry_stone": {
        "intent":               "renewal",
        "design_life_yr":       100,    # planned cadence: re-stack every ~100yr
        "renewal_cost":         0.20,   # labour only, no binder; cheapest rebuild
        "return_to_substrate":  0.95,   # stones back to landscape
    },
    # Modern RC is nominal-permanent (100yr design life) but in practice renewal
    # is costly: demolition + rebar separation + concrete crushing. Rebar can be
    # recycled (~40–60%) but concrete aggregate mostly landfilled.
    "reinforced_concrete": {
        "intent":               "permanent",
        "design_life_yr":       100,
        "renewal_cost":         0.90,
        "return_to_substrate":  0.10,
    },
    # Lime mortar's re-carbonation makes masonry separable: bricks/stones pry free,
    # lime dust dissolves. Many historic traditions explicitly planned phased repair.
    "lime_mortar": {
        "intent":               "renewal",
        "design_life_yr":       200,
        "renewal_cost":         0.40,   # moderate; skilled mortaring but reusable units
        "return_to_substrate":  0.70,   # masonry units fully reusable; lime re-absorbs
    },
    # Plain Portland: cheaper to build than RC but equally difficult to dispose of.
    # No rebar to reclaim; rubble is inert fill at best.
    "portland_unreinforced": {
        "intent":               "permanent",
        "design_life_yr":       75,
        "renewal_cost":         0.80,
        "return_to_substrate":  0.05,
    },
}


def philosophy(archetype_key: str) -> dict:
    """Return the design-philosophy dict for an archetype (for renewal.py)."""
    if archetype_key not in _PHILOSOPHY:
        raise ValueError(f"No philosophy entry for '{archetype_key}'")
    return _PHILOSOPHY[archetype_key]


class ArchetypeInstance:
    """
    Internal record: MaterialProps + environment + quality factor.
    Used by degradation.py for graph-based simulation and load-sharing math.
    Distinct from structure.Structure (which failure_modes.py consumes).
    """
    __slots__ = ("name", "props", "env", "initial_redundancy", "quality_factor")

    def __init__(self, name: str, props: MaterialProps, env, quality_factor: float = 1.0):
        self.name               = name
        self.props              = props
        self.env                = env
        self.initial_redundancy = props.columns   # R0 = min-cut = column count
        self.quality_factor     = quality_factor

    def __repr__(self) -> str:
        return f"ArchetypeInstance({self.name}, R0={self.initial_redundancy}, q={self.quality_factor:.2f})"


def load_sharing_factor(props: MaterialProps) -> float:
    """
    Mirrors archetypeRedundancy.js computeLoadSharingFactor.
    Lateral ties slow per-column damage; they do NOT add to R0.
    """
    n, t = props.columns, props.lateral_ties
    if n <= 1 or t == 0:
        return 0.0
    max_ties = (n - 1) * 3        # 3 layers assumed
    ratio    = min(t / max_ties, 1.0)
    return 1.0 - math.exp(-3.0 * ratio)


def make(archetype: str, env, quality_factor: float = 1.0):
    """
    Return a structure.Structure for the given archetype placed in env.
    quality_factor is forwarded to failure_modes via structure.Structure's
    environment field (simulate.py wraps env before passing here).
    """
    import copy
    from structure import make_structure
    if archetype not in _CATALOGUE:
        raise ValueError(f"Unknown archetype '{archetype}'. Options: {ARCHETYPES}")
    # Settlement failure only meaningful in saturated clay (gw >= 0.50).
    # Below that threshold it isn't the dominant mechanism; zero it out so
    # foundation_settlement doesn't swamp all other modes in dry/FT/seismic
    # regimes where groundwater stays low.
    if env.groundwater_level < 0.50:
        env = copy.copy(env)
        env.settlement_rate = 0.0
    s = make_structure(archetype, env)
    s._quality_factor = quality_factor
    return s


def make_instance(archetype: str, env, quality_factor: float = 1.0) -> ArchetypeInstance:
    """Return an ArchetypeInstance (MaterialProps-based) for graph/degradation use."""
    if archetype not in _CATALOGUE:
        raise ValueError(f"Unknown archetype '{archetype}'. Options: {ARCHETYPES}")
    return ArchetypeInstance(archetype, _CATALOGUE[archetype], env, quality_factor)
