# 💰 Bio-Grid Economic Impact Analysis

> **Re-derived August 2026** from published cost benchmarks. Run
> `python3 tools/derive_economics.py` to reproduce every figure here. Inputs:
> [`data/cost_basis_2026.json`](../data/cost_basis_2026.json). Sources:
> [REFERENCES.md](../REFERENCES.md). Method and findings:
> [SCIENCE_UPDATE_2026.md](SCIENCE_UPDATE_2026.md).

## 💸 Total Investment: $39.7B – $88.5B over 5 years (midpoint $64B)

The previous figure of $85B falls inside this range. The allocation behind it does not
survive — three of the six line items were off by more than 2×, and one by more than 200×.

### 📦 Infrastructure Construction – $31.4B – $61.3B

| Item | Previously | Derived | Basis |
|---|---|---|---|
| Underground transmission, 4,500 km | $18B | **$22.6B – $45.3B** | EEI HV underground $6–12M/mile → $5.0–10.1M/km escalated to 2026$ |
| Substations + switching | $12B | **$1.8B – $9.0B** | ~90 sites at 50 km spacing × $20–100M (assumption) |
| Energy storage | $7B | **$7B → 28–47 GWh** | $150–250/kWh installed (`bnef_battery_survey_2025`) |
| Neural hubs + processing | $8B | **$29M – $38M** | 7 × GB200 NVL72 + facility |

**Transmission was understated by roughly 1.9×.** The original $18B implies $4.0M/km, below
the low end of the reference class before any inflation adjustment.

**The overhead alternative costs $5.0B – $10.0B** — $17B–$35B less. Buried cable runs about
4.5× the equivalent overhead line (`iet_transmission_comparison`). This is the largest
single cost decision in the programme and deserves an explicit argument.

**If HVDC is intended rather than HVAC,** converter stations alone are 30–40% of project
capex (`tse_hvdc_economics`), which makes HVDC uneconomic below roughly 500–600 km
regardless of line cost. For a 4,500 km network of shorter segments this is likely the
wrong technology. The repository has not yet made this choice explicitly.

### 🧠 Technology Development – $0.6B – $3.1B

Previously $25B, with $12B of it assigned to "grid software + AI systems." Derived at 2–5%
of hard construction cost, which is how utility programmes actually scope software and
integration.

**On the neural core.** The specification and the budget describe different projects:

- **As specified:** 500 H100 GPUs ≈ 62 DGX H100 systems, **625–688 kW**.
- **Current equivalent:** 7 × GB200 NVL72 = 504 Blackwell GPUs, **840–924 kW**, roughly 25×
  the H100 performance at comparable power (`nvidia_gb200_nvl72`). All-in with facility:
  **$29M–$38M**.
- **What $8B actually buys:** ~1,500–1,900 NVL72 racks — 109,000–137,000 GPUs at
  **181–229 MW**. That is a hyperscale AI training campus needing its own generation.

A grid control plane runs state estimation, contingency analysis and optimal power flow.
Those are not training workloads. It needs **O(1 MW)**, not O(200 MW). The specification is
the credible number.

### 👷 Workforce Development – $0.9B – $3.7B

Previously $15B. Derived at 3–6% of hard construction cost.

---

## 👷‍♂️ Job Creation

Derived with PERI multipliers of **12.9–16 job-years per $1M**, inclusive of direct,
indirect and induced effects (`peri_employment_multipliers`).

### 🏗️ Construction phase

| Measure | Derived |
|---|---|
| Total job-years over the build | 827,000 – 1,025,000 |
| Sustained jobs across 5 years | 165,000 – 205,000 |
| Of which direct, on-site | 66,000 – 103,000 |

The earlier claim of **125,000 construction jobs** sits inside this band and is defensible —
**as direct-plus-indirect-plus-induced sustained employment**. As on-site construction
headcount it is about 3× too high. PERI multipliers produce job-*years*, and the original
documents did not state which measure they were using. That ambiguity is the most common
way infrastructure employment claims mislead, so the units are now explicit.

### 🛠️ Permanent operations

| Function | FTE |
|---|---|
| Cable and line crews | 90 – 180 |
| Substation crews | 270 – 720 |
| Control room and cyber | 50 – 150 |
| **Total grid O&M** | **410 – 1,050** |

Against a previous claim of **150,000 permanent jobs**. Operating the grid accounts for
about **0.5%** of that. The other 99.5% is reshored manufacturing employment — a legitimate
industrial-policy objective, but one that follows from trade and industrial policy rather
than from building transmission. Listing them together made the grid look like it created
employment it does not create.

---

## 📈 Economic Return

### The denominator

Minnesota and Wisconsin consume **132.9 TWh/yr** at about **12.5 ¢/kWh**
(`eia_state_profiles`). With the Michigan UP, the regional electricity bill is roughly
**$17.3B/yr** — the ceiling on any electricity-denominated benefit.

### Why the previous return figures were withdrawn

| Previous claim | Implied annual value | Share of entire regional bill |
|---|---|---|
| Energy cost savings $12B/yr | $12.0B | **69%** |
| 15-year ROI of 340% | $19.3B | **111%** |
| Payback in 4.2 years | $20.2B | **117%** |

Each would require the project to capture most or all of every dollar the region spends on
electricity. These are not aggressive forecasts — they are arithmetically unavailable, and
no technical improvement can produce them.

### Derived return

**Congestion and dispatch-efficiency savings: $0.5B – $1.4B/yr** (3–8% of regional spend).

15-year undiscounted benefit-cost ratio on energy savings alone: **0.09 – 0.52**.

Below 1.0, and correctly so. **No transmission project is justified on energy savings.**
The justification is reliability value, avoided generation capital, and enabling load
growth — evaluated as a multi-value benefit-cost ratio (`brattle_transmission_2025`),
typically targeting 1.5–3.0.

The reliability term is the missing piece. It should be quantified with LBNL's ICE
Calculator (`lbnl_ice`), which has not been done for this project. Until it is, the ratio
above omits the project's largest legitimate benefit and **understates** the case.

---

## 🧲 Secondary Effects

Retained as qualitative claims. None are derived, and none should be cited as figures:

- **Workforce reskilling** — plausible in direction, unquantified in magnitude.
- **Local business growth** near hubs — a standard induced effect, already counted inside
  the PERI multiplier above. Do not add it again separately.
- **Export leadership: $150B/yr by 2040** — **no derivation exists.** It exceeds the
  revenue of the entire global grid-equipment sector by a wide margin. Retained as an
  aspiration, explicitly not a projection.
- **Tax revenue growth** — follows from the employment figures; not separately derived.

---

## ✅ Summary

What the re-derivation found:

- **The headline capital figure holds.** $85B sits inside the derived $39.7B–$88.5B.
- **The allocation does not.** Against derived midpoints: transmission understated **1.9×**
  ($18B vs $34B); compute overstated **~240×** ($8B vs $34M); software overstated **~14×**
  ($25B vs $1.9B); workforce overstated **~6×** ($15B vs $2.3B).
- **Storage was too pessimistic.** Battery prices fell faster than the plan assumed.
- **Construction jobs were roughly right**, once units are stated.
- **Permanent jobs and all three return figures were not.** They exceeded the size of the
  market they were drawn from.
- **The strongest argument for this project has not been made yet** — reliability value is
  where transmission economics actually live, and it remains unquantified here.

A better grid may well build a better economy. The case has to be made on benefits the
region can actually supply.
