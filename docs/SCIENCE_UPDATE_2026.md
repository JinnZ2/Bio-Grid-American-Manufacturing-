# Science Update — 2026

A refresh of the technical and quantitative claims in this repository against current
literature and agency data, completed **August 2026**. Every figure below resolves to
[`REFERENCES.md`](../REFERENCES.md).

This document is the audit trail. It records what the repository asserted, what the
evidence now says, and what was changed as a result — including the cases where the
original figure held up, and the cases where it did not.

---

## How this was done

Three passes, in order:

1. **Source the physics.** Every quantitative claim was traced to a citation or marked as
   an assumption. Nothing was left implying a provenance it does not have.
2. **Check the arithmetic.** Equations were checked for dimensional consistency,
   convergence and numerical stability — independently of whether the underlying idea is
   sound. Several failed, and the failures were mechanical rather than conceptual.
3. **Re-derive the economics.** Cost and jobs figures were rebuilt from current published
   benchmarks rather than adjusted. The derivation is executable:

   ```
   python3 tools/derive_economics.py
   ```

   Inputs live in [`data/cost_basis_2026.json`](../data/cost_basis_2026.json), each entry
   carrying a source key. Entries marked `ASSUMPTION` are not sourced and are labelled as
   such in the output.

**A note on method.** The most useful check applied here was not looking up better
numbers — it was dividing claimed benefits by the size of the market they must come from.
Three of this repository's headline economic claims fail that test by more than an order
of magnitude, and no amount of technical performance can rescue them. That check is cheap
and worth applying to every future figure added here.

---

## Summary of what changed

| Domain | Verdict | Action |
|---|---|---|
| Battery storage cost | Original was **conservative** — prices fell faster than assumed | Budget restated as delivered capacity |
| Underground transmission cost | **Understated ~1.9×** | Re-derived to $22.6B–$45.3B |
| Neural core compute | **Specification and budget differ by ~200×** | Both restated; hardware modernised |
| Total pilot capex | **Roughly right, wrong internally** | $39.7B–$88.5B derived; allocation rebuilt |
| Energy-savings claim | **Not achievable** — 69% of the entire regional bill | Replaced with derived $0.5B–$1.4B/yr |
| 340% ROI / 4.2-yr payback | **Not achievable** — 111–117% of the regional bill | Replaced with benefit-cost framing |
| Construction jobs | **Defensible**, if read as job-years | Units made explicit |
| Permanent jobs | **Overstated ~150×** for grid operations | Rescoped and relabelled |
| $150B/yr exports | **No derivation exists** | Retained, explicitly marked aspiration |
| AMOC collapse premise | **Weakened by observations** | Reframed around the observed record |
| Marine plastics | **Understated** — nanoplastics dominate | Updated with 2025 Nature data |
| Mycelium composites | **Real, but insulation-class** | Strength figures added as a constraint |
| Physarum vs. fungal mycelium | **Conflated in the tunnel spec** | Corrected — different organisms, different roles |
| Rectenna efficiency | **Lab peak ≠ ambient** | Both figures given |
| Air-quality cascade | **Correct as written** | Left alone; one transfer function flagged |
| Grid-forming inverters | **Now standardised** | IEEE 2800a referenced where islanding is claimed |
| Core equations | **Four mechanical errors** | Corrected in place |

---

## 1. Energy cost and performance

### What changed in the world

Solar and wind have now been the cheapest new-build generation in the United States for
ten consecutive years. Lazard's June 2025 v18 report puts unsubsidised utility-scale solar
at **$38–78/MWh** and onshore wind at **$37–86/MWh**, against gas combined cycle at
**$48–109/MWh** (`lazard_lcoe_v18`).

Two things in that are worth noticing, because they cut against the usual narrative:

- **The ranges tightened but the floors rose.** Solar was $29–92/MWh in 2024 and is
  $38–78/MWh now. The cheapest projects got more expensive. Interconnection queues, labour
  and equipment costs are pushing the floor up even as the technology improves.
- **New gas got more expensive, not less.** New-build CCGT capital cost hit a ten-year
  high. Existing gas remains competitive on fuel cost, but building new gas no longer is.

