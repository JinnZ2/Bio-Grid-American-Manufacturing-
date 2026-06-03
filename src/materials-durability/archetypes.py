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


class Structure:
    """
    A material archetype instantiated in a specific environment.
    Produced by make(); consumed by failure_modes and degradation.

    quality_factor: lognormal workmanship/material variability drawn by the
    caller (simulate.py). Scales all failure times multiplicatively.
    """
    __slots__ = ("name", "props", "env", "initial_redundancy", "quality_factor")

    def __init__(self, name: str, props: MaterialProps, env, quality_factor: float = 1.0):
        self.name               = name
        self.props              = props
        self.env                = env
        self.initial_redundancy = props.columns   # R0 = min-cut = column count
        self.quality_factor     = quality_factor

    def __repr__(self) -> str:
        return f"Structure({self.name}, R0={self.initial_redundancy}, q={self.quality_factor:.2f})"


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


def make(archetype: str, env, quality_factor: float = 1.0) -> Structure:
    """Instantiate an archetype in an environment."""
    if archetype not in _CATALOGUE:
        raise ValueError(f"Unknown archetype '{archetype}'. Options: {ARCHETYPES}")
    return Structure(archetype, _CATALOGUE[archetype], env, quality_factor)
