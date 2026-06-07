#!/usr/bin/env python3
"""
Bio-Grid American Manufacturing — Scrap-Alloy Contamination Physics Simulator
CC0 1.0 Universal — No rights reserved. Share freely.

Maps trace-element contamination in recycled Al alloys to regional injury risk
across four vectors, producing an exposure_weighted_risk_index per region.

Physics grounding (real metallurgy):
  Fe  → β-AlFeSi platelets (needle morphology, stress riser → brittle fracture)
        Sjolander & Seifeddine, J Mater Sci Technol 26(6) 2010
  Si  → stabilises β phase → compounds Fe embrittlement
  Cu  → galvanic pitting at CuAl2 precipitates + IACS conductivity penalty
        Hatch, "Aluminum: Properties and Physical Metallurgy", ASM 1984
  Pb  → food-contact migration under acid conditions (painted scrap, old solder)
        FDA/EFSA technical guidance on metallic food-contact materials
  Cd  → food toxicity; IARC Group 1 carcinogen (galvanised-coating carryover)
  Mn/Cr/V/Ti → solid-solution strengtheners → IACS conductivity collapse
        Skyllas-Kazacos, Electrochim. Acta 49(24) 2004

Injury vectors:
  FOOD_CAN   → oxide barrier breach (Fe brittleness, galvanic pitting) +
               Pb/Cd migration through acidic food contact
  ELECTRICAL → IACS drop → higher resistivity → resistive heating → fire risk
  MEDICAL    → ion leaching (Pb, Cd, Cu) + sterilisation failure when
               IACS < 40% (inductive autoclave heating becomes uneven)
  STRUCTURAL → β-AlFeSi brittle fracture + galvanic pit → crack initiation

Output:
  exposure_weighted_risk_index (EWRI) per region, descending.
  EWRI = Σ_v(score_v × product_share_v) × population_M

Usage:
  python3 contamination_sim.py            (human-readable table)
  python3 contamination_sim.py --json     (machine-readable NDJSON)
"""

import math
import sys
import json
from dataclasses import dataclass, asdict

# ─── Physics constants ────────────────────────────────────────────────────────

# β-AlFeSi embrittlement threshold
FE_PLATELET_THRESHOLD_PPM = 1500    # ~0.15 wt%; below this Fe stays globular/harmless
SI_BETA_STABILIZATION     = 0.55    # Si exponent in β-phase stability expression

# IACS conductivity penalty per 100 ppm of each element  (% IACS lost)
# Reference baseline: 1350-grade electrical Al = 61.0 % IACS at 99.7% purity
IACS_PENALTY_PER_100PPM = {
    "Cu": 0.35,   # CuAl2 precipitates — strongest electron-scattering defect in Al
    "Mn": 0.30,   # Mn stays in solid solution at typical casting speeds
    "Cr": 0.40,   # Cr: forms dispersoids but strong scatterer in solution
    "V":  0.50,   # V: highest solid-solution IACS penalty in Al
    "Ti": 0.20,   # Ti: moderate; also partitions to grain-boundary precipitates
    "Fe": 0.12,   # Fe: mostly in precipitates, lower bulk solid-solution fraction
    "Si": 0.10,   # Si: majority in eutectic, small bulk penalty
}
AL_BASE_IACS           = 61.0   # % IACS — pure 1350-Al baseline
IACS_STERILISE_THRESH  = 40.0   # % IACS — below this, RF/inductive autoclave heating fails

# Pb/Cd food migration (FDA/EFSA guidance)
PB_MIGRATION_FRACTION = 3.0e-4      # bulk Al → migrated food fraction under 3% acetic acid
CD_MIGRATION_FRACTION = 5.0e-4      # Cd more mobile (smaller ion, higher acid solubility)
PB_FDA_LIMIT_PPM      = 0.10        # mg/kg migrated food (FDA action level)
CD_EFSA_LIMIT_PPM     = 0.05        # mg/kg (EFSA Tolerable Weekly Intake-derived)

# Galvanic pitting (Cu drives pit formation at CuAl2 → pit depth ∝ Cu content)
CU_PIT_RATE_NORM = 8.0e-4           # normalised pit severity per ppm Cu [0–1 scale]

# ─── Data structures ──────────────────────────────────────────────────────────