Real-world capacity factors for 2025 (`eia_capacity_factors_2025`): wind **34.2%**,
utility-scale solar **24.4%**, gas **58.4%**, nuclear **91.0%**. Wind and solar together
supplied a record **17%** of U.S. generation (`eia_wind_solar_record_2025`).

### Storage — the one place the repository was too pessimistic

BloombergNEF's December 2025 survey found stationary-storage packs at **$70/kWh**, down
**45%** in a single year — the steepest fall of any battery segment, and the first time
stationary storage has been the cheapest segment (`bnef_battery_survey_2025`). Installed
utility-scale system cost, including balance of system and installation, is **$150–250/kWh**.

The repository allocates **$7B** to storage without stating what that buys. At current
installed prices it buys **28–47 GWh**, or **7.0–11.7 GW at four hours**. That is a
serious amount of storage — considerably more than the same budget would have bought when
the figure was written.

**Change made:** the storage line is now expressed as delivered capacity rather than as a
budget number, so it stays meaningful as prices continue to move.

### Solar cell efficiency

Perovskite–silicon tandems reached **34.85%** NREL-certified in April 2025
(`perovskite_record`). Commercial tandem modules ship at **24.5%**.

That gap matters for any document in this repository that assumes near-term deployment of
record-efficiency cells. Laboratory record and purchasable product are separated by 7–10
percentage points and several years. Silicon at 22–23% module efficiency remains the
planning assumption.

---

## 2. Transmission — where the cost estimate broke

The pilot specifies **4,500 km** of underground transmission at **$18B**, implying
**$4.0M/km** ($6.4M/mile).

Against the reference class (`eei_underground_conversion`), high-voltage underground
transmission runs **$6–12M/mile** before escalation. Converting to kilometres and
escalating to 2026 dollars gives **$5.0–10.1M/km**, so 4,500 km costs **$22.6B–$45.3B**.
The original figure sits below the low end of the range before inflation is even applied.

Two things compound this:

- Buried cable costs roughly **4.5×** the equivalent overhead line
  (`iet_transmission_comparison`). Running the same 4,500 km overhead would cost
  **$5.0B–$10.0B** — a $17B–$35B decision that the repository makes implicitly, on
  aesthetic and resilience grounds, without ever pricing the alternative.
- HVDC cable and converter-station supply chains have inflated faster than general
  construction indices since 2021. The 1.35× escalator used here is a floor, not a
  best estimate.

If HVDC is intended rather than HVAC, converter stations alone are **30–40% of project
capex** (`tse_hvdc_economics`) — a fixed cost that makes HVDC uneconomic below roughly
500–600 km regardless of how cheap the line gets. For a 4,500 km network of shorter
segments, this is likely the wrong technology, and the repository does not currently
address the choice.

**Change made:** transmission cost re-derived and the overhead alternative priced
explicitly, so the burial decision is visible as a decision.

---

## 3. Compute — the specification and the budget describe different projects

The repository specifies **500 NVIDIA H100 GPUs** at the Duluth-Superior neural core, and
separately allocates **$8B** to "neural hubs + processing centers."

These are not the same project. They are not within two orders of magnitude of each other.

**500 H100s** is about 62 DGX H100 systems drawing **625–688 kW** (`nvidia_gb200_nvl72`).
On current hardware the equivalent is **7 × GB200 NVL72 racks** — 504 Blackwell GPUs at
**840–924 kW**, delivering roughly 25× the H100 performance at comparable power. All-in,
including facility, that is **$29M–$38M**.

**$8B** buys approximately **1,500–1,900 NVL72 racks**: 109,000–137,000 GPUs drawing
**181–229 MW**. That is a hyperscale AI training campus. It would be among the largest
computing facilities in North America, and it would need its own dedicated generation.

A control plane for a regional grid needs **O(1 MW)**, not O(200 MW). Grid state
estimation, contingency analysis and optimal power flow are not training workloads. The
specification is the credible number; the budget line is not.

**Change made:** hardware modernised from H100 to GB200 NVL72, power and cost derived, and
the contradiction documented rather than quietly averaged away.

---

## 4. Economics — re-derived

Running `tools/derive_economics.py`:

