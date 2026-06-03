"""
failure_modes.py  --  CC0

Analytic time-to-threshold for each degradation mechanism, given a Structure.

Each function returns years until that mode alone would collapse the structure.
The minimum across modes is the governing failure; collapse occurs first.

Physics references:
  FT spalling     : Fagerlund, Cement Concrete Res 1977; critical saturation theory
  Salt corrosion  : Tuutti, Cement Concrete Inst 1982; chloride diffusion model
  Seismic brittle : Park & Paulay, RC Structures 1975; ductility demand vs. capacity
  Settlement      : Terzaghi & Peck, Soil Mechanics 1948; drainage-controlled consolidation
  Mortar leaching : Richardson, Cement Concrete Res 2004; Ca dissolution kinetics
  Redundancy      : graph-theory R0 model (archetypeRedundancy.js) — columns + LSF
"""

import math
from typing import Dict, Tuple

INF = float("inf")

# Rigidity threshold above which brittle seismic fracture is active.
# Below this value joints dissipate energy (dry_stone rocking, lime_mortar sliding)
# rather than accumulating damage to fracture → treated as non-brittle.
_BRITTLE_RIGIDITY_THRESHOLD = 0.60


# ─── individual mode functions ────────────────────────────────────────────────

def _ft_spalling_time(s) -> float:
    """
    Freeze-thaw spalling: ice-lens expansion above critical saturation.

    Rate ∝ porosity^1.5 × annual FT cycles.
    Self-healing (pozzolanic C-A-S-H) fills pores over time → reduces rate.
    Quality factor scales time multiplicatively (better workmanship = longer life).
    """
    ft = s.env.freeze_thaw_cycles
    if ft == 0:
        return INF
    p    = s.props.porosity
    sh   = s.props.self_healing
    rate = (p ** 1.5) * (ft / 1000.0) * (1.0 - sh * 0.60) * 0.55
    return (1.0 / rate) * s.quality_factor if rate > 0 else INF


def _salt_corrosion_time(s) -> float:
    """
    Chloride / salt attack.

    Rebar multiplies damage 5× via depassivation → expansive Fe2O3 products
    that spall cover concrete (Tuutti 1982 initiation + propagation model).
    Pozzolanic self-healing binds Cl⁻ into Friedel's salt → reduces penetration.
    """
    sal = s.env.salinity
    if sal == 0:
        return INF
    p     = s.props.porosity
    rebar = 5.0 if s.props.has_rebar else 1.0
    sh    = s.props.self_healing
    rate  = sal * (p ** 0.8) * rebar * (1.0 - sh * 0.35) / 30.0
    return (1.0 / rate) * s.quality_factor if rate > 0 else INF


def _seismic_brittle_time(s) -> float:
    """
    Seismic brittle fracture.

    Rigid structures (rigidity > threshold) cannot dissipate seismic energy
    through joint slip or plastic hinging → catastrophic fracture on peak event.

    Ductile structures (dry_stone rocking, lime_mortar joint slip) are modelled
    as immune to this mode — they absorb energy without fracture.

    A minimum seismic_factor threshold filters out tectonic-quiet regions:
    below sf=0.12 the annual probability of a damaging event is negligible
    and background noise in the simulation would otherwise generate spurious
    seismic collapses in FT/stable regimes.

    Expected time = 1 / (annual P(collapse)):
      P(collapse | event) ∝ rigidity^2.2 × seismic_factor
      event rate          ≈ seismic_factor (index of mean annual return frequency)
    """
    if s.props.rigidity < _BRITTLE_RIGIDITY_THRESHOLD:
        return INF   # ductile: joints dissipate energy, no brittle failure mode

    sf = s.env.seismic_factor
    if sf < 0.12:
        return INF   # below structural-damage threshold for tectonically quiet sites
    rig   = s.props.rigidity
    p_col = (rig ** 2.2) * sf
    rate  = sf * p_col
    return (1.0 / rate) * s.quality_factor if rate > 0 else INF


def _settlement_time(s) -> float:
    """
    Differential settlement in saturated clay.

    Only activates when groundwater_level > 0.50 — genuinely saturated clay.
    Below that threshold the soil is not in consolidating plastic state and
    settlement damage is negligible (the regime data encodes this: wet_clay
    has gw_mean=0.78, freeze_thaw has gw_mean=0.35).

    Free-draining structures (dry_stone) dissipate pore pressure instantly →
    near-zero consolidation-driven settlement differential.
    """
    gw = s.env.groundwater_level
    sr = s.env.settlement_rate
    if gw < 0.50 or sr == 0:
        return INF
    drain = s.props.drainage
    rate  = (1.0 - drain) * gw * sr * 20.0
    return (1.0 / rate) * s.quality_factor if rate > 0 else INF


