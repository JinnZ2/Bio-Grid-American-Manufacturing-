# Repository Reorganization Plan

## Goals
- Reduce root clutter (currently 10+ top-level directories)
- Group domain research under one parent
- Fix files with missing/wrong extensions
- Fix nested `src/src/` directory bug
- Move Python models to dedicated directory
- Organize docs into clear subcategories
- Move markdown "data" files to docs where they belong
- Move `technical/` JS modules into `src/` (they're imported by `bin/generate_report.js`)
- Update README repo structure diagram
- Update CLAUDE.md repo structure
- Keep all imports/tests working

## New Structure

```
Bio-Grid-American-Manufacturing-/
├── .github/workflows/ci.yml
├── .eslintrc.json, .prettierrc.json, .gitignore, babel.config.json
├── package.json, package-lock.json
├── LICENSE, CONTRIBUTING.md, CLAUDE.md, README.md
├── Meta-README.md, BioGrid_Ontology.json
│
├── src/                              # Application code
│   ├── components/
│   │   ├── AntSwarmKnowledge.jsx
│   │   ├── LiveStatusPanel.jsx
│   │   └── KnowledgeNodesImport.js       # renamed (had no extension)
│   ├── logic/
│   │   └── mycelialGrowth.js
│   ├── adapters/
│   │   └── sensorAdapter.js
│   ├── api/
│   │   └── feeds.js
│   ├── hooks/
│   │   └── useSwarmConfig.js             # fixed from src/src/hooks/
│   ├── config/
│   │   ├── parameters.json
│   │   ├── knowledge_nodes.json
│   │   ├── geo_map.json
│   │   └── resilience-profiles.json      # renamed (had no extension)
│   ├── technical/                        # moved from root technical/
│   │   ├── blueprint-core.js
│   │   ├── mycelial-network.js
│   │   └── system-integration.js
│   └── __tests__/
│       ├── mycelialGrowth.test.js
│       ├── feeds.test.js
│       └── sensorAdapter.test.js
│
├── docs/
│   ├── architecture/                     # Technical specs & equations
│   │   ├── technical-equations.md            # from root
│   │   ├── bio-hybrid-equations.md
│   │   ├── 3d-energy-city-equations.md
│   │   ├── 3d-energy-city-implementation.md
│   │   ├── technical-implementation.md       # from src/BioGridTechnicalImplementation.js
│   │   ├── recovery-mitigation.md            # from src/Recovery-blowback-mitigation.js
│   │   ├── self-healing-network.md
│   │   └── trust-model.md
│   ├── strategy/                         # Planning & roadmap
│   │   ├── implementation-timeline.md
│   │   ├── northwoods-bridge-strategy.md
│   │   ├── northwoods-specs.md               # from data/
│   │   ├── political-coalition-strategy.md
│   │   ├── international-export-strategy.md
│   │   ├── roadmap.md
│   │   └── how-to-deploy.md                  # from root
│   ├── feasibility/                      # All feasibility analysis
│   │   ├── feasibility-summary.md
│   │   ├── duluth-superior-feasibility.md
│   │   ├── regional-feasibility.md
│   │   ├── superior-michigan-expansion.md
│   │   ├── technical-feasibility.md
│   │   └── economic-impact.md
│   ├── risk/                             # Risk assessment
│   │   ├── strategic-risk-factors.md
│   │   └── risk-assessment.md
│   ├── reference/                        # Reference & summaries
│   │   ├── use-cases.md                      # from root
│   │   ├── summary.md                        # from src/Summary.md
│   │   ├── core-brief.md                     # from data/
│   │   ├── economic-projections.md           # from data/
│   │   ├── manufacturing-specs.md            # from data/
│   │   ├── tech-implementation-summary.md    # from data/
│   │   ├── implementation-matrix.yaml
│   │   ├── propaganda-readme.md
│   │   └── full-hex.md
│   └── blueprint/                        # Compressed/seed docs
│       ├── reconstruction.md
│       ├── seed-parser.md
│       ├── ultra-compressed.md
│       └── universal-problem-solving.md
│
├── domains/                              # All domain research
│   ├── amoc/                                 # from AMOC/
│   ├── desertification/                      # from Desertification/
│   ├── electromagnetic-energy/               # from Electromagnetic-energy-harvesting/
│   ├── energy/                               # from Energy/
│   ├── waste-management/                     # from Waste-management/
│   └── regional/                             # from Regional-bio-grid/
│       ├── infrastructure/
│       ├── manufacturing/
│       ├── dual-system/
│       └── feasibility-overview.md
│
├── models/                               # Python simulations
│   ├── ant-colony-model.py                   # from docs/
│   ├── rural-first-expansion.py              # from docs/
│   └── eta-sensitivity.py                    # from Waste-management/
│
├── bin/
│   └── generate_report.js                    # update imports
│
├── public/
│   ├── dashboard.html
│   └── data/sensors.json
│
└── data/                                 # Actual data files only
    (empty after moving markdown docs out)
```

## File Moves Summary

### Root → docs/
- `Technical-equations.md` → `docs/architecture/technical-equations.md`
- `Use-cases.md` → `docs/reference/use-cases.md`
- `HOW_TO_DEPLOY-small.md` → `docs/strategy/how-to-deploy.md`

### Root domain dirs → domains/
- `AMOC/` → `domains/amoc/`
- `Desertification/` → `domains/desertification/`
- `Electromagnetic-energy-harvesting/` → `domains/electromagnetic-energy/`
- `Energy/` → `domains/energy/`
- `Waste-management/` → `domains/waste-management/` (minus .py file)
- `Regional-bio-grid/` → `domains/regional/`

### src/ cleanup
- `src/BioGridTechnicalImplementation.js` → `docs/architecture/technical-implementation.md`
- `src/Recovery-blowback-mitigation.js` → `docs/architecture/recovery-mitigation.md`
- `src/Summary.md` → `docs/reference/summary.md`
- `src/components/Knowledge-nodes-import` → `src/components/KnowledgeNodesImport.js`
- `src/config/Resilience-profiles` → `src/config/resilience-profiles.json`
- `src/src/hooks/` → `src/hooks/` (fix nested src)

### technical/ → src/technical/
- `technical/blueprint-core.js` → `src/technical/blueprint-core.js`
- `technical/mycelial-network.js` → `src/technical/mycelial-network.js`
- `technical/system-integration.js` → `src/technical/system-integration.js`

### data/ markdown → docs/
- `data/core_brief.md` → `docs/reference/core-brief.md`
- `data/Economic-projections.md` → `docs/reference/economic-projections.md`
- `data/manufacturing.md` → `docs/reference/manufacturing-specs.md`
- `data/northwoods_specs.md` → `docs/strategy/northwoods-specs.md`
- `data/tech_implementation.md` → `docs/reference/tech-implementation-summary.md`

### docs/ reorganize into subdirs
- `docs/Bio-hybrid-equations.md` → `docs/architecture/bio-hybrid-equations.md`
- `docs/3D_Energy_City_Equations.md` → `docs/architecture/3d-energy-city-equations.md`
- `docs/3D_Energy_City_Volumetric_Implementation.md` → `docs/architecture/3d-energy-city-implementation.md`
- `docs/self_healing_network.md` → `docs/architecture/self-healing-network.md`
- `docs/trust_model.md` → `docs/architecture/trust-model.md`
- `docs/Implementation_Timeline.md` → `docs/strategy/implementation-timeline.md`
- `docs/Northwoods_Bridge_Strategy.md` → `docs/strategy/northwoods-bridge-strategy.md`
- `docs/Political_Coalition_Strategy.md` → `docs/strategy/political-coalition-strategy.md`
- `docs/International_Export_Strategy.md` → `docs/strategy/international-export-strategy.md`
- `docs/roadmap.md` → `docs/strategy/roadmap.md`
- `docs/FEASIBILITY_SUMMARY.md` → `docs/feasibility/feasibility-summary.md`
- `docs/Duluth-superior-feasibility.md` → `docs/feasibility/duluth-superior-feasibility.md`
- `docs/regional_feasibility.md` → `docs/feasibility/regional-feasibility.md`
- `docs/Superior-Michigan-expansion.md` → `docs/feasibility/superior-michigan-expansion.md`
- `docs/Technical-feasibility.md` → `docs/feasibility/technical-feasibility.md`
- `docs/Economic_Impact.md` → `docs/feasibility/economic-impact.md`
- `docs/Strategic-risk-factors.md` → `docs/risk/strategic-risk-factors.md`
- `docs/risk_assessment.md` → `docs/risk/risk-assessment.md`
- `docs/implementation_matrix.yaml` → `docs/reference/implementation-matrix.yaml`
- `docs/README_propaganda_version.md` → `docs/reference/propaganda-readme.md`
- `docs/FullHex.md` → `docs/reference/full-hex.md`
- `docs/Blueprint/*` → `docs/blueprint/*` (lowercase)

### Python models → models/
- `docs/Ant-colony-model.py` → `models/ant-colony-model.py`
- `docs/Rural-first-expansion.py` → `models/rural-first-expansion.py`
- `Waste-management/eta_sensitivity.py` → `models/eta-sensitivity.py`

## Files to Update
1. `bin/generate_report.js` — fix imports from `../technical/` → `../src/technical/`
2. `README.md` — rewrite repo structure section
3. `CLAUDE.md` — rewrite repo structure section
4. `src/__tests__/mycelialGrowth.test.js` — verify import paths still work

## What Stays at Root
- `README.md`, `Meta-README.md`, `CLAUDE.md`, `CONTRIBUTING.md`, `LICENSE`
- `BioGrid_Ontology.json` (referenced externally, CC0)
- All config files (.eslintrc.json, .prettierrc.json, babel.config.json, package.json, etc.)

## Risks
- `bin/generate_report.js` imports from `technical/` — needs path update
- Test import paths reference `../src/logic/` — these should still work since tests are under `src/__tests__/`
- The spec-style `.js` files being moved to `.md` won't be linted/formatted anymore (that's a feature, not a bug)
