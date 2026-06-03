"""
structure.py  --  CC0

Data model consumed by failure_modes.py.

Material, Geometry, and Loads parameters are archetype-specific constants.
Environment is drawn per-simulation run from simulate.draw_env().

Capacity check: compression_crushing requires comp_strength * thickness > dead+live.
  For earthen/biomass renewal archetypes, loads are lower (light single-story shelter)
  and thickness encodes the effective structural section depth, not just wall skin.

Parameter encoding notes:
  thickness_m  — structural section depth; also frost-budget proxy for masonry.
                 For earthen/biomass materials: effective bearing section (may be
                 much larger than a masonry joint — e.g. sod=1.5m wall, cob=1.0m).
  span_m       — angular-distortion tolerance for foundation_settlement:
                 allow = span_m / 500 (metres differential before cracking).
                 For dry_stone this is large because individual stones accommodate
                 movement without propagating a through-crack.
  tensile_strength — for dry_stone encodes effective friction/interlock shear
                 resistance under gravity preload, not block tension.
  seismic_factor — design base-shear coefficient (archetype-specific).
                 Rigid structures amplify ground motion; rocking structures
                 (dry_stone) decouple from it, so seismic_factor ≈ 0.
  thermal_sensitivity — 0 for permanent materials; > 0 gates thermal_melt mode.
                 1/thermal_sensitivity ≈ baseline seasonal life in years.
                 Ice = 2.0 (~0.5yr), snow = 4.0 (~0.25yr).
"""

from dataclasses import dataclass


@dataclass
class Material:
    compressive_strength: float   # normalised (pure-Al ref = 1.0; granite ≈ 10)
    tensile_strength:     float   # joint/mortar tensile or friction-shear resistance
    creep_rate:           float   # strain yr⁻¹
    thermal_sensitivity:  float = 0.0  # 0 = permanent; >0 enables thermal_melt mode


@dataclass
class Geometry:
    thickness_m:    float   # effective structural section depth; frost-budget proxy
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
# Per-archetype parameter tables  (18 archetypes)
# ---------------------------------------------------------------------------
# PERMANENT: granite  field_stone  roman_pozzolan  massive_arch
#            concrete  modern_reinforced  lumber  dry_stone
# RENEWAL  : timber_laced  treehouse  ice  snow  cob  bamboo
#            bamboo_and_clay  willow_and_clay  sod  straw
#
# Invariant: comp_strength * thickness > dead_load + live_load
#   (util < 1.0 so compression_crushing doesn't fire at year 0)
# ---------------------------------------------------------------------------

