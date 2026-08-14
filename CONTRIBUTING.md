# 🧪 Contributing to BioGrid 2.0

Pull requests welcome. Please:

- Stick to MIT-compatible components
- Don't introduce proprietary services
- Keep commit messages useful
- Respect swarm behavior constraints

Ask questions in Discussions first if unsure.

---

## How claims work here

This repository runs a loop, and contributions are expected to run it too:

```
hypothesize → run → result falsified → edit claim → search for unknowns → rerun
```

A falsified claim is not an embarrassment to be deleted. It is a result. The record of
what was tried, what failed and which check caught it lives in
[`legacy/`](legacy/README.md), and it stays there because **precedence carries** — the next
person needs to know which ground has already been walked.

### If you add a number

**Source it or label it.** Every quantitative claim either resolves to an entry in
[REFERENCES.md](REFERENCES.md) or is explicitly marked an assumption. There is no third
category, and "it appeared in an earlier document here" is not a source — that is how the
withdrawn figures propagated in the first place.

Three distinctions this repository keeps, because collapsing them is how good numbers go
bad:

| Keep apart | Why |
|---|---|
| Laboratory record vs. field performance | Rectennas hit 97% in a rig and ~32% on ambient power |
| Modelled vs. built | The 87%-efficient CAES system does not exist |
| Target vs. measurement | Every 99.95% figure here is a target; none has been validated |

State units, especially for employment. "125,000 jobs" is defensible as job-years and
misleading as simultaneous headcount, and the difference is a factor of three.

### If you change a cost

Costs live in [`data/cost_basis_2026.json`](data/cost_basis_2026.json), not in prose. Edit
the parameter, then:

```bash
python3 tools/derive_economics.py
```

Update the affected documents from its output. Lazard, BNEF, EIA STEO and the NREL ATB all
publish annually, so this will drift — refreshing it is a data edit and a script run, not a
rewrite.

### If you falsify something

Good. That is the loop working. Then:

1. **Don't delete the old claim.** Move its prior state to `legacy/`, or mark it superseded
   in place with the original still visible.
2. **Record the test**, not just the verdict. It has to be re-runnable by someone who
   disagrees with you.
3. **State the revised claim** — or say plainly that none is available yet.
4. **Add what you now don't know** to the unknowns list in
   [`legacy/README.md`](legacy/README.md). A falsification that raises no new question
   usually means the check was too shallow.

### The cheapest useful check

Before reaching for better data, divide the claimed benefit by the size of the market it
must come from. Three of this project's headline economic claims failed that test by more
than an order of magnitude — no amount of technical performance could have rescued them,
because the constraint was the market, not the system.

It costs one division. Run it first.