```
Underground transmission, 4,500 km   $22.6B - $45.3B
Substations and switching (90 sites) $1.8B  - $9.0B
Storage (budget held fixed)          $7.0B
Neural control core                  $29M   - $38M
Software and integration             $0.6B  - $3.1B
Workforce and training               $0.9B  - $3.7B
--------------------------------------------------
With 20-30% contingency              $39.7B - $88.5B
```

**Midpoint $64B, against the original claim of $85B.**

The headline number survives — $85B falls inside the derived range. The **allocation does
not**. Transmission is roughly twice what was budgeted; compute is two orders of magnitude
less; software and workforce, which the original documents assign $25B and $15B, derive to
**$0.6–3.1B** and **$0.9–3.7B** when scaled as a share of hard construction cost the way
utility programmes actually scope them.

### The claims that fail

Minnesota and Wisconsin together consume **132.9 TWh/yr** at an average retail price near
**12.5 ¢/kWh** (`eia_state_profiles`). Adding the Michigan Upper Peninsula, the regional
electricity bill is approximately **$17.3B/yr**. That is the entire market — every
kilowatt-hour every customer buys.

Against that denominator:

| Claim | Implied annual value | Share of the entire regional bill |
|---|---|---|
| $12B/yr energy cost savings | $12.0B | **69%** |
| 340% ROI over 15 years | $19.3B | **111%** |
| 4.2-year payback | $20.2B | **117%** |

These are not aggressive projections. They are arithmetically unavailable. Saving 69% of
all regional electricity spending would require electricity to become nearly free while
consumption held constant. Returning 111% of it annually would require the project to
generate more value than the region's entire electricity sector produces.

No technical performance improvement can fix this, because the constraint is the size of
the market, not the efficiency of the system.

**What fits instead:** a transmission-and-controls programme plausibly delivers **3–8%**
in congestion and dispatch-efficiency savings — **$0.5B–$1.4B/yr**. Over 15 years,
undiscounted, that is a benefit-cost ratio of **0.09–0.52** on avoided energy cost alone.

Below 1.0 — which is the correct and unsurprising answer. **Transmission is never
justified on energy savings.** It is justified on reliability value, avoided generation
capital, and enabling load growth, evaluated as a multi-value benefit-cost ratio
(`brattle_transmission_2025`), typically targeting 1.5–3.0. Reliability value should be
quantified with LBNL's ICE Calculator (`lbnl_ice`); this repository has never done so, and
that is the single highest-value analysis still missing.

**Change made:** "340% ROI" and "4.2-year payback" removed as unsupportable. Replaced with
a benefit-cost framing and an explicit statement of which benefit terms remain unquantified.

### Jobs — right number, wrong units

PERI's published multipliers are **12.9–16 job-years per $1M** invested, inclusive of
direct, indirect and induced effects (`peri_employment_multipliers`). Applied to the $64B
midpoint: **827,000–1,025,000 job-years**, or **165,000–205,000 jobs sustained** across a
five-year build, of which **66,000–103,000** are direct.

The original claim of **125,000 construction jobs** is **defensible** — it sits inside that
band. But only if read as direct-plus-indirect-plus-induced sustained employment. Read as
on-site construction workers, it is roughly 3× too high. The original documents never say
which they mean, and this is the single most common way infrastructure job claims mislead.

**Permanent jobs is a different story.** Operating 4,500 km of underground cable and ~90
substations requires:

| Function | FTE |
|---|---|
| Cable and line crews | 90–180 |
| Substation crews | 270–720 |
| Control room and cyber | 50–150 |
| **Total** | **410–1,050** |

Against a claim of **150,000 permanent jobs**. Grid operations account for roughly **0.5%**
of it. The remainder is reshored manufacturing employment — a plausible industrial-policy
goal, but a consequence of trade and industrial policy, not of building a grid. Attributing
it to the grid is a category error.

**Change made:** job figures now state their units. Grid O&M and industrial-policy
employment are separated.

### The claim with no derivation

**$150B/yr in technology exports by 2040** has no available derivation. No public
market-size denominator supports it; it exceeds the revenue of the entire global
grid-equipment sector by a wide margin.

Per the citation policy, it is retained but explicitly labelled an aspiration rather than
a projection. It should not be cited as a figure.

---

## 5. AMOC — the premise needs reframing

The `AMOC/` module is built on a collapse occurring over a **1–2 year** period, with
infrastructure pre-positioned to harvest the transition.

