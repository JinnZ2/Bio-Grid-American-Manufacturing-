"""
structure.py  --  CC0

Data model consumed by failure_modes.py.

Material, Geometry, and Loads parameters are archetype-specific constants.
Environment is drawn per-simulation run from simulate.draw_env().

Parameter encoding notes:
  thickness_m  — for masonry: actual wall/section thickness; also encodes
                 effective frost budget (low-porosity materials effectively
                 present more thickness to spall before failure).
  span_m       — angular-distortion tolerance for foundation_settlement:
                 allow = span_m / 500 (metres differential before cracking).
                 For dry_stone this is large because individual stones
                 accommodate movement without propagating a through-crack.
  tensile_strength — for dry_stone this encodes effective friction/interlock
                 shear resistance under gravity preload, not block tension.
  loads.seismic_factor — design base-shear coefficient (archetype-specific).
                 Rigid structures amplify ground motion; rocking structures
                 (dry_stone) decouple from it, so seismic_factor ≈ 0.
"""

from dataclasses import dataclass, field


@dataclass
class Material:
    compressive_strength: float   # normalised (pure-Al ref = 1.0; granite ≈ 8)
    tensile_strength:     float   # joint/mortar tensile or friction-shear resistance
    creep_rate:           float   # strain yr⁻¹


@dataclass
class Geometry:
    thickness_m:    float   # structural section depth; also frost-budget proxy
    block_height_m: float   # individual unit height (joint spacing)
    span_m:         float   # effective differential-settlement tolerance (see note)


@dataclass
class Loads:
    dead_load:      float   # normalised gravity demand
    live_load:      float   # normalised imposed demand
    seismic_factor: float   # design base-shear coefficient
    wind_factor:    float   # normalised wind demand


@dataclass
class Structure:
    """Archetype + environment bundle consumed by failure_modes."""
    material:    Material
    geometry:    Geometry
    loads:       Loads
    environment: object     # simulate.Environment


# ---------------------------------------------------------------------------
# Per-archetype parameter tables
# ---------------------------------------------------------------------------

_MATERIALS = {
    # Massive opus caementicium (C-A-S-H matrix, volcanic tuff aggregate).
    # Low w/c ratio ≈ modern 0.3 → very dense → high FT tolerance encoded as
    # large thickness_m.  Tensile at mortar joints (not block strength).
    # creep_rate calibrated so creep_time ≈ 556yr → ~73% stable survival.
    "roman_pozzolan": Material(
        compressive_strength = 5.0,
        tensile_strength     = 0.8,    # pozzolan mortar joint — brittle in tension
        creep_rate           = 9.0e-6,
    ),
    # Dry-laid granite/limestone coursing.  Friction provides shear resistance.
    # Blocks barely creep; stone compressive strength is high but tensile = 0 at
    # joints → encoded via large effective friction value (gravity interlock).
    # thickness=0.6m → FT budget gives ~91% stable survival; fails fast in FT regime.
    "dry_stone": Material(
        compressive_strength = 8.0,
        tensile_strength     = 3.2,    # friction interlock under gravity preload
        creep_rate           = 2.0e-7,
    ),
    # Modern Portland concrete with mild-steel rebar.
    # thickness=0.3m ≈ rebar cover depth: water_intrusion budget is thin →
    # chloride reaches rebar quickly in coastal/wet conditions.
    "reinforced_concrete": Material(
        compressive_strength = 4.0,
        tensile_strength     = 2.5,
        creep_rate           = 1.0e-5,
    ),
    # Lime-mortar ashlar / rubble.  Flexible joints.
    # tensile=1.5 encodes mortar friction + soft shear dissipation (seismic benefit).
    "lime_mortar": Material(
        compressive_strength = 2.5,
        tensile_strength     = 1.5,
        creep_rate           = 1.2e-5,
    ),
    # Unreinforced OPC concrete.
    "portland_unreinforced": Material(
        compressive_strength = 3.5,
        tensile_strength     = 0.6,
        creep_rate           = 1.5e-5,
    ),
}

_GEOMETRIES = {
    # Thick monolithic mass; large thickness_m encodes pozzolan's low porosity
    # (10.5%) → large frost budget before 30% thickness lost to spalling.
    "roman_pozzolan": Geometry(
        thickness_m    = 6.0,
        block_height_m = 0.30,
        span_m         = 20.0,   # rigid monolith; limited differential tolerance
    ),
    # Open-jointed stones; each stone accommodates movement independently so the
    # effective crack-propagation span is very large → large span_m.
    # thickness=0.9m → FT budget calibrated to ~91% stable / fast FT failure.
    "dry_stone": Geometry(
        thickness_m    = 0.9,
        block_height_m = 0.50,
        span_m         = 650.0,  # stones slide without propagating a through-crack
    ),
    # thickness=0.3m ≈ structural cover depth driving water/salt intrusion budget.
    "reinforced_concrete": Geometry(
        thickness_m    = 0.3,
        block_height_m = 0.20,
        span_m         = 12.0,
    ),
    "lime_mortar": Geometry(
        thickness_m    = 0.5,
        block_height_m = 0.50,
        span_m         = 8.0,
    ),
    "portland_unreinforced": Geometry(
        thickness_m    = 0.5,
        block_height_m = 0.15,
        span_m         = 10.0,
    ),
}

_LOADS = {
    # Rigid frames amplify seismic demand; massive pozzolan walls attract load.
    "roman_pozzolan":       Loads(dead_load=0.5, live_load=0.2, seismic_factor=0.10, wind_factor=0.10),
    # Dry_stone rocks/slides → base-isolates → nearly zero seismic base shear.
    "dry_stone":            Loads(dead_load=0.5, live_load=0.2, seismic_factor=0.00, wind_factor=0.15),
    "reinforced_concrete":  Loads(dead_load=0.5, live_load=0.2, seismic_factor=0.05, wind_factor=0.10),
    "lime_mortar":          Loads(dead_load=0.5, live_load=0.2, seismic_factor=0.00, wind_factor=0.12),
    "portland_unreinforced":Loads(dead_load=0.5, live_load=0.2, seismic_factor=0.08, wind_factor=0.10),
}


def make_structure(archetype: str, env) -> "Structure":
    """Return a Structure for the given archetype placed in env."""
    return Structure(
        material    = _MATERIALS[archetype],
        geometry    = _GEOMETRIES[archetype],
        loads       = _LOADS[archetype],
        environment = env,
    )
