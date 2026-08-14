# Legacy — the falsification record

This is not a graveyard. It is the part of the method that most projects throw away.

```
hypothesize → run → result falsified → edit claim → search for unknowns → rerun
                          │                                    │
                          └────────── recorded here ───────────┘
```

A claim that was tested and failed is worth more than a claim that was never tested. It
tells you the shape of the problem, which check caught it, and where to look next. Deleting
it destroys the only evidence that the method ran. **Precedence carries.**

So these files stay, and they stay legible — with the original claim intact, the test that
falsified it, and the revised claim beside it. Anyone can re-run the check and disagree.

**One rule: nothing here is current.** These are prior states. For a live figure start at
[REFERENCES.md](../REFERENCES.md); for why one changed, read
[docs/SCIENCE_UPDATE_2026.md](../docs/SCIENCE_UPDATE_2026.md).

| Folder | Contents |
|---|---|
| [`pre-2026-refresh/`](#pre-2026-refresh) | Documents that still exist — these are their *previous states* |
| [`obsolete/`](#obsolete) | Files removed outright — no current counterpart |

---

## The falsification log

Each row is one full cycle. The **test** column is the point of the whole exercise: the
check that decided it, so it can be re-run.

### Cycle 1 — regional economics

The test that did most of the work was not a better cost lookup. It was dividing every
claimed benefit by the size of the market it must come from.

**Denominator:** MN + WI + MI-UP retail electricity = **$17.3B/yr**
(`eia_state_profiles`, 2024). That is every kilowatt-hour every customer buys.

| Hypothesis | Test | Result | Revised claim |
|---|---|---|---|
| $12B/yr energy cost savings | ÷ regional market | **69% of it** — falsified | $0.5B–$1.4B/yr (3–8%) |
| 340% ROI over 15 years | ÷ regional market | **111%** — falsified | Benefit-cost ratio, target 1.5–3.0 |
| 4.2-year payback | ÷ regional market | **117%** — falsified | Not applicable; BCR instead |
| $85B annual impact (seed docs) | ÷ regional market | **~5× the market** — falsified | Superseded in payloads |
| $8.5B annual return (FullHex) | ÷ regional market | **49%** — falsified | Same derived band |
| 500K jobs + $85B, Michigan alone | vs programme totals | Exceeds the whole 3-state pilot — falsified | Withdrawn as unsourced |
| 150,000 permanent jobs | Bottom-up O&M staffing | Grid ops = **0.5%** of it — falsified | 410–1,050 FTE |
| 125,000 construction jobs | PERI multipliers | **Survived** — as job-years, not headcount | Units made explicit |
| $85B total capex | Line-by-line re-derivation | **Survived** the total, failed the allocation | $39.7B–$88.5B, rebuilt |
| $150B/yr exports by 2040 | Searched for a denominator | **No test available** | Retained as aspiration only |

The last row is its own category. A claim that cannot be tested is not falsified — it is
*unfalsifiable*, which is a different and more serious problem. It stays labelled as such.

### Cycle 2 — equations

Found by checking dimensions and convergence, not by disputing any concept.

| Hypothesis | Test | Result | Revised claim |
|---|---|---|---|
| `W(t+1) = φ·W(t) + ΔL·(1-φ)` converges | Solve the recursion | φ > 1 → `W(t) = φᵗ·W(0)` **diverges** | Use `φ⁻¹ ≈ 0.618`; same fixed point, now stable |
| `E = P·V·ln(P₂/P₁)/(γ-1)` | Dimensional check | Mixes isothermal and adiabatic — no such process | State one or the other; apply 60–73% RTE |
| `A = Π p_i·η·τ` | Numerical range | Underflows to 0 at M ≈ 300 → zeroes all of Ψ | Sum of logs |
| `Area_ratio = π(r_i²/r_j²)` | Cancel the terms | π cancels; off by 3.14159 | `r_i²/r_j²` |

### Cycle 3 — physical premises

| Hypothesis | Test | Result | Revised claim |
|---|---|---|---|
| AMOC collapses over 1–2 years | RAPID array, 2004–2023 | 1.0 Sv/decade — **inconsistent with mid-century collapse** | Decadal gradients; magnitude still contested |
| Microplastics are the target fraction | 2025 *Nature* survey | Nanoplastics are **~9× all larger debris** | Capture mechanisms don't transfer to nanoscale |
| Mycelium as structure | Compressive strength | ≥0.08 MPa vs 20–40 MPa concrete — **250–500× weaker** | Insulation-class; keep out of the load path |
| Rectenna at 97% | Read the test conditions | High input power only; ambient is **~32%** | Size against 32% |
| Ozone cascade premise is backwards | Read the module | **Falsified my own critique** — it models wildfire plumes correctly | Module left alone; one transfer function flagged |
| "Mycelial matrix = *Physarum*" | Taxonomy | Slime mould ≠ fungus; no structural strength | Choose deliberately per layer |

That fifth row matters as much as the others. A review that only ever confirms its own
first guess is not running the method either.

### Still unknown — the "search for unknowns" step

Open questions, ranked by how much rests on them. These are the next rerun.

1. **Reliability value is unquantified.** Every 99.95% figure in this repository is a
   target, never a measurement. It is also the largest *missing* benefit term, so the
   current benefit-cost ratio **understates** the project. Tool: LBNL ICE Calculator.
2. **HVAC or HVDC is undecided.** Converter stations are 30–40% of capex, which makes HVDC
   uneconomic below ~500–600 km. For 4,500 km of shorter segments this is decisive.
3. **The burial decision is unpriced.** Overhead costs $17B–$35B less. That is an argument
   to make, not an assumption to hold.
4. **Ozone degradation kinetics** use test data at 5–50× ambient concentration with no
   acceleration transfer function.
5. **Substation costs are assumed.** Replace with MISO MTEP figures.
6. **Efficiency and cost-reduction targets** (42%, 35%, 30%) have no stated baseline or
   method anywhere in the repository.
7. **`src/BioGridTechnicalImplementation.js` is truncated and does not parse.** The final
   statement is cut off mid-expression, leaving three unclosed braces. Verified identical
   at `fb07207`, so the damage is original rather than introduced. Whatever the lost tail
   contained is unrecoverable from this repository — reconstructing it would mean inventing
   content, so it has been flagged in-file instead. If the original exists elsewhere, that
   is the fix.

---

<a id="pre-2026-refresh"></a>

## `pre-2026-refresh/`

The ten documents modified by the 2026 review, as they stood at commit `fb07207`.
Directory structure mirrors the repository root.

| Archived file | What changed |
|---|---|
| `data/Economic-projections.md` | Rewritten. All figures re-derived from published benchmarks. |
| `docs/Economic_Impact.md` | Rewritten. $85B breakdown rebuilt; three return claims withdrawn. |
| `README.md` | Headline figures replaced with derived ranges. |
| `Technical-equations.md` | Two equations corrected — φ recursion, CAES expression. |
| `docs/Bio-hybrid-equations.md` | Two corrections — swarm product underflow, stray π. |
| `docs/Technical-feasibility.md` | Compute modernised H100 → GB200 NVL72; islanding tied to IEEE 2800a. |
| `AMOC/AMOC-transition.md` | Collapse premise reframed against the RAPID observational record. |
| `Waste-management/Microplastics.md` | Updated for nanoplastic dominance and engineered PET enzymes. |
| `Regional-bio-grid/Infrastructure/underground-bio-tunnel-specs.md` | *Physarum* distinguished from fungal mycelium; strength bounds added. |
| `docs/FEASIBILITY_SUMMARY.md` | Region scores marked unsourced; 15,000 km scope costed. |

---

<a id="obsolete"></a>

## `obsolete/`

Files **removed** from the repository. Unlike `pre-2026-refresh/`, these have no current
version anywhere.

| Archived file | Why it was removed |
|---|---|
| `docs/README_propaganda_version.md` | Unreferenced alternate README repeating five withdrawn claims verbatim, with no sign they had been retracted. |
| `src/components/Knowledge-nodes-import` | Broken scratch fragment, referenced nowhere. Not a valid module: `canvasRef` and `setKnowledgeNodes` undefined, and its import resolves to `src/components/api/feeds`, which does not exist. `AntSwarmKnowledge.jsx` already implements the wiring it sketched. |
| `src/config/Resilience-profiles` | Dead config. No extension so nothing could load it; referenced nowhere; three of its four keys appear in no source file. |

The markdown and JS-style files carry a banner. **`Resilience-profiles` does not** — it is
valid JSON and a banner would have broken it. It is byte-identical.

### Not archived — relocated instead

`src/src/hooks/useSwarmConfig.js` looked obsolete and was not. It is live code:
`src/Summary.md` documents importing it, and the file's own header declares its intended
path. The duplicated `src/` prefix was the bug. It was **moved** to
`src/hooks/useSwarmConfig.js`; archiving it would have broken the documented import.

---

## Fidelity

Archived files carry a banner marking them superseded. **That banner is the only
modification.** It exists because an unmarked copy of a withdrawn figure in the same
repository quietly undoes the correction — someone searching for "340% ROI" would find it in
full context with no indication it had been retracted.

Byte-exact originals, no banner:

```bash
git show fb07207:docs/Economic_Impact.md      # any pre-refresh file
git show 680c51d:docs/README_propaganda_version.md   # any obsolete file
git log --follow -p -- docs/Economic_Impact.md       # full history
```

## Adding to this record

When a claim in this repository fails a check:

1. **Do not delete it.** Move the prior state here, or mark it superseded in place.
2. **Record the test**, not just the verdict — the check has to be re-runnable.
3. **State the revised claim**, or say plainly that none is available yet.
4. **Add what you now don't know** to the unknowns list above. A falsification that
   surfaces no new question usually means the check was too shallow.
5. **Re-run** `python3 tools/derive_economics.py` if any cost input moved.