The observational record does not support that timeline. The RAPID array at 26°N shows
weakening of **1.0 [0.4–1.6] Sv per decade** over 2004–2023 — consistent with climate
model projections and explicitly **not consistent with collapse in the mid-21st century**
(`amoc_rapid_mccarthy_2025`). The same analysis finds the trend will not become
statistically "unfamiliar" (signal-to-noise > 2) until the **2040s**, or "unknown" (S/N >
3) until the **2060s**.

Observationally constrained projections give roughly **50% weakening by 2100** under
high emissions (`amoc_sciadv_2025`) — a major climate event, but a century-scale decline,
not a two-year transition.

**The magnitude is genuinely contested.** A 2026 preprint argues for **2.6 ± 0.7 Sv per
decade** at 26°N, roughly 20 Sv falling to 15 Sv (`amoc_opinion_2026`) — substantially
faster than the peer-reviewed RAPID analysis. It is a preprint and it disagrees with the
observation record; both are cited here deliberately. Separately, eddy-resolving ocean
models show **weaker** AMOC response to Greenland meltwater than coarse-resolution models
(`amoc_eddying_2026`), which matters because meltwater forcing is the mechanism this
module assumes.

**What this means for the module.** The energy-harvesting concepts — thermal gradient,
salinity gradient, pH differential, turbulence — are not invalidated. Gradients exist
whether or not a collapse occurs. But the framing does not survive: there is no
short-duration, high-intensity "transition energy" window to pre-position for. Gradient
harvesting has to justify itself against ordinary ocean-energy economics, on gradients
that are changing over decades.

**Change made:** the AMOC framework is reframed around the observed record with the
disagreement stated. The 1–2 year collapse premise is marked as unsupported.

---

## 6. Marine plastics — the repository understated the problem

The `Waste-management/Microplastics.md` framework targets microplastics. The dominant
fraction is smaller than that.

A July 2025 *Nature* study found **27 million tonnes of nanoplastics in the North Atlantic
alone** — roughly **nine times all larger plastic debris in every ocean combined**
(`nanoplastics_nature_2025`). The surface mixed layer holds **11.73–15.20 Mt**.
Concentrations run **18.1 mg/m³** at the surface, **10.9 mg/m³** at ~1 km depth, and
**5.5 mg/m³** near the seabed. The authors describe the estimate as conservative — some
common polymers were undetectable by their method.

This changes the engineering problem rather than merely enlarging it. The module's
electrostatic and piezoelectric capture mechanisms assume particles large enough to carry
meaningful triboelectric charge and to couple mechanically to a resonant structure.
Nanoscale particles behave as colloids: Brownian motion dominates, surface chemistry
dominates capture, and mechanical filtration at that scale means processing the water
column itself.

**On the biological pathway:** enzymatic depolymerisation has matured. Carbios' LCC-ICCG
converts **98% of PET to monomers in 24 hours**, with enzyme loading cut 3× and reaction
temperature reduced from 72 °C to 68 °C (`petase_acscatal_2023`). This substantially
outperforms the IsPETase-derived figures the module currently cites — but it is a
**reactor** process on collected, sorted, pre-treated PET. It is not an in-ocean
remediation pathway, and the module should not present it as one.

**Change made:** nanoplastic data and current enzyme performance added, with the
scale-dependence of the capture mechanisms made explicit.

---

## 7. Biological materials and algorithms

### Mycelium composites — real, and bounded

The literature has matured considerably (`mycelium_jof_2025`, `mycelium_architecture_2025`).
Machine learning now predicts mechanical properties well: **R² = 0.992** for internal
bonding, **R² = 0.979** for compressive strength (`mycelium_ann_2025`).

The number that governs everything: pre-cultured mycelium composites reach compressive
strength **≥ 0.08 MPa** and flexural strength **≥ 11 N** (`mycelium_buildings_2025`).

Structural concrete is 20–40 MPa. **Mycelium composites are roughly 250–500× weaker.**
They are insulation-class materials, and the literature is clear that thermal insulation,
acoustic absorption and fire performance are where they compete — not load-bearing
structure.

This determines which layer of a structure these materials can occupy. A mycelium composite
can be tunnel lining, thermal barrier or duct insulation. It cannot be the tunnel.