@dataclass
class AlloyComposition:
    """Trace elements in ppm (parts per million by mass)."""
    Fe_ppm: float = 0.0
    Si_ppm: float = 0.0
    Cu_ppm: float = 0.0
    Pb_ppm: float = 0.0
    Cd_ppm: float = 0.0
    Mn_ppm: float = 0.0
    Cr_ppm: float = 0.0
    V_ppm:  float = 0.0
    Ti_ppm: float = 0.0

@dataclass
class RegionProfile:
    name:             str
    composition:      AlloyComposition
    population_M:     float   # millions of people served
    food_can_share:   float   # fraction of Al output → food cans
    electrical_share: float   # fraction → electrical conductors/wiring
    medical_share:    float   # fraction → medical devices / packaging
    structural_share: float   # fraction → structural members / fasteners

@dataclass
class InjuryScores:
    food_can:   float = 0.0
    electrical: float = 0.0
    medical:    float = 0.0
    structural: float = 0.0

@dataclass
class RegionResult:
    region:      str
    ewri:        float   # exposure_weighted_risk_index
    scores:      InjuryScores
    iacs_pct:    float   # computed IACS (%)
    brittleness: float   # β-AlFeSi index [0=none, 1=severe]

# ─── Physics functions ────────────────────────────────────────────────────────

def brittleness_index(c: AlloyComposition) -> float:
    """
    β-AlFeSi platelet embrittlement index [0, 1].

    Platelets nucleate when Fe > threshold; Si stabilises the β phase and
    amplifies brittleness. Index scales linearly with excess Fe and a
    power-law Si synergy term, capped at 1.
    """
    if c.Fe_ppm <= FE_PLATELET_THRESHOLD_PPM:
        return 0.0
    excess_fe  = c.Fe_ppm - FE_PLATELET_THRESHOLD_PPM
    si_synergy = 1.0 + SI_BETA_STABILIZATION * (c.Si_ppm / 5000.0)
    return min((excess_fe / 10000.0) * si_synergy, 1.0)

def iacs_percent(c: AlloyComposition) -> float:
    """Actual IACS conductivity (%) after all solid-solution and precipitate penalties."""
    loss = 0.0
    for elem, ppm in [
        ("Cu", c.Cu_ppm), ("Mn", c.Mn_ppm), ("Cr", c.Cr_ppm),
        ("V",  c.V_ppm),  ("Ti", c.Ti_ppm), ("Fe", c.Fe_ppm),
        ("Si", c.Si_ppm),
    ]:
        loss += (ppm / 100.0) * IACS_PENALTY_PER_100PPM[elem]
    return max(0.0, AL_BASE_IACS - loss)

def galvanic_damage(c: AlloyComposition) -> float:
    """
    Normalised galvanic pitting severity [0, 1].
    Cu drives pit initiation at CuAl2 precipitates via local galvanic cells.
    """
    return min(c.Cu_ppm * CU_PIT_RATE_NORM, 1.0)

def pb_dose_ratio(c: AlloyComposition) -> float:
    """Pb migrated dose / FDA action level. Values > 1 exceed the limit."""
    return (c.Pb_ppm * PB_MIGRATION_FRACTION) / PB_FDA_LIMIT_PPM

def cd_dose_ratio(c: AlloyComposition) -> float:
    """Cd migrated dose / EFSA TWI limit. Values > 1 exceed the tolerance level."""
    return (c.Cd_ppm * CD_MIGRATION_FRACTION) / CD_EFSA_LIMIT_PPM

def score_food_can(c: AlloyComposition) -> float:
    """
    FOOD_CAN injury score [0, 10].

    Pathways:
      • Pb/Cd migrate through oxide barrier into acidic food contents
      • Fe brittleness → can-seam cracking → barrier breach
      • Cu galvanic pitting → pinhole corrosion → barrier breach
    """
    pb  = pb_dose_ratio(c) * 4.0
    cd  = cd_dose_ratio(c) * 3.0
    brk = brittleness_index(c) * 2.0
    gal = galvanic_damage(c) * 1.0
    return min(pb + cd + brk + gal, 10.0)

