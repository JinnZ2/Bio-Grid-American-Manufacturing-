"""
archetypes.py  --  CC0

Unified REGISTRY for 18 structural archetypes: MaterialProps (scorecard),
philosophy (design intent + lifecycle), and graph topology key.

R0 = min-cut of load-path graph = independent vertical load paths.
lateral_ties = load-sharing factor input (slows per-column damage, not R0).

Rankings reference:
  freeze_thaw      : roman_pozzolan best — porosity 10.5%, FT durability
  coastal_salt     : roman_pozzolan best — C-A-S-H self-heals in seawater
  wet_clay         : dry_stone longest   — free drainage + settlement tolerance
  seismic          : dry_stone wins; pozzolan ~0% — rigid → brittle fracture
  temperate_stable : dry_stone ~91%      — redundancy dominates benign conditions
  renewal lens     : ice/snow/sod/bamboo — zero or near-zero substrate debt flux
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

    # ── PERMANENT intent ─────────────────────────────────────────────────────

    # Unjointed granite ashlar. Near-zero porosity → FT immune; extreme E-mod →
    # seismic brittle; no mortar → no chloride path; dry joints → free reuse.
    "granite": MaterialProps(
        name="granite",
        porosity=0.01,
        rigidity=0.95,
        drainage=0.25,
        has_rebar=False,
        columns=2,
        lateral_ties=1,
        bond_strength=0.90,
        self_healing=0.02,
    ),

    # Rough-coursed field stone; open joints drain well; moderate R0.
    "field_stone": MaterialProps(
        name="field_stone",
        porosity=0.08,
        rigidity=0.60,
        drainage=0.60,
        has_rebar=False,
        columns=3,
        lateral_ties=3,
        bond_strength=0.45,
        self_healing=0.05,
    ),

    # Opus caementicium: volcanic-ash / lime concrete.
    # Portus Cosanus seawall still standing 2000yr; Caesarea Maritima breakwater.
    # Porosity 10–11% measured at Baianus Sinus (Jackson et al. 2017).
    # Zero rebar → no chloride pathway; tobermorite self-heals hairline cracks.
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

    # Large unreinforced arch: stone or plain concrete ring in compression.
    # Thick section; high rigidity; no rebar chloride path.
    "massive_arch": MaterialProps(
        name="massive_arch",
        porosity=0.20,
        rigidity=0.90,
        drainage=0.08,
        has_rebar=False,
        columns=3,
        lateral_ties=1,
        bond_strength=0.72,
        self_healing=0.03,
    ),

    # Plain Portland cement, unreinforced; smaller sections than massive_arch.
    # Higher w/c ratio → more porosity → weaker FT; no rebar avoids salt path.
    "concrete": MaterialProps(
        name="concrete",
        porosity=0.19,
        rigidity=0.86,
        drainage=0.09,
        has_rebar=False,
        columns=2,
        lateral_ties=2,
        bond_strength=0.78,
        self_healing=0.04,
    ),

    # Modern Portland concrete with mild-steel rebar.
    # Rebar provides ductility vs. seismic but creates the chloride pathway.
    "modern_reinforced": MaterialProps(
        name="modern_reinforced",
        porosity=0.14,
        rigidity=0.82,
        drainage=0.06,
        has_rebar=True,
        columns=2,
        lateral_ties=4,
        bond_strength=0.84,
        self_healing=0.08,
    ),

    # Dimensional lumber (stud / post-and-beam). Many parallel studs = high R0.
    # Flexible frame; good seismic ductility; rot + moisture are main failure paths.
    "lumber": MaterialProps(
        name="lumber",
        porosity=0.30,
        rigidity=0.35,
        drainage=0.40,
        has_rebar=False,
        columns=5,
        lateral_ties=8,
        bond_strength=0.65,
        self_healing=0.00,
    ),

    # Mortarless dry-stone masonry.
    # Open joints drain freely → no ice-lens accumulation → good FT tolerance.
    # Friction-only joints act as energy-dissipating fuses → seismic resilient.
    # High R0 (redundant load paths through many stones) → stable-condition king.
    "dry_stone": MaterialProps(
        name="dry_stone",
        porosity=0.38,
        rigidity=0.22,
        drainage=0.95,
        has_rebar=False,
        columns=4,
        lateral_ties=6,
        bond_strength=0.18,
        self_healing=0.00,
    ),

    # ── RENEWAL intent ───────────────────────────────────────────────────────

    # Byzantine masonry with horizontal timber tie-beams.
    # Flexible joints; timber rots → cadenced rebuild every ~200yr.
    "timber_laced": MaterialProps(
        name="timber_laced",
        porosity=0.24,
        rigidity=0.40,
        drainage=0.42,
        has_rebar=False,
        columns=3,
        lateral_ties=2,
        bond_strength=0.62,
        self_healing=0.22,
    ),

    # Round-wood elevated structure (tree platform / hillside shelter).
    # Very flexible; high wind exposure; short planned life.
    "treehouse": MaterialProps(
        name="treehouse",
        porosity=0.35,
        rigidity=0.20,
        drainage=0.80,
        has_rebar=False,
        columns=4,
        lateral_ties=4,
        bond_strength=0.40,
        self_healing=0.00,
    ),

    # Packed ice (igloo / quinzhee). Refreezing heals cracks; melts by spring.
    "ice": MaterialProps(
        name="ice",
        porosity=0.05,
        rigidity=0.50,
        drainage=0.05,
        has_rebar=False,
        columns=3,
        lateral_ties=3,
        bond_strength=0.30,
        self_healing=0.60,
    ),

    # Compacted snow. Very low strength; melts faster than ice.
    "snow": MaterialProps(
        name="snow",
        porosity=0.80,
        rigidity=0.10,
        drainage=0.80,
        has_rebar=False,
        columns=2,
        lateral_ties=2,
        bond_strength=0.10,
        self_healing=0.80,
    ),

    # Earth + straw + water monolith. Fibres provide tensile reinforcement.
    # Clay self-heals surface cracks; highly water-sensitive.
    "cob": MaterialProps(
        name="cob",
        porosity=0.40,
        rigidity=0.25,
        drainage=0.35,
        has_rebar=False,
        columns=5,
        lateral_ties=3,
        bond_strength=0.55,
        self_healing=0.35,
    ),

    # Bamboo pole frame. Very high tensile / compressive strength-to-weight.
    # Rapid re-growth (~3yr); seismic ductile; vulnerable to rot without treatment.
    "bamboo": MaterialProps(
        name="bamboo",
        porosity=0.45,
        rigidity=0.15,
        drainage=0.85,
        has_rebar=False,
        columns=8,
        lateral_ties=10,
        bond_strength=0.35,
        self_healing=0.00,
    ),

    # Bamboo frame infilled with rammed clay; better thermal mass than bare bamboo.
    "bamboo_and_clay": MaterialProps(
        name="bamboo_and_clay",
        porosity=0.38,
        rigidity=0.18,
        drainage=0.65,
        has_rebar=False,
        columns=6,
        lateral_ties=8,
        bond_strength=0.45,
        self_healing=0.25,
    ),

    # Wattle-and-daub: woven willow branches plastered with clay.
    "willow_and_clay": MaterialProps(
        name="willow_and_clay",
        porosity=0.42,
        rigidity=0.15,
        drainage=0.55,
        has_rebar=False,
        columns=6,
        lateral_ties=6,
        bond_strength=0.40,
        self_healing=0.30,
    ),

    # Sod / turf block walls and roof. Root network is the tensile element.
    # return_to_substrate = 1.0 — literally returns to earth.
    "sod": MaterialProps(
        name="sod",
        porosity=0.55,
        rigidity=0.10,
        drainage=0.45,
        has_rebar=False,
        columns=4,
        lateral_ties=3,
        bond_strength=0.20,
        self_healing=0.50,
    ),

    # Straw bale with lime plaster shell. High insulation; rot-prone when wet.
    "straw": MaterialProps(
        name="straw",
        porosity=0.70,
        rigidity=0.08,
        drainage=0.60,
        has_rebar=False,
        columns=3,
        lateral_ties=2,
        bond_strength=0.25,
        self_healing=0.10,
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
    # Quarried granite: one build, ~3000yr life, enormous extraction cost.
    # Stones can be re-used but quarrying is a permanent extraction event.
    "granite": {
        "intent":               "permanent",
        "design_life_yr":       3000,
        "renewal_cost":         0.98,
        "return_to_substrate":  0.20,
    },
    # Field stone gathered from the surface: lower extraction than quarried granite;
    # stones fully reusable; some lime mortar lost but mostly substrate-returnable.
    "field_stone": {
        "intent":               "permanent",
        "design_life_yr":       500,
        "renewal_cost":         0.30,
        "return_to_substrate":  0.75,
    },
    # Roman pozzolan: designed for permanence — Pantheon, Caesarea — one build
    # intended for millennia. Demolition essentially impossible; matrix inert.
    "roman_pozzolan": {
        "intent":               "permanent",
        "design_life_yr":       2000,
        "renewal_cost":         0.95,
        "return_to_substrate":  0.05,
    },
    # Stone/plain-concrete arch: massive, permanent, no rebar to reclaim.
    "massive_arch": {
        "intent":               "permanent",
        "design_life_yr":       500,
        "renewal_cost":         0.85,
        "return_to_substrate":  0.05,
    },
    # Plain Portland: cheaper to build than RC but equally non-returnable.
    "concrete": {
        "intent":               "permanent",
        "design_life_yr":       75,
        "renewal_cost":         0.80,
        "return_to_substrate":  0.05,
    },
    # RC: rebar recyclable (~50%) but concrete aggregate mostly landfilled.
    "modern_reinforced": {
        "intent":               "permanent",
        "design_life_yr":       100,
        "renewal_cost":         0.90,
        "return_to_substrate":  0.10,
    },
    # Dimensional lumber: wood decomposes or can be re-milled; moderate return.
    "lumber": {
        "intent":               "permanent",
        "design_life_yr":       100,
        "renewal_cost":         0.50,
        "return_to_substrate":  0.60,
    },
    # Dry stone: traditionally maintained by re-stacking; zero binder loss.
    "dry_stone": {
        "intent":               "renewal",
        "design_life_yr":       100,
        "renewal_cost":         0.20,
        "return_to_substrate":  0.95,
    },
    # Timber-laced masonry: lime mortar re-carbonates; stones separable; timber rots.
    "timber_laced": {
        "intent":               "renewal",
        "design_life_yr":       200,
        "renewal_cost":         0.40,
        "return_to_substrate":  0.70,
    },
    # Treehouse: entirely wood; designed for short life + abandonment.
    "treehouse": {
        "intent":               "renewal",
        "design_life_yr":       20,
        "renewal_cost":         0.15,
        "return_to_substrate":  0.80,
    },
    # Ice: designed for one winter season; melts clean; zero net extraction.
    "ice": {
        "intent":               "renewal",
        "design_life_yr":       1,      # 1yr cadence (winter → spring melt → winter)
        "renewal_cost":         0.02,
        "return_to_substrate":  1.00,
    },
    # Snow: even shorter — a few months; returns fully to the water cycle.
    "snow": {
        "intent":               "renewal",
        "design_life_yr":       1,
        "renewal_cost":         0.01,
        "return_to_substrate":  1.00,
    },
    # Cob: earth + straw; bulldozed cob dissolves back into soil within decades.
    "cob": {
        "intent":               "renewal",
        "design_life_yr":       50,
        "renewal_cost":         0.10,
        "return_to_substrate":  0.95,
    },
    # Bamboo: rapid re-growth (~3yr cycle); untreated bamboo returns to soil.
    "bamboo": {
        "intent":               "renewal",
        "design_life_yr":       30,
        "renewal_cost":         0.10,
        "return_to_substrate":  0.95,
    },
    # Bamboo + clay: clay returns to soil; bamboo composts.
    "bamboo_and_clay": {
        "intent":               "renewal",
        "design_life_yr":       40,
        "renewal_cost":         0.12,
        "return_to_substrate":  0.90,
    },
    # Wattle and daub: willow re-sprouts from cut stakes; clay returns.
    "willow_and_clay": {
        "intent":               "renewal",
        "design_life_yr":       30,
        "renewal_cost":         0.08,
        "return_to_substrate":  0.95,
    },
    # Sod: literally earth; returns to earth.
    "sod": {
        "intent":               "renewal",
        "design_life_yr":       25,
        "renewal_cost":         0.05,
        "return_to_substrate":  1.00,
    },
    # Straw bale: straw composts in a few years; lime plaster re-absorbs CO2.
    "straw": {
        "intent":               "renewal",
        "design_life_yr":       20,
        "renewal_cost":         0.06,
        "return_to_substrate":  0.98,
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
        self.initial_redundancy = props.columns
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
    max_ties = (n - 1) * 3
    ratio    = min(t / max_ties, 1.0)
    return 1.0 - math.exp(-3.0 * ratio)


def make(archetype: str, env, quality_factor: float = 1.0):
    """
    Return a structure.Structure for the given archetype placed in env.
    quality_factor scales all finite failure times multiplicatively.
    """
    import copy
    from structure import make_structure
    if archetype not in _CATALOGUE:
        raise ValueError(f"Unknown archetype '{archetype}'. Options: {ARCHETYPES}")
    props = _CATALOGUE[archetype]
    if env.groundwater_level < 0.50:
        # Settlement only relevant in saturated clay.
        env = copy.copy(env)
        env.settlement_rate = 0.0
    else:
        # High-drainage materials shed pore water → reduce effective settlement rate.
        # drainage=0 keeps full rate; drainage=1.0 reduces by 80% (free-draining).
        # Physical basis: dry_stone open joints drain pore pressure; cob/straw
        # retain water → full rate applies.
        reduced = env.settlement_rate * (1.0 - 0.8 * props.drainage)
        env = copy.copy(env)
        env.settlement_rate = max(reduced, 0.0)
    s = make_structure(archetype, env)
    s._quality_factor = quality_factor
    return s


def make_instance(archetype: str, env, quality_factor: float = 1.0) -> ArchetypeInstance:
    """Return an ArchetypeInstance (MaterialProps-based) for graph/degradation use."""
    if archetype not in _CATALOGUE:
        raise ValueError(f"Unknown archetype '{archetype}'. Options: {ARCHETYPES}")
    return ArchetypeInstance(archetype, _CATALOGUE[archetype], env, quality_factor)