_MATERIALS = {
    # ── PERMANENT ────────────────────────────────────────────────────────────

    # Unjointed granite ashlar. Near-zero porosity → FT immune; no mortar →
    # no chloride path; dry joints → full substrate return possible.
    "granite": Material(
        compressive_strength = 10.0,
        tensile_strength     = 1.5,    # dry-joint friction only
        creep_rate           = 1.0e-9,
    ),
    # Rough-coursed field stone; open joints drain well; moderate capacity.
    "field_stone": Material(
        compressive_strength = 6.0,
        tensile_strength     = 2.0,    # rough-face friction interlock
        creep_rate           = 5.0e-8,
    ),
    # Massive opus caementicium (C-A-S-H matrix, volcanic tuff aggregate).
    # creep_rate calibrated so creep_time ≈ 556yr → ~73% stable survival.
    "roman_pozzolan": Material(
        compressive_strength = 5.0,
        tensile_strength     = 0.8,    # pozzolan mortar joint — brittle in tension
        creep_rate           = 9.0e-6,
    ),
    # Large unreinforced arch: thick compression ring; no rebar; high rigidity.
    "massive_arch": Material(
        compressive_strength = 4.0,
        tensile_strength     = 0.5,    # arch-thrust dominated; minimal tension
        creep_rate           = 2.0e-5,
    ),
    # Plain Portland cement, unreinforced; smaller sections than massive_arch.
    "concrete": Material(
        compressive_strength = 3.5,
        tensile_strength     = 0.6,
        creep_rate           = 1.5e-5,
    ),
    # Modern Portland concrete with mild-steel rebar (cover ≈ 0.3m).
    "modern_reinforced": Material(
        compressive_strength = 4.0,
        tensile_strength     = 2.5,
        creep_rate           = 1.0e-5,
    ),
    # Dimensional lumber. Strong in compression parallel-to-grain (~30MPa → 3.0 units).
    # High water sensitivity; rot + moisture creep dominant failure paths.
    "lumber": Material(
        compressive_strength = 3.0,
        tensile_strength     = 2.5,
        creep_rate           = 3.0e-5,
    ),
    # Dry-laid granite/limestone coursing. Friction provides shear resistance.
    # thickness=0.9m → FT budget gives ~91% stable survival.
    "dry_stone": Material(
        compressive_strength = 8.0,
        tensile_strength     = 3.2,    # friction interlock under gravity preload
        creep_rate           = 2.0e-7,
    ),

    # ── RENEWAL ──────────────────────────────────────────────────────────────

    # Byzantine masonry with horizontal timber tie-beams.
    "timber_laced": Material(
        compressive_strength = 2.5,
        tensile_strength     = 1.5,
        creep_rate           = 1.2e-5,
    ),
    # Round-wood elevated structure. Low dead load; flexible.
    "treehouse": Material(
        compressive_strength = 0.8,
        tensile_strength     = 3.0,
        creep_rate           = 4.0e-5,
    ),
    # Packed ice (igloo / quinzhee). Dome arch carries self-weight efficiently.
    # thermal_sensitivity gates seasonal melt failure mode.
    "ice": Material(
        compressive_strength = 2.0,
        tensile_strength     = 0.5,
        creep_rate           = 1.0e-2,   # ice flows under sustained load
        thermal_sensitivity  = 2.0,      # base life ≈ 0.5yr
    ),
    # Compacted snow. Lower strength than ice; melts faster.
    # creep_rate reduced: snow compacts but doesn't flow structurally at short timescales.
    "snow": Material(
        compressive_strength = 0.8,
        tensile_strength     = 0.2,
        creep_rate           = 1.0e-3,   # compaction, not plastic flow
        thermal_sensitivity  = 4.0,      # base life ≈ 0.25yr
    ),
    # Earth + straw + water monolith. Straw fibres provide tensile reinforcement.
    "cob": Material(
        compressive_strength = 0.5,
        tensile_strength     = 1.0,
        creep_rate           = 5.0e-5,
    ),
    # Bamboo pole frame. High tensile/compressive strength (~25–40MPa → 3.0 units
    # parallel grain), but very thin section per pole.
    "bamboo": Material(
        compressive_strength = 2.0,
        tensile_strength     = 4.5,
        creep_rate           = 2.0e-5,
    ),
    # Bamboo frame with rammed clay infill.
    "bamboo_and_clay": Material(
        compressive_strength = 1.5,
        tensile_strength     = 3.5,
        creep_rate           = 3.0e-5,
    ),
    # Wattle-and-daub: woven willow branches plastered with clay.
    "willow_and_clay": Material(
        compressive_strength = 0.8,
        tensile_strength     = 2.0,
        creep_rate           = 4.0e-5,
    ),
    # Sod / turf blocks. Root network is the tensile element.
    # Norse longhouse walls were 1.5–2m thick; thickness reflects effective section.
    "sod": Material(
        compressive_strength = 0.3,
        tensile_strength     = 0.5,
        creep_rate           = 8.0e-5,
    ),
    # Straw bale with lime plaster shell. Very high insulation; rot-prone when wet.
    "straw": Material(
        compressive_strength = 0.2,
        tensile_strength     = 0.8,
        creep_rate           = 1.0e-4,
    ),
}

_GEOMETRIES = {
    # ── PERMANENT ────────────────────────────────────────────────────────────
    # thickness=1.0m: balanced so granite wins stable but loses coastal (haloclasty
    # from salt-crystal growth in micro-pores reduces effective FT budget vs pozzolan).
    "granite": Geometry(
        thickness_m    = 1.0,
        block_height_m = 0.80,
        span_m         = 30.0,
    ),
    "field_stone": Geometry(
        thickness_m    = 0.7,
        block_height_m = 0.35,
        span_m         = 15.0,
    ),
    # Large thickness encodes pozzolan's low porosity (10.5%) → large frost budget.
    "roman_pozzolan": Geometry(
        thickness_m    = 6.0,
        block_height_m = 0.30,
        span_m         = 20.0,
    ),
    "massive_arch": Geometry(
        thickness_m    = 1.2,
        block_height_m = 0.20,
        span_m         = 25.0,
    ),
    "concrete": Geometry(
        thickness_m    = 0.5,
        block_height_m = 0.15,
        span_m         = 10.0,
    ),
    # thickness=0.3m ≈ rebar cover depth driving water/salt intrusion budget.
    "modern_reinforced": Geometry(
        thickness_m    = 0.3,
        block_height_m = 0.20,
        span_m         = 12.0,
    ),
    # thickness=0.20m: effective bearing section for stud frame (not stud depth).
    "lumber": Geometry(
        thickness_m    = 0.20,
        block_height_m = 2.4,
        span_m         = 6.0,
    ),
    # Open-jointed stones; each stone accommodates movement independently.
    "dry_stone": Geometry(
        thickness_m    = 0.9,
        block_height_m = 0.50,
        span_m         = 650.0,
    ),

    # ── RENEWAL ──────────────────────────────────────────────────────────────
    "timber_laced": Geometry(
        thickness_m    = 0.5,
        block_height_m = 0.50,
        span_m         = 8.0,
    ),
    # thickness=0.30m: effective round-wood bearing section depth.
    "treehouse": Geometry(
        thickness_m    = 0.30,
        block_height_m = 3.0,
        span_m         = 5.0,
    ),
    "ice": Geometry(
        thickness_m    = 0.3,
        block_height_m = 0.20,
        span_m         = 3.0,
    ),
    "snow": Geometry(
        thickness_m    = 0.5,
        block_height_m = 0.30,
        span_m         = 2.0,
    ),
    # thickness=1.0m: typical cob wall section (0.4–0.6m min, 1m common).
    "cob": Geometry(
        thickness_m    = 1.0,
        block_height_m = 0.10,
        span_m         = 4.0,
    ),
    # thickness=0.20m: aggregate effective section across bamboo pole spacing.
    "bamboo": Geometry(
        thickness_m    = 0.20,
        block_height_m = 3.0,
        span_m         = 8.0,
    ),
    # thickness=0.30m: bamboo + clay composite section.
    "bamboo_and_clay": Geometry(
        thickness_m    = 0.30,
        block_height_m = 1.5,
        span_m         = 6.0,
    ),
    # thickness=0.40m: wattle-and-daub wall typically 0.20–0.40m.
    "willow_and_clay": Geometry(
        thickness_m    = 0.40,
        block_height_m = 1.0,
        span_m         = 4.0,
    ),
    # thickness=1.5m: Norse longhouse sod walls were 1.5–2m thick.
    "sod": Geometry(
        thickness_m    = 1.5,
        block_height_m = 0.20,
        span_m         = 3.0,
    ),
    # thickness=1.0m: straw bale (2-string bale ~0.45m; 3-string ~0.60m; plastered ~1m).
    "straw": Geometry(
        thickness_m    = 1.0,
        block_height_m = 0.50,
        span_m         = 5.0,
    ),
}