def score_electrical(c: AlloyComposition) -> float:
    """
    ELECTRICAL injury score [0, 10].

    IACS drop → resistivity rise → I²R heating → fire risk.
    Heating is super-linear in resistivity loss (power ∝ 1/σ²).
    Mn/Cr/V/Ti drive most of the IACS collapse in recycled alloys.
    """
    iacs          = iacs_percent(c)
    iacs_loss_frac = max(0.0, AL_BASE_IACS - iacs) / AL_BASE_IACS
    heat_risk      = (iacs_loss_frac ** 1.5) * 8.0   # super-linear: power ∝ (1/IACS)^2
    pit_contrib    = galvanic_damage(c) * 2.0          # Cu pitting severs conductors
    return min(heat_risk + pit_contrib, 10.0)

def score_medical(c: AlloyComposition) -> float:
    """
    MEDICAL injury score [0, 10].

    Pathways:
      • Ion leaching (Pb, Cd, Cu) into body fluids / drug solutions
      • Sterilisation failure: IACS < 40% → uneven inductive autoclave heating
      • Device fracture from Fe brittleness during handling
    """
    ion_leach    = (pb_dose_ratio(c) * 2.0 +
                    cd_dose_ratio(c) * 1.5 +
                    galvanic_damage(c) * 2.0)
    steril_fail  = 3.0 if iacs_percent(c) < IACS_STERILISE_THRESH else 0.0
    device_brk   = brittleness_index(c) * 1.0
    return min(ion_leach + steril_fail + device_brk, 10.0)

def score_structural(c: AlloyComposition) -> float:
    """
    STRUCTURAL injury score [0, 10].

    β-AlFeSi platelets act as stress risers under cyclic load → brittle fracture.
    Cu galvanic pitting creates crack-initiation sites under sustained stress.
    """
    brk = brittleness_index(c) * 6.0
    gal = galvanic_damage(c) * 3.0
    return min(brk + gal, 10.0)

def compute_injury_scores(c: AlloyComposition) -> InjuryScores:
    return InjuryScores(
        food_can   = score_food_can(c),
        electrical = score_electrical(c),
        medical    = score_medical(c),
        structural = score_structural(c),
    )

def exposure_weighted_risk_index(profile: RegionProfile) -> float:
    """
    EWRI = Σ_v(score_v × product_share_v) × population_M

    Each injury-vector score is weighted by the fraction of that region's
    Al output going to that product category, then scaled by population
    exposed (millions). Regions with large populations and high-risk alloys
    in high-contact products score highest.
    """
    s = compute_injury_scores(profile.composition)
    weighted = (
        s.food_can   * profile.food_can_share   +
        s.electrical * profile.electrical_share +
        s.medical    * profile.medical_share    +
        s.structural * profile.structural_share
    )
    return round(weighted * profile.population_M, 4)

# ─── Regional data ────────────────────────────────────────────────────────────
#
# Contamination profiles reflect dominant scrap feed sources per region:
#   Duluth-Superior   — Iron Range taconite scrap: high Fe/Mn, low Pb/Cd
#   Detroit Metro     — Auto shredder residue: high Cu (wiring), Pb (body paint/solder)
#   Cleveland-Lorain  — Mixed steel/Al: elevated Fe, moderate Cu
#   Chicago-Gary      — Integrated mills + stainless carryover: high Mn/Cr
#   Milwaukee-Racine  — Al casting foundries: high Si (eutectic alloys), Fe
#   Minneapolis-StP   — Post-consumer: Pb concerns from pre-1978 building demolition scrap