**The repository already gets this right.** `underground-bio-tunnel-specs.md` specifies a
6-inch structural concrete liner carrying the load, with the biological layer at 2 inches
on top of a 4-inch growth medium. That is the correct allocation. The strength figures are
added here so the constraint is explicit and stays that way.

### One taxonomic correction

`underground-bio-tunnel-specs.md` describes the "mycelial inoculation matrix" as
"engineered **Physarum polycephalum** strains."

Physarum polycephalum is an **acellular slime mould** in Amoebozoa — a protist. It is not a
fungus and it does not produce mycelium. It forms a **plasmodium**: a single multinucleate
cell that spreads as a network of protoplasmic tubes. Fungal mycelium is a mass of
hyphae — walled, septate or coenocytic filaments of a completely different lineage.

The distinction has engineering consequences, so it is not pedantry:

| | Physarum plasmodium | Fungal mycelium |
|---|---|---|
| Structure | Single multinucleate cell | Multicellular hyphal network |
| Mechanical role | None — no structural strength | Binds substrate into rigid composite |
| Best use here | Network optimisation, routing, sensing | Composite material, insulation |
| Persistence | Motile, reconfigures continuously | Fixed once grown and dried |

Both organisms appear in this repository and both are used appropriately — Physarum for the
network optimiser, fungal mycelium for composites. Only the labelling conflates them. A
tunnel layer intended as **structural biocomposite** needs a fungus; a layer intended as an
**adaptive routing substrate** needs Physarum. They cannot substitute for each other.

### Physarum and ant colony optimisation — sound, and worth stating why

The Physarum-derived algorithms in `Regional-bio-grid/physarum-network-optimizer.js` rest
on well-established work: reinforcing high-load links while pruning unused ones solves
shortest path, minimum-risk path, network design, and Voronoi/Delaunay construction
(`physarum_review`).

One 2025 result is directly relevant. Increasing extracellular matrix viscosity slows
network expansion but **does not change final network complexity** — fractal dimension
converges to the same value across all viscosity conditions (`physarum_viscosity_2025`).
Substrate resistance changes how fast the network forms, not what it converges to. For a
grid-routing analogy, that is a useful and non-obvious property: the optimiser's converged
topology should be robust to the cost of laying cable, even though the schedule is not.

The ant colony optimisation formulation in `Technical-equations.md` is the standard ACO
transition rule and is correct as written.

---

## 8. Grid control — the standards landscape moved

The repository's self-healing and autonomous-reconfiguration concepts now have a standards
context that did not exist when they were written.

**IEEE 2800-2022**, with amendment **2800a**, sets minimum requirements for inverter-based
resources interconnecting with transmission systems, and the amendment specifically reduces
barriers for **grid-forming** equipment (`ieee_2800`). Grid-forming inverters establish
voltage and frequency autonomously and provide synthetic inertia — unlike grid-following
inverters, which need an existing grid reference and cannot black-start.

This matters directly. The repository's "graceful collapse buffering" and "restart locally"
properties are **grid-forming capabilities**, and they are now specifiable against a
published standard (`doe_gfm_specs`) rather than described qualitatively. Any node intended
to island and restart must be specified as grid-forming.

**Change made:** grid-forming requirements referenced where islanding behaviour is claimed.

---

## 9. Air quality cascade — sound premise, one real gap

The `src/air-quality-cascade/` module models ozone-driven degradation of conductors and
elastomers. On review, **its physical basis is the strongest-sourced work in this
repository** and needed no correction.

The module explicitly rejects a "local trucks cause local ozone" narrative in favour of
transported wildfire plumes as the primary driver: fires emit NOₓ, VOCs and HOₓ precursors
directly; ozone forms inside the plume during transport and arrives pre-formed; the plume
is an air mass and so blankets terrain uniformly, independent of local ground-source
density; and NOₓ-limited rural air yields more ozone per unit NOₓ than NOₓ-saturated urban
air. It cites Wotawa & Trainer (2000), Jaffe & Wigder (2012), FIREX-AQ and two 2025 ACP
papers. That is correct atmospheric chemistry, correctly attributed.

