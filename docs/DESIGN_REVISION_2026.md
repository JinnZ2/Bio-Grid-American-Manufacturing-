# Design Revision — 2026

The [science update](SCIENCE_UPDATE_2026.md) established what the evidence supports. It
left the design with open decisions rather than a verdict. This document closes them, and
sets out the governance and financial route from the design as written to one that can
actually be built.

Everything here is computed, not asserted:

```bash
python3 tools/transition_pathways.py                # ranked moves
python3 tools/transition_pathways.py --strategies   # three routes compared
python3 tools/transition_pathways.py --sensitivity  # does the ranking survive?
```

Parameters: [`data/transition_basis_2026.json`](../data/transition_basis_2026.json).
Costs: [`data/cost_basis_2026.json`](../data/cost_basis_2026.json). Sources:
[REFERENCES.md](../REFERENCES.md).

---

## The finding, first

**Three modifications are available today, need nobody's permission, and account for 60%
of all the value on the table for 5% of the effort.**

| | Move | Value | Effort | Kind |
|---|---|---|---|---|
| **M3** | Reallocate the over-budgeted lines | $43.8B | $1.5M | capital redirected |
| **M2** | HVAC default; HVDC only where distance earns it | $10.2B | $3.9M | capex risk avoided |
| **M4** | Specify grid-forming inverters at procurement | $691M | $8.7M | benefit enabled |

None has a prerequisite. None requires a consenting party beyond the programme itself.
Critical path: **zero years** — these are decisions, not projects.

Against that, the full path to financial close is **5.5 years and 11 governance and
financial gates**. Design work is **23% of the effort; the rest is permission.**

That ratio is the real result. The engineering problems in this project are cheap. The
consent problems are not, and they are almost entirely untouched.

---

## What changes

### M3 — Reallocate, don't refinance *(no prerequisite)*

The re-derivation found compute over-allocated by ~240×, software by ~14× and workforce by
~6×, while transmission was understated by 1.9×. The envelope was approximately right; the
allocation inside it was not.

| Line | As written | Derived | Freed |
|---|---|---|---|
| Neural hubs + processing | $8B | $34M | $8.0B |
| Grid software + AI | $25B | $1.9B | $23.1B |
| Workforce development | $15B | $2.3B | $12.7B |
| | | **Total** | **$43.8B** |

**This is not a saving.** No money is created — $43.8B that was budgeted for compute and
software that does not need to exist can buy transmission that does. The tool labels it
`capital_redirected` for exactly this reason, and the distinction matters when talking to
anyone who might fund it.

It is a spreadsheet change. It is also, by a factor of eleven, the highest-leverage move
available.

### M2 — HVAC by default *(no prerequisite)*

Converter stations are **30–40% of HVDC project capex** and are a fixed cost per terminal,
so HVDC loses to HVAC below roughly 500–600 km. A 4,500 km network built of shorter
segments is the wrong shape for HVDC.

The repository never makes this choice, which leaves a 30–40% capex swing unresolved. Make
it: **HVAC for the backbone, HVDC only where a single run earns its converters** — in this
footprint, the long lake crossings and nothing else.

Cost of deciding: zero. Value: ~$10.2B of avoided overrun risk.

### M4 — Grid-forming inverters, specified now *(no prerequisite, one-way)*

Grid-forming inverters establish voltage and frequency autonomously and provide synthetic
inertia. Grid-following inverters need an existing grid reference and **cannot black-start**.

Every "graceful collapse buffering" and "restart locally" claim in this repository is a
grid-forming capability. It does not fall out of the routing software.

Specify IEEE 2800-2022 with amendment 2800a on every inverter-based resource intended to
island. The premium at procurement is small. **The retrofit is not possible at any sensible
price**, which is why this ranks fourth on raw leverage but belongs in the do-now set: its
reversibility is 0.1, and an option you lose by not exercising it is not really free.

### M1 — Selective burial *(gated by a routing study)*

Buried cable costs about **4.5× the equivalent overhead line**. The design buries all
4,500 km without ever pricing the alternative — the largest unexamined decision in the
programme.

Bury where burial buys something: urban and highway crossings, wildfire-ignition corridors,
icing-exposed spans, sensitive habitat. Overhead elsewhere.

At 20% buried rather than 100%: **$21.2B avoided**. The 20% is an assumption; the real
number comes from the routing study (T1, ~$12M, 1 year), which is the cheapest way to
resolve the largest cost uncertainty in the project.

### M7 — Gate on measured reliability *(gated by the ICE study)*

The current expansion trigger is "grid reliability ≥ 99.95%". Nothing in this repository
measures reliability, so the gate tests a quantity that does not exist. Replace it with a
SAIDI/SAIFI improvement measured against the pre-build baseline.

