# 💸 Economic Projections

Modeling of regional and national economic impacts for BioGrid 2.0 rollout.

> **Re-derived August 2026.** Every figure on this page is now computed from published cost
> benchmarks rather than asserted. Inputs: [`cost_basis_2026.json`](cost_basis_2026.json).
> Derivation: `python3 tools/derive_economics.py`. Sources:
> [REFERENCES.md](../REFERENCES.md). Full audit trail:
> [docs/SCIENCE_UPDATE_2026.md](../docs/SCIENCE_UPDATE_2026.md).

---

## Initial Investment

**$39.7B – $88.5B** (Northwoods deployment, 2026 dollars, midpoint **$64B**)

| Line item | Derived cost | Basis |
|---|---|---|
| Underground transmission, 4,500 km | $22.6B – $45.3B | EEI HV underground $6–12M/mile, escalated to 2026$ |
| Substations and switching, ~90 sites | $1.8B – $9.0B | 50 km spacing × $20–100M/site (assumption) |
| Storage | $7.0B | Budget held fixed from original scope |
| Neural control core | $29M – $38M | 7 × GB200 NVL72 + facility |
| Software and integration | $0.6B – $3.1B | 2–5% of hard construction cost |
| Workforce and training | $0.9B – $3.7B | 3–6% of hard construction cost |
| Contingency | 20–30% | Standard pre-FEED practice |

The previous headline of **$85B** falls inside this range, so the top-line number survives.
The **allocation does not**. Transmission was budgeted at $18B against a derived
$22.6B–$45.3B. Compute was budgeted at $8B against a derived $29–38M. Software and
workforce were budgeted at $25B and $15B against derived $0.6–3.1B and $0.9–3.7B.

**The overhead alternative.** Running the same 4,500 km overhead rather than buried costs
**$5.0B – $10.0B** — a **$17B–$35B** difference. Burial is a defensible choice for
resilience and land use, but it is the single largest cost decision in this programme and
it should be argued explicitly rather than assumed.

---

## What the storage budget buys

At 2025 installed prices of **$150–250/kWh** (`bnef_battery_survey_2025`), the $7B storage
line delivers:

**28 – 47 GWh — equivalently 7.0 – 11.7 GW at four hours.**

This is the one line where the original figures were **conservative**. Stationary-storage
pack prices fell **45% in 2025 alone**, to $70/kWh, making stationary storage the cheapest
battery segment for the first time. The same budget buys substantially more energy than it
would have when this document was first written.

Stated as capacity rather than dollars so it stays meaningful as prices continue to move.

---

## Employment

Derived using PERI's published multipliers of **12.9–16 job-years per $1M** invested,
inclusive of direct, indirect and induced effects (`peri_employment_multipliers`).

| Measure | Derived |
|---|---|
| Total job-years over the build | 827,000 – 1,025,000 |
| Jobs sustained during 5-year build | 165,000 – 205,000 |
| Of which direct (on-site) | 66,000 – 103,000 |

**Units matter here, and the previous version of this page did not state them.** The
earlier figure of 125,000 construction jobs is defensible when read as
direct-plus-indirect-plus-induced sustained employment. Read as on-site construction
workers, it is roughly 3× too high.

### Permanent operations

Operating 4,500 km of underground cable and ~90 substations:

| Function | FTE |
|---|---|
| Cable and line crews | 90 – 180 |
| Substation crews | 270 – 720 |
| Control room and cyber | 50 – 150 |
| **Total grid O&M** | **410 – 1,050** |

The previous figure of **150,000 permanent jobs** is not a grid-operations number — grid
operations account for roughly **0.5%** of it. The remainder is reshored manufacturing
employment. That may well be a worthwhile national goal, but it follows from trade and
industrial policy, not from building transmission. The two are listed separately here
because conflating them is what made the original figure misleading.

---

## Returns

### The constraint

Minnesota and Wisconsin consume **132.9 TWh/yr** at roughly **12.5 ¢/kWh**
(`eia_state_profiles`). Including the Michigan Upper Peninsula, the total regional
electricity bill is about **$17.3B/yr**. That is every kilowatt-hour every customer in the
region buys — the ceiling on any benefit denominated in electricity cost.

The previous version of this page claimed returns that exceed it:

| Previous claim | Implied annual value | Share of the entire regional bill |
|---|---|---|
| $12B/yr energy cost savings | $12.0B | **69%** |
| 340% ROI over 15 years | $19.3B | **111%** |
| 4.2-year payback | $20.2B | **117%** |

These are not optimistic projections; they are arithmetically unavailable. No level of
technical performance can produce them, because the limit is the size of the market rather
than the efficiency of the system.

### What fits

**Congestion and dispatch-efficiency savings: $0.5B – $1.4B/yr** (3–8% of regional spend).

Over 15 years undiscounted, that is a benefit-cost ratio of **0.09 – 0.52** on avoided
energy cost alone — below 1.0, which is the correct and expected answer.

**Transmission is never justified on energy savings.** It is justified on reliability
value, avoided generation capital and enabling load growth, evaluated as a multi-value
benefit-cost ratio (`brattle_transmission_2025`) typically targeting 1.5–3.0. The
reliability term should be quantified with LBNL's ICE Calculator (`lbnl_ice`). That
analysis has not been done for this project and is the highest-value piece of work still
outstanding — without it, the benefit-cost ratio above is missing its largest legitimate
component and understates the case.

---

## Technology exports

The figure of **$150B/yr by 2040** has **no available derivation**. No public market-size
denominator supports it; it exceeds the revenue of the entire global grid-equipment sector
by a wide margin.

It is retained here as an **aspiration, explicitly not a projection**, and should not be
cited as a figure.

---

## Reproducing these numbers

```bash
python3 tools/derive_economics.py           # full derivation
python3 tools/derive_economics.py --json    # machine-readable
```

Inputs are in [`cost_basis_2026.json`](cost_basis_2026.json). Entries marked `ASSUMPTION`
are **not sourced data** — chiefly substation unit costs, soft-cost percentages, the
savings band and the O&M staffing ratios. Replace them with real figures as they become
available; MISO's Transmission Cost Estimation Guide (`miso_mtep25`) is the correct
reference class for the substation and line costs.

> "If you think BioGrid is expensive, try rebuilding without it."
>
> Fair. But the case has to be made against the reliability and avoided-capital value it
> actually delivers, not against savings the regional market cannot supply.
