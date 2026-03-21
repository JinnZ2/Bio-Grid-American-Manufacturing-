# CLAUDE.md

## Project Overview

BioGrid 2.0 is a decentralized infrastructure framework for relaunching American manufacturing through distributed intelligence inspired by biological systems (ant colonies, mycelial networks, neural architectures). It targets the Great Lakes region (Minnesota-Wisconsin-Upper Michigan) with a phased deployment from 2025-2040.

**License:** MIT (keep all contributions MIT-compatible, no proprietary services)

## Repository Structure

```
src/
  components/         # React components (AntSwarmKnowledge.jsx, LiveStatusPanel.jsx)
  logic/              # Core algorithms (mycelialGrowth.js - self-healing network regrowth)
  adapters/           # Data integration (sensorAdapter.js)
  api/                # Data feeds with fallback strategies (feeds.js)
  config/             # JSON/YAML configuration (parameters.json, knowledge_nodes.json, geo_map.json)
  __tests__/          # Jest unit tests
  BioGridTechnicalImplementation.js   # Main implementation class
  Recovery-blowback-mitigation.js     # Recovery mechanisms
docs/                 # Technical documentation, timelines, Python models
Regional-bio-grid/    # Regional implementation specs (Infrastructure/, Manufacturing/)
Energy/               # Energy domain specs
data/                 # Compressed data, specs, physarum-network-optimizer.js
bin/                  # Build/utility scripts (generate_report.js)
public/               # Static assets (dashboard.html)
BioGrid_Ontology.json # Machine-readable ontology (CC0)
```

## Tech Stack

- **Frontend:** React, Canvas API, Lucide-react icons
- **Language:** JavaScript ES6+ (Node.js)
- **Testing:** Jest
- **Modeling:** Python (ant colony models, sensitivity analysis)
- **Data formats:** JSON, YAML, Markdown

## Common Commands

```bash
# Run tests
npx jest

# Run a specific test
npx jest src/__tests__/mycelialGrowth.test.js

# Generate report
node bin/generate_report.js
```

## Code Conventions

- **Components:** PascalCase filenames (e.g., `AntSwarmKnowledge.jsx`)
- **Functions/variables:** camelCase
- **Logic modules:** camelCase filenames (e.g., `mycelialGrowth.js`)
- **Fallback patterns:** All external data sources must have cascading fallback strategies
- **Self-healing:** Network components should implement regrowth/recovery mechanisms
- No linter or formatter is configured; follow existing code style

## Key Configuration

Swarm parameters live in `src/config/parameters.json`:
- `num_ants`: 75 (range 50-100+)
- `discovery_radius`: 30
- `pheromone_strength`: 0.5 / `pheromone_decay`: 0.01
- `swarm_refresh_rate`: 100ms
- `ant_roles`: scout, worker, forager

Knowledge landscape defined in `src/config/knowledge_nodes.json` (6 core nodes).

## Architecture Patterns

- **Swarm Intelligence:** Ant colony optimization for routing and resource allocation
- **Mycelial Networks:** Self-healing link regrowth when nodes fail
- **Distributed Agents:** Edge nodes with localized intelligence (ESP32, Raspberry Pi)
- **Pheromone-Based Routing:** Virtual pheromone trails for path optimization
- **Golden Ratio (PHI):** Neural control optimization constant

## Testing

Tests are in `src/__tests__/` using Jest. Current coverage includes:
- Mycelial regrowth link generation
- Viable neighbor filtering
- Null/undefined input fallback behavior

When adding new logic modules, add corresponding tests in `src/__tests__/`.

## Contributing Guidelines

From `CONTRIBUTING.md`:
- Pull requests welcome
- Keep all components MIT-compatible
- No proprietary services
- Write useful commit messages
- Respect swarm behavior constraints
- Ask questions in Discussions first

## Key Documentation (Reading Order)

1. `README.md` - Project overview and vision
2. `Meta-README.md` - Design philosophy
3. `docs/Implementation_Timeline.md` - 2025-2040 deployment roadmap
4. `docs/Northwoods_Bridge_Strategy.md` - Pilot implementation
5. `BioGrid_Ontology.json` - Conceptual framework
6. `Technical-equations.md` - Mathematical foundations
7. `docs/implementation_matrix.yaml` - System dependencies

## Deployment

No CI/CD pipeline configured. Deployment is phased:
- **Phase 1 (2025):** Duluth-Superior pilot, 10 edge nodes
- **Phase 2 (2026-2027):** 20 additional nodes, 500km infrastructure
- **Phase 3 (2027-2030):** Full mesh (55 nodes), 2500km infrastructure

Target hardware: ESP32/Raspberry Pi (edge), GPU clusters (central), fiber-optic/5G/RF mesh (networking).