**Do not conflate the two ozone trends.** Weather-adjusted U.S. anthropogenic ozone is
**declining** — May–September averages down about **10 ppb** and 98th-percentile values
down about **20 ppb** since 2002 (`epa_ozone_trends`) — while wildfire-driven exceedances
are rising. Background tropospheric ozone sits at **33–48 ppb** and is increasing in some
regions globally (`ozone_acp_2025`). These are three separate signals on different
timescales. The module is right to model the wildfire term; anyone extending it should not
reach for the general trend, which points the other way.

**The one real gap: accelerated test data needs a transfer function.** Standard ozone
testing of vulcanised rubber uses **250–2,000 ppb** (`ozone_elastomer_testing`) — **5–50×
ambient background**, including plume conditions. Degradation rates taken from those tests
cannot be applied directly to field exposure without an acceleration-factor correction.
Doing so overstates real degradation by a large and unquantified factor, and this affects
the elastomer and conductor-corrosion kinetics downstream in the cascade.

**Change made:** the atmospheric model was left alone — it is correct. The
accelerated-to-field transfer function is flagged as the outstanding work.

---

## 10. Storage and RF physics

### CAES

Real round-trip efficiencies, measured or modelled (`caes_efficiency_2025`):

| Configuration | Round-trip efficiency | Status |
|---|---|---|
| Liquid piston adiabatic + packed-bed thermal | 72.6% | Modelled |
| Underwater adiabatic, real operating conditions | 64.1% | Measured |
| Gravity-assisted isobaric shaft | 87.1% energy / 70.1% exergy | **Modelled only, not built** |

The distinction in that last row matters. The 87.1% figure is an optimised model of a
system that does not exist. The honest planning number for CAES is **60–73%**.

Usefully, adiabatic CAES is now assessed as viable for **10–100 hour** storage durations
(`caes_iscience_2025`), with a **15% experience rate** as capacity scaled from 10 to 100 MW
(`caes_nature_reviews_2026`). That is precisely the duration regime where lithium-ion is
uneconomic — so CAES and batteries are complements in this design, not competitors.

### Rectennas

Reported RF-to-DC conversion efficiency reaches **97.18%** (`rectenna_review_2025`). That
number should not be used for planning. It is measured at high input power in a controlled
setup.

The figure that matters for ambient harvesting is **32% average across 2–18 GHz at −5 dBm**
(`rectenna_broadband_2025`). A representative 5G-band prototype produces **0.91 V DC at 0
dBm** input. Losses are dominated by rectifier diode non-linearity, transmission-line
attenuation and antenna–rectifier impedance mismatch — all of which worsen as input power
falls.

Any "sky network" or ambient-harvesting element in this repository must be sized against
the ~32% figure, and against the recognition that ambient RF power density supports
sensor-class loads, not infrastructure-class ones.

---

## 11. Equation corrections

Four mechanical errors, found by checking dimensions and convergence rather than by
disputing any concept. All are corrected in place.

### 11.1 The phi self-repair recursion diverges

`Technical-equations.md` gave:

```
W(t+1) = φ × W(t) + ΔL × (1 - φ)        φ ≈ 1.618
```

with the comment "this keeps learning converging."

It does the opposite. The homogeneous solution is `W(t) = φᵗ · W(0)`, and since **φ > 1**
this grows without bound. A fixed point exists at `W* = ΔL`, but it is **unstable** —
any perturbation grows geometrically at 1.618× per step. The `(1 − φ)` coefficient is also
negative, so the correction term pushes away from the loss differential rather than toward
it.

**Correction:** use the reciprocal, `φ⁻¹ = 1/φ ≈ 0.618` (equivalently `φ − 1`, since
`1/φ = φ − 1`):

```
W(t+1) = φ⁻¹ × W(t) + (1 - φ⁻¹) × ΔL      φ⁻¹ ≈ 0.618
```

Now the coefficients are positive and sum to 1, the fixed point is still `W* = ΔL`, and it
is **stable** — convergence is geometric at 0.618 per step, about 1.6% of initial error
remaining after 9 steps. This is an exponential moving average with a golden-ratio
smoothing constant, which is what the text describes.

The golden ratio is preserved. Only its reciprocal is used, which is the form that
converges.

### 11.2 The CAES equation mixes two thermodynamic processes

```
E_air = P × V × ln(P2/P1) / (γ - 1)
```