This is also how the reliability benefit term gets populated — the single largest missing
piece of the benefit-cost case.

### M6 — Contract the load before building for it *(gated by MISO position)*

EIA's 2026 outlook makes data-centre load the dominant driver of US electricity growth, and
contracted load is how transmission is actually being financed in 2025–26. The region has
the two things such a tenant wants: cold water and cheap wind.

This changes **who pays**, not what gets built. It converts a speculative ratepayer-funded
build — which needs a benefit-cost case that currently does not close on energy savings —
into contracted revenue, which needs a counterparty.

---

## Tested and rejected

**M5 — Substituting storage for transmission does not pay at plausible ratios.**

Stationary storage fell 45% in 2025, so the trade is worth testing. It fails:

| | |
|---|---|
| Deferring 400 km of overhead | avoids **$664M** |
| Storage required at 0.020 GWh/km | costs **$1.6B** |
| Net | **−$936M** |

**Breakeven is 0.0083 GWh/km — about 8 MWh per kilometre deferred.** Above that, storage is
the more expensive way to buy the same deferral.

This is worth stating precisely rather than dropping, because the intuition ("batteries got
cheap, so build batteries instead of lines") is widespread and, at these numbers, wrong for
bulk transfer. Storage earns its place on other grounds — the $7B line already buys 28–47
GWh — but not as a transmission substitute at this scale.

---

## Transition: governance and financial

The modifications are cheap. Reaching the point where they matter is not.

### Three routes

| Route | Critical path | Gates | Effort | Trade |
|---|---|---|---|---|
| **Public-led / rate base** | 5.0 yr | 6 | $231M | No counterparty risk; maximum political exposure. Slowest gate is the tri-state compact plus three certificates of need. |
| **Anchor-tenant led** | 5.5 yr | 5 | $251M | Trades political risk for counterparty concentration. Highest total value; needs a signed tenant before capital commits. |
| **Federal corridor led** | 6.5 yr | 5 | $191M | Routes siting authority through federal designation instead of state certificates. Slowest, cheapest, most robust to any single state stalling. |

Siting authority is modelled as **either** state certificates of need **or** federal
corridor designation — that is why the federal route can reach financial close without
three state approvals, and why it takes 1.5 years longer to do it.

### The ordering that matters

```
M3 → M2 → T1 → M1 → M4 → G3 → F2 → M7 → M6 → F4 → F5 → G1 → G2 → G4 → F6 → BUILD
└──── free, today ────┘   └──────────── permission: 5.5 years ────────────┘
```

Two properties worth noting:

- **Everything cheap and reversible resolves before financial close (F6).** F6 has
  reversibility 0.2 — it is the point of no return, and the model deliberately front-loads
  every decision that can still be changed.
- **The routing study (T1) gates the single largest saving.** $12M and one year unlocks
  $21.2B of avoided burial cost. Nothing else in the programme has that shape.

---

## Does the ranking survive its own assumptions?

The effort model has four weights, and all four are assumptions. Varying them 4× in each
direction:

```
scenario                    M3   M2   M1   M4   M7   M6   M5
baseline                     1    2    3    4    5    6    7
time cheap (0.25x)           1    3    2    4    5    6    7
time dear (4x)               1    2    3    4    5    6    7
consent cheap (0.25x)        1    3    2    5    4    6    7
consent dear (4x)            1    2    3    4    6    5    7
irreversibility ignored      1    2    3    4    5    6    7
irreversibility 5x           1    3    2    6    4    5    7
```

**M3 is first in every scenario. M1, M2 and M3 are the top three in every scenario. M5 is
last in every scenario.** The ordering of the middle group moves; the conclusion does not.

The absolute leverage figures are not trustworthy — they depend on weights nobody has
measured. The *ordering* is, and that is what the tool is for.

---

## What this does not settle

1. **The reliability benefit is still unquantified.** Every route above books it, and none
   of them can until the ICE study exists. It is $250k of work gating the largest term in
   the case.
2. **The 20% burial fraction is a guess.** T1 replaces it with an answer.
3. **The storage/transmission substitution ratio is a guess.** The breakeven is exact; the
   requirement is not. A production-cost model would settle it.
4. **No route is costed for opposition.** The consent-party counts are proxies for
   difficulty, not for the probability that a party says no.
5. **Anchor-tenant concentration risk is unmodelled.** One counterparty carrying the
   revenue case is a different risk profile from a rate base, and the tool scores it only
   on speed and cost.

Per [CONTRIBUTING.md](../CONTRIBUTING.md), these belong in the unknowns list in
[`legacy/README.md`](../legacy/README.md), and they are recorded there.