def _mortar_leaching_time(s) -> float:
    """
    Mortar / bond dissolution under sustained wet conditions.

    Dry_stone has bond_strength ≈ 0.18 (friction only); no mortar exists to
    leach → mode is absent below the threshold.
    Lime mortar dissolves faster than Portland in alkaline groundwater.
    """
    bs = s.props.bond_strength
    if bs < 0.25:
        return INF   # friction-only joint: no mortar to leach
    hum  = s.env.humidity_pct / 100.0
    gw   = s.env.groundwater_level
    sh   = s.props.self_healing
    rate = (1.0 - bs) * hum * gw * 0.04 * (1.0 - sh * 0.40)
    return (1.0 / rate) * s.quality_factor if rate > 0 else INF


def _carbonation_shrinkage_time(s) -> float:
    """
    Slow carbonation-driven shrinkage cracking in cementitious matrices.

    Absent in dry_stone (no cement binder to carbonate).
    Rate peaks at 50–70% RH (optimal CO2 ingress with available moisture).
    Self-healing (pozzolanic) partially counters crack propagation.

    Physical basis: CO2 + Ca(OH)2 → CaCO3 + H2O.  Carbonation front
    advances as sqrt(time); cumulative shrinkage mismatch eventually cracks
    the matrix in a statically determinate (rigid) system.  Dry_stone is
    immune because there is no continuous cement matrix.
    """
    if s.props.bond_strength < 0.25:
        return INF   # dry_stone / friction-only: no cement matrix
    hum       = s.env.humidity_pct / 100.0
    rh_factor = 4.0 * hum * (1.0 - hum)   # peaks at 50% RH, zero at 0% and 100%
    sh        = s.props.self_healing
    rate      = 0.0024 * rh_factor * (1.0 - sh * 0.40)
    return (1.0 / rate) * s.quality_factor if rate > 0 else INF


def _redundancy_exhaustion_time(s) -> float:
    """
    Slow background structural degradation moderated by graph-theory redundancy.

    Uses archetypeRedundancy.js logic:
      R0 = columns (min-cut; independent load paths)
      LSF = load-sharing factor from lateral ties (slows per-column damage)

    Higher R0 and more lateral ties → longer expected life even under diffuse
    environmental stress that no single mode dominates.

    self_healing reduces the effective degradation rate: pozzolanic C-A-S-H
    and lime re-carbonation continuously repair micro-damage, extending life.
    This is why roman pozzolan structures survive millennia in benign climates.
    """
    from archetypes import load_sharing_factor
    props = s.props
    r0    = props.columns
    lsf   = load_sharing_factor(props)

    base_rate  = 0.015
    # Self-healing repairs micro-damage but diminishing returns at high coverage
    heal_damp  = 1.0 + props.self_healing * 0.8
    effective  = base_rate / (r0 * (1.0 + lsf) * heal_damp)
    hum_factor = s.env.humidity_pct / 100.0
    rate       = effective * (0.5 + 0.5 * hum_factor)
    return (1.0 / rate) * s.quality_factor if rate > 0 else INF


# ─── registry ────────────────────────────────────────────────────────────────

_MODES = {
    "ft_spalling":            _ft_spalling_time,
    "salt_corrosion":         _salt_corrosion_time,
    "seismic_brittle":        _seismic_brittle_time,
    "settlement":             _settlement_time,
    "mortar_leaching":        _mortar_leaching_time,
    "carbonation_shrinkage":  _carbonation_shrinkage_time,
    "redundancy_exhaustion":  _redundancy_exhaustion_time,
}


# ─── public API ───────────────────────────────────────────────────────────────

def failure_times(s) -> Dict[str, float]:
    """Return {mode_name: years_to_failure} for all six modes."""
    return {name: fn(s) for name, fn in _MODES.items()}


def critical_mode(s) -> Tuple[str, float]:
    """Return (mode_name, time_yr) for the mode that fires first."""
    times = failure_times(s)
    name  = min(times, key=lambda k: times[k])
    return name, times[name]