REGIONS = [
    RegionProfile(
        name             = "Duluth-Superior (Iron Range)",
        composition      = AlloyComposition(
            Fe_ppm=3200, Si_ppm=1800, Cu_ppm=400,  Pb_ppm=150, Cd_ppm=20,
            Mn_ppm=1400, Cr_ppm=100,  V_ppm=50,    Ti_ppm=120,
        ),
        population_M     = 0.29,
        food_can_share   = 0.15,
        electrical_share = 0.40,
        medical_share    = 0.05,
        structural_share = 0.40,
    ),
    RegionProfile(
        name             = "Detroit Metro (Auto Scrap)",
        composition      = AlloyComposition(
            Fe_ppm=2800, Si_ppm=2200, Cu_ppm=1800, Pb_ppm=680, Cd_ppm=55,
            Mn_ppm=900,  Cr_ppm=220,  V_ppm=30,    Ti_ppm=80,
        ),
        population_M     = 4.39,
        food_can_share   = 0.10,
        electrical_share = 0.50,
        medical_share    = 0.10,
        structural_share = 0.30,
    ),
    RegionProfile(
        name             = "Cleveland-Lorain (Steel/Al Mixed)",
        composition      = AlloyComposition(
            Fe_ppm=4100, Si_ppm=2600, Cu_ppm=950,  Pb_ppm=310, Cd_ppm=38,
            Mn_ppm=1200, Cr_ppm=180,  V_ppm=65,    Ti_ppm=95,
        ),
        population_M     = 2.06,
        food_can_share   = 0.20,
        electrical_share = 0.35,
        medical_share    = 0.15,
        structural_share = 0.30,
    ),
    RegionProfile(
        name             = "Chicago-Gary (Integrated Mills)",
        composition      = AlloyComposition(
            Fe_ppm=2600, Si_ppm=1500, Cu_ppm=700,  Pb_ppm=420, Cd_ppm=42,
            Mn_ppm=2100, Cr_ppm=480,  V_ppm=90,    Ti_ppm=60,
        ),
        population_M     = 9.53,
        food_can_share   = 0.25,
        electrical_share = 0.30,
        medical_share    = 0.20,
        structural_share = 0.25,
    ),
    RegionProfile(
        name             = "Milwaukee-Racine (Foundry)",
        composition      = AlloyComposition(
            Fe_ppm=3500, Si_ppm=5800, Cu_ppm=620,  Pb_ppm=260, Cd_ppm=30,
            Mn_ppm=800,  Cr_ppm=140,  V_ppm=40,    Ti_ppm=110,
        ),
        population_M     = 1.57,
        food_can_share   = 0.15,
        electrical_share = 0.25,
        medical_share    = 0.10,
        structural_share = 0.50,
    ),
    RegionProfile(
        name             = "Minneapolis-St. Paul (Post-Consumer)",
        composition      = AlloyComposition(
            Fe_ppm=2100, Si_ppm=1600, Cu_ppm=550,  Pb_ppm=780, Cd_ppm=28,
            Mn_ppm=600,  Cr_ppm=90,   V_ppm=25,    Ti_ppm=70,
        ),
        population_M     = 3.64,
        food_can_share   = 0.30,
        electrical_share = 0.30,
        medical_share    = 0.15,
        structural_share = 0.25,
    ),
]

# ─── Simulation runner ────────────────────────────────────────────────────────

def run_simulation(regions=REGIONS):
    results = []
    for p in regions:
        c    = p.composition
        ewri = exposure_weighted_risk_index(p)
        results.append(RegionResult(
            region      = p.name,
            ewri        = ewri,
            scores      = compute_injury_scores(c),
            iacs_pct    = round(iacs_percent(c), 2),
            brittleness = round(brittleness_index(c), 4),
        ))
    results.sort(key=lambda r: r.ewri, reverse=True)
    return results

# ─── Output formatters ────────────────────────────────────────────────────────

def print_table(results):
    COL = 42
    hdr = (f"{'#':<3} {'Region':<{COL}} {'EWRI':>7}"
           f" {'FOOD':>6} {'ELEC':>6} {'MED':>5} {'STRUCT':>7}"
           f" {'IACS%':>6} {'BRIT':>6}")
    sep = "─" * len(hdr)
    print()
    print("Bio-Grid American Manufacturing — Contamination Hotspot Ranking")
    print(sep)
    print(hdr)
    print(sep)
    for i, r in enumerate(results, 1):
        s = r.scores
        print(
            f"{i:<3} {r.region:<{COL}} {r.ewri:>7.3f}"
            f" {s.food_can:>6.2f} {s.electrical:>6.2f}"
            f" {s.medical:>5.2f} {s.structural:>7.2f}"
            f" {r.iacs_pct:>6.1f} {r.brittleness:>6.4f}"
        )
    print(sep)
    print()
    print("EWRI   = exposure_weighted_risk_index = Σ(score_v × share_v) × population_M")
    print("IACS%  = computed conductivity (pure Al = 61.0%); fire risk rises sharply < 40%")
    print("BRIT   = β-AlFeSi brittleness index  [0 = no platelets,  1 = severe embrittlement]")
    print("Scores = 0–10 per vector; 10 = maximum physics-modelled severity")
    print()

def print_json(results):
    for r in results:
        print(json.dumps(asdict(r), indent=None))

# ─── Entry point ─────────────────────────────────────────────────────────────

def main():
    results = run_simulation()
    if "--json" in sys.argv:
        print_json(results)
    else:
        print_table(results)

if __name__ == "__main__":
    main()