The `ln(P₂/P₁)` term is the **isothermal** work integral. The `1/(γ−1)` term is from the
**adiabatic** work expression. Combining them describes no physical process, and the result
is dimensionally inconsistent with either.

**Correction** — state whichever process is intended:

```
Isothermal:  E = P₁V₁ · ln(P₂/P₁)
Adiabatic:   E = (P₁V₁)/(γ-1) · [(P₂/P₁)^((γ-1)/γ) - 1]
```

Real CAES is neither, which is why measured round-trip efficiency is 64–73% rather than
the ~100% either ideal expression implies. Multiply by the round-trip efficiency from §10.

### 11.3 The swarm product underflows to zero

`docs/Bio-hybrid-equations.md` gives:

```
A = Π(i=1 to M) [p_i(t) × η_ij × τ_ij(t)]
```

Each `p_i` is a probability in [0,1]. A product of M such terms decays exponentially in M
and underflows double-precision floating point at roughly M ≈ 300 for typical values — and
reaches numerically meaningless magnitudes well before that. For any realistic swarm size
this evaluates to zero, which then zeroes the entire `Ψ = F × A × C` product.

**Correction:** work in log space, which is numerically stable and monotonically
equivalent:

```
log A = Σ(i=1 to M) [log p_i(t) + log η_ij + log τ_ij(t)]
```

Or, if a bounded aggregate is wanted rather than a joint likelihood, use the normalised
geometric mean `A = exp((1/M) Σ log(...))`.

### 11.4 A stray π in the area ratio

```
Area_ratio = π × (r_i²/r_j²) = K_i/K_j
```

The ratio of two circle areas is `(πr_i²)/(πr_j²) = r_i²/r_j²`. The π cancels. As written,
the expression is off by a factor of π ≈ 3.14159.

**Correction:**

```
Area_ratio = r_i²/r_j² = K_i/K_j
```

### Also worth noting

- **`Cp = 0.35–0.5` for helical wind collectors is optimistic.** The Betz limit caps any
  wind turbine at `16/27 ≈ 0.593`. Helical vertical-axis designs typically underperform
  horizontal-axis turbines, and the upper end of the stated range is not well supported.
  Flagged rather than replaced — no single authoritative source covers the geometry space.
- **`E_total = η × I × A × t` needs derates.** Plane-of-array irradiance, temperature
  coefficient, soiling and inverter efficiency all reduce it. The reality check is the
  measured 2025 U.S. utility-scale solar capacity factor of **24.4%**.
- **The free-space path loss and ant colony optimisation formulas are correct** as written.

---

## Open work

> **Items 3 and 4 below were closed by [DESIGN_REVISION_2026.md](DESIGN_REVISION_2026.md)**,
> which turns this review's findings into design changes and scores them by leverage. Run
> `python3 tools/transition_pathways.py`.

Ranked by how much the conclusions depend on them:

1. **Quantify reliability value with the ICE Calculator** (`lbnl_ice`). Without it, the
   benefit-cost ratio in §4 is missing its largest legitimate term, and the project looks
   worse than it probably is. Highest-value analysis outstanding.
2. **Derive an accelerated-to-field transfer function for the ozone cascade** (§9). The
   atmospheric model is sound; the elastomer degradation kinetics rest on test data taken
   at 5–50× ambient concentration.
3. **Decide HVAC or HVDC.** Converter stations at 30–40% of capex make this decisive for a
   4,500 km network of shorter segments, and the repository is currently silent.
4. **Price the burial decision.** Overhead costs $17B–$35B less. That trade deserves an
   explicit argument, not an implicit assumption.
5. **Replace assumed substation costs** with MISO MTEP figures (`miso_mtep25`).
6. **Re-scope the AMOC module** around decadal gradients rather than a transition event.
7. **Re-derive the export projection** or retire it.

## Maintenance

Lazard, BNEF, EIA STEO and the NREL ATB all publish annually. When they do:

1. Update the affected entries in `data/cost_basis_2026.json`.
2. Update the corresponding citation in `REFERENCES.md`, including the figure.
3. Re-run `python3 tools/derive_economics.py` and update §4 above.

Because the derivation is executable, refreshing the economics is a data edit and a script
run — not a rewrite.
