"""
simulate.py  --  CC0

Environment definitions, sampling, and Monte-Carlo survival surface.

REGIMES encode historical deployment contexts.
Each parameter is sampled from N(mean, std) clamped to physical bounds.

A lognormal quality_factor (σ=0.18) models workmanship and raw-material
variability — the main source of scatter within a single regime.
This is what produces ~9% failure for dry_stone in stable conditions rather
than 0%: a small fraction of sites have poor drainage, weak stone, or
substandard placement.
"""

import math
import random
from collections import Counter
from dataclasses import dataclass
from typing import Dict, Optional, Tuple

from archetypes import make, ARCHETYPES
from failure_modes import critical_mode


# ─── environment record ───────────────────────────────────────────────────────

@dataclass
class Environment:
    temperature_c:      float   # mean annual air temperature (°C)
    humidity_pct:       float   # relative humidity (%)
    groundwater_level:  float   # [0,1] fraction of year near saturation
    freeze_thaw_cycles: int     # annual FT cycles
    salinity:           float   # [0,1] chloride exposure index
    seismic_factor:     float   # [0,1] ground-motion intensity index
    settlement_rate:    float   # differential settlement (m/yr)


# ─── regime parameter tables ─────────────────────────────────────────────────
# Each entry: (mean, std).  Clamped after sampling.

_RAW: Dict[str, Dict[str, Tuple[float, float]]] = {

    # Northern climates with repeated annual freeze cycles.
    # Roman pozzolan's 10.5% porosity keeps ice-lens formation below critical
    # saturation threshold (Fagerlund) → lowest FT damage rate.
    "freeze_thaw": {
        "temperature_c":      (2.0,  5.0),
        "humidity_pct":       (75.0, 8.0),
        "groundwater_level":  (0.35, 0.12),
        "freeze_thaw_cycles": (62.0, 18.0),
        "salinity":           (0.05, 0.03),
        "seismic_factor":     (0.05, 0.03),
        "settlement_rate":    (0.0015, 0.0008),
    },

    # Marine exposure: chloride spray + high humidity.
    # Rebar materials depassivate within decades; pozzolan's tobermorite
    # (seawater-cured) self-heals and binds Cl⁻ as Friedel's salt.
    "coastal_salt": {
        "temperature_c":      (15.0, 5.0),
        "humidity_pct":       (84.0, 6.0),
        "groundwater_level":  (0.40, 0.12),
        "freeze_thaw_cycles": (8.0,  5.0),
        "salinity":           (0.35, 0.10),
        "seismic_factor":     (0.08, 0.04),
        "settlement_rate":    (0.002, 0.001),
    },

    # High-plasticity clay, elevated groundwater, differential settlement.
    # Dry_stone's open joints drain pore pressure → 272yr median life.
    # Mortared/rigid structures crack as clay heaves seasonally.
    "wet_clay": {
        "temperature_c":      (12.0, 4.0),
        "humidity_pct":       (84.0, 7.0),
        "groundwater_level":  (0.78, 0.14),
        "freeze_thaw_cycles": (12.0, 8.0),
        "salinity":           (0.04, 0.02),
        "seismic_factor":     (0.06, 0.03),
        "settlement_rate":    (0.0048, 0.0020),
    },

    # Active tectonic zone.  Rigid materials (pozzolan, Portland) fracture
    # catastrophically in the brittle-failure mode; dry_stone rocks and slides.
    "seismic": {
        "temperature_c":      (16.0, 6.0),
        "humidity_pct":       (55.0, 15.0),
        "groundwater_level":  (0.25, 0.12),
        "freeze_thaw_cycles": (5.0,  4.0),
        "salinity":           (0.06, 0.04),
        "seismic_factor":     (0.62, 0.18),
        "settlement_rate":    (0.001, 0.0005),
    },

    # Benign: low frost, low salt, low seismic, stable soils.
    # Pure redundancy contest: dry_stone's R0=4 + lateral_ties=6 wins.
    "stable": {
        "temperature_c":      (14.0, 4.0),
        "humidity_pct":       (58.0, 10.0),
        "groundwater_level":  (0.18, 0.08),
        "freeze_thaw_cycles": (5.0,  3.0),
        "salinity":           (0.02, 0.01),
        "seismic_factor":     (0.04, 0.02),
        "settlement_rate":    (0.0008, 0.0004),
    },
}

