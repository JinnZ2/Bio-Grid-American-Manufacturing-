# CLAUDE.md

Orientation for AI assistants working in this repository.

> Adapted from the `add-claude-documentation` branch. That branch also proposed a full
> directory reorganization which was **not** adopted — it forked before the
> `air-quality-cascade`, `materials-durability` and `contamination` modules existed and had
> no home for them. This file describes the structure that actually exists.

## What this repository is

A speculative open framework for decentralized infrastructure — energy, manufacturing,
waste, climate adaptation — built around bio-inspired distributed intelligence (ant colony
optimization, *Physarum* network routing, fungal composites).

It is a **design and analysis repository**, not a product. Most of it is documents and
models. The JavaScript under `src/` is a simulation and dashboard layer; the Python is
domain modelling.

## The one rule that matters

**Every quantitative claim resolves to [REFERENCES.md](REFERENCES.md), or is explicitly
labelled an assumption. There is no third category.**

"It appeared in an earlier document here" is not a source. That is precisely how a set of
unsupportable figures propagated through this repository until the 2026 review caught them.
Read [docs/SCIENCE_UPDATE_2026.md](docs/SCIENCE_UPDATE_2026.md) before touching any number.

Three distinctions that are never collapsed:

| Keep apart | Because |
|---|---|
| Lab record vs. field performance | Rectennas: 97% in a rig, ~32% on ambient power |
| Modelled vs. built | The 87%-efficient CAES system does not exist |
| Target vs. measurement | Every 99.95% figure here is a target; none is validated |

## Layout

```
REFERENCES.md            Sourced bibliography with DOIs — start here for any figure
CONTRIBUTING.md          The claim-handling loop
legacy/                  Falsification record — prior states, NOT current
  pre-2026-refresh/      Previous versions of documents that still exist
  obsolete/              Files removed outright
docs/                    Strategy, feasibility, risk, equations, blueprints
  SCIENCE_UPDATE_2026.md The evidence review and every correction it produced
  DESIGN_REVISION_2026.md What changes as a result, and the route to build it
data/                    Briefs, projections, cost_basis_2026.json, transition_basis_2026.json
tools/derive_economics.py    Reproducible cost model
tools/transition_pathways.py Leverage ranking + governance/financial transition
src/
  components/            React: AntSwarmKnowledge, LiveStatusPanel
  hooks/                 useSwarmConfig — loads config/parameters.json
  logic/                 mycelialGrowth, archetypeRedundancy
  technical/             blueprint-core, mycelial-network, system-integration
  api/ adapters/         Data feeds and sensor adapters
  air-quality-cascade/   Python: wildfire-plume ozone → material degradation
  materials-durability/  Python: 18 archetypes, degradation, renewal
  contamination/         Python: contamination sim + hotspot scanner
  __tests__/             Jest suites
AMOC/ Desertification/ Waste-management/ Energy/
Electromagnetic-energy-harvesting/ Regional-bio-grid/    Domain documents
```

## Commands

```bash
npm ci                  # install
npm test                # jest — 62 tests, 10 suites
npm run lint            # eslint
npm run format:check    # prettier (CI enforces this)
npm run report          # node bin/generate_report.js

python3 tools/derive_economics.py                    # rebuild the economics
python3 tools/transition_pathways.py                 # ranked design changes + transition
python3 tools/transition_pathways.py --sensitivity   # do the rankings survive?
python3 Waste-management/test_eta_sensitivity.py     # python model tests
```

CI runs tests, lint and format on Node 18 and 20, plus the Python model tests.

## Known-broken files

Two files do not parse and are excluded from lint and formatting. Both were damaged before
the 2026 review; neither is a regression.

- **`src/BioGridTechnicalImplementation.js`** — truncated mid-expression, unclosed braces.
  The lost tail is unrecoverable from this repository. Treat it as a specification document
  that happens to use JavaScript syntax. Nothing imports it, and nothing can.
- **`src/Recovery-blowback-mitigation.md`** — was `.js`, but it is markdown: prose, one
  fenced ```javascript block, prose. Renamed in 2026 to match its actual content.

## Working here

- **Costs live in `data/cost_basis_2026.json`, not in prose.** Edit the parameter, re-run
  `tools/derive_economics.py`, update the documents from its output.
- **`legacy/` is append-only in spirit.** When a claim fails a check, move its prior state
  there or mark it superseded in place — with the test that decided it. Do not delete it.
- **Don't restore withdrawn figures.** If you find `340% ROI`, `$85B annual impact`,
  `275k jobs`, `500 H100 GPUs` or a `1–2 year AMOC collapse` outside a supersession block,
  that is a regression.
- **Design changes go through `transition_pathways.py`.** Add the modification to
  `data/transition_basis_2026.json` with its cost, lead time, consenting parties and
  reversibility, then re-run. A change that cannot be scored is a change nobody can rank.
- **φ applies to geometry, φ⁻¹ to decay.** Applying φ = 1.618 to a recursion makes it
  diverge; that was a real bug in `Technical-equations.md`.
- **Prefer editing in place with a marked correction** over silent rewriting. The audit
  trail is the point.

## The check worth running first

Before reaching for better data, divide any claimed benefit by the size of the market it
must come from. Three of this project's headline economic claims failed that by more than
an order of magnitude — the constraint was the market, not the technology.

It costs one division.