_LOADS = {
    # ── PERMANENT ────────────────────────────────────────────────────────────
    "granite":           Loads(dead_load=0.60, live_load=0.20, seismic_factor=0.12, wind_factor=0.08),
    "field_stone":       Loads(dead_load=0.50, live_load=0.20, seismic_factor=0.05, wind_factor=0.12),
    # Rigid frames amplify seismic; massive walls attract large dead load.
    "roman_pozzolan":    Loads(dead_load=0.50, live_load=0.20, seismic_factor=0.10, wind_factor=0.10),
    "massive_arch":      Loads(dead_load=0.60, live_load=0.20, seismic_factor=0.08, wind_factor=0.08),
    "concrete":          Loads(dead_load=0.50, live_load=0.20, seismic_factor=0.08, wind_factor=0.10),
    "modern_reinforced": Loads(dead_load=0.50, live_load=0.20, seismic_factor=0.05, wind_factor=0.10),
    # Lumber frame: lighter than masonry; more live load proportion; seismic ductile.
    "lumber":            Loads(dead_load=0.25, live_load=0.20, seismic_factor=0.03, wind_factor=0.15),
    # Dry stone rocks/slides → base-isolates → nearly zero seismic base shear.
    "dry_stone":         Loads(dead_load=0.50, live_load=0.20, seismic_factor=0.00, wind_factor=0.15),

    # ── RENEWAL ──────────────────────────────────────────────────────────────
    "timber_laced":      Loads(dead_load=0.50, live_load=0.20, seismic_factor=0.00, wind_factor=0.12),
    # Treehouse: very light shelter; single occupant loads only.
    "treehouse":         Loads(dead_load=0.10, live_load=0.10, seismic_factor=0.02, wind_factor=0.25),
    # Ice/snow: igloo/shelter; low occupant load only.
    "ice":               Loads(dead_load=0.05, live_load=0.03, seismic_factor=0.00, wind_factor=0.05),
    "snow":              Loads(dead_load=0.03, live_load=0.02, seismic_factor=0.00, wind_factor=0.08),
    # Earthen structures: single-story; light occupant loads.
    "cob":               Loads(dead_load=0.30, live_load=0.10, seismic_factor=0.00, wind_factor=0.08),
    "bamboo":            Loads(dead_load=0.15, live_load=0.20, seismic_factor=0.01, wind_factor=0.20),
    "bamboo_and_clay":   Loads(dead_load=0.20, live_load=0.15, seismic_factor=0.01, wind_factor=0.15),
    "willow_and_clay":   Loads(dead_load=0.20, live_load=0.10, seismic_factor=0.01, wind_factor=0.15),
    "sod":               Loads(dead_load=0.25, live_load=0.05, seismic_factor=0.00, wind_factor=0.05),
    "straw":             Loads(dead_load=0.10, live_load=0.05, seismic_factor=0.00, wind_factor=0.10),
}


def make_structure(archetype: str, env) -> "Structure":
    """Return a Structure for the given archetype placed in env."""
    return Structure(
        material    = _MATERIALS[archetype],
        geometry    = _GEOMETRIES[archetype],
        loads       = _LOADS[archetype],
        environment = env,
    )