REGIMES: Dict = _RAW   # callers iterate keys


# ─── sampler ─────────────────────────────────────────────────────────────────

def draw_env(rng: random.Random, regime: str) -> Environment:
    """Sample one Environment from the regime's parameter distributions."""
    p = _RAW[regime]

    def g(key, lo=None, hi=None) -> float:
        mean, std = p[key]
        v = rng.gauss(mean, std)
        if lo is not None: v = max(lo, v)
        if hi is not None: v = min(hi, v)
        return v

    return Environment(
        temperature_c      = g("temperature_c",      lo=-30,  hi=50),
        humidity_pct       = g("humidity_pct",        lo=10,   hi=100),
        groundwater_level  = g("groundwater_level",   lo=0.0,  hi=1.0),
        freeze_thaw_cycles = int(max(0, g("freeze_thaw_cycles"))),
        salinity           = g("salinity",             lo=0.0,  hi=1.0),
        seismic_factor     = g("seismic_factor",       lo=0.0,  hi=1.0),
        settlement_rate    = g("settlement_rate",      lo=0.0),
    )


def _draw_quality(rng: random.Random) -> float:
    """
    Lognormal workmanship/material quality factor, mean=1.0, σ_log=0.18.

    Represents stone quality, mixing ratios, placement skill, curing conditions.
    A quality < 1 accelerates all failure modes proportionally.
    Clamped to [0.30, 3.0] to avoid numerical extremes.
    """
    log_q = rng.gauss(0.0, 0.18)
    return max(0.30, min(3.0, math.exp(log_q)))


# ─── survival surface ─────────────────────────────────────────────────────────

def survival_surface(
    regime:  str,
    horizon: int  = 500,
    n:       int  = 2000,
    seed:    int  = 1,
) -> Dict:
    """
    Monte-Carlo survival surface.

    For each of n (environment, quality) samples, evaluates every archetype.
    Records whether it survived the horizon and its critical failure mode.

    Returns:
        {archetype: {survival_frac, median_collapse, dominant_first_mode}}

    Calibration targets (--n 2000 --horizon 500 --seed 1):
        freeze_thaw  : roman_pozzolan best survival
        coastal_salt : roman_pozzolan best survival
        wet_clay     : dry_stone longest median_collapse (~272yr)
        seismic      : roman_pozzolan 0.0% survival (brittle)
        stable       : dry_stone ~91% survival (redundancy wins)
    """
    rng = random.Random(seed)
    acc: Dict[str, Dict] = {
        a: {"survived": 0, "collapse_years": [], "first_modes": []}
        for a in ARCHETYPES
    }

    for _ in range(n):
        env     = draw_env(rng, regime)
        quality = _draw_quality(rng)
        for arch in ARCHETYPES:
            s              = make(arch, env, quality_factor=quality)
            cname, ctime   = critical_mode(s)
            if ctime > horizon:
                acc[arch]["survived"] += 1
            else:
                acc[arch]["collapse_years"].append(int(min(ctime, horizon)))
            acc[arch]["first_modes"].append(cname)

    results: Dict = {}
    for a, d in acc.items():
        cy     = sorted(d["collapse_years"])
        median: Optional[int] = int(cy[len(cy) // 2]) if cy else None
        dom    = Counter(d["first_modes"]).most_common(1)[0][0]
        results[a] = {
            "survival_frac":       round(d["survived"] / n, 4),
            "median_collapse":     median,
            "dominant_first_mode": dom,
        }

    return results
