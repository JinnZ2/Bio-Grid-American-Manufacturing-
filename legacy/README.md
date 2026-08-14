# Legacy

Superseded versions of documents, kept for provenance.

**Nothing in this folder should be cited.** These files contain the figures the August 2026
review found unsupportable. They are preserved so the corrections are auditable — so a
reader can see what was claimed, what replaced it, and why — not because the content is
still usable.

If you want a current number, start at [REFERENCES.md](../REFERENCES.md).
If you want to know why a number changed, read
[docs/SCIENCE_UPDATE_2026.md](../docs/SCIENCE_UPDATE_2026.md).

---

## `pre-2026-refresh/`

The ten documents modified by the 2026 science refresh, as they stood at commit
`fb07207` — the last commit before the review. Directory structure mirrors the repository
root, so `pre-2026-refresh/docs/Economic_Impact.md` is the old version of
`docs/Economic_Impact.md`.

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

### The claims withdrawn

Kept here in one place, because these are the ones most likely to be quoted from an old
copy still circulating elsewhere:

| Withdrawn claim | Why |
|---|---|
| $12B/yr energy cost savings | 69% of the entire regional electricity bill ($17.3B/yr) |
| 340% ROI over 15 years | Implies $19.3B/yr — 111% of that bill |
| 4.2-year payback | Implies $20.2B/yr — 117% of that bill |
| 150,000 permanent jobs | Grid operations account for ~0.5%; 410–1,050 FTE derived |
| $150B/yr exports by 2040 | No derivation exists; retained elsewhere as an aspiration only |
| $8B for 500 H100 GPUs | Budget and specification differ by ~240× |
| 500 H100 GPUs | Superseded hardware; 7 × GB200 NVL72 is the current equivalent |
| 1–2 year AMOC collapse | RAPID observes 1.0 Sv/decade; not consistent with mid-century collapse |
| `W(t+1) = φ·W(t) + ΔL·(1-φ)` | Diverges. φ > 1. Corrected to use 1/φ ≈ 0.618 |

### A note on fidelity

Each archived file carries a banner at the top marking it as superseded. **That banner is
the only modification.** The banner exists because an unmarked copy of a withdrawn figure
in the same repository would quietly undo the correction — someone searching for "340% ROI"
would find it, in context, with no indication it had been retracted.

For a byte-exact original with no banner:

```bash
git show fb07207:docs/Economic_Impact.md
```

Full history for any file:

```bash
git log --follow -p -- docs/Economic_Impact.md
```
