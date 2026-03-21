#  Trust Model: BioGrid Swarm System

##  1. Assumptions

- Nodes may be compromised, misconfigured, or disconnected.
- Ant agents are not individually trusted, but trust emerges from swarm behavior.
- No single node has global knowledge or control.
- Mycelial repair logic can be gamed if not bounded.
- External inputs (sensor data, environmental readings) may be spoofed or delayed.

---

##  2. Trust Principles

| Principle | Description |
|----------|-------------|
| **Redundancy Over Authority** | No single node decides regrowth. Multiple agents must independently rediscover degraded nodes. |
| **Behavioral Consistency** | Nodes are observed over time. Sudden behavioral deviation is flagged, not trusted. |
| **Decay Resilience** | Decay maps are shared but not absolute. One node’s idea of failure isn't gospel. |
| **Memory Filtering** | Ant memory trails decay fast. This limits propagation of false paths or manipulated pheromone trails. |
| **Healable ≠ Trusted** | Nodes marked as `repairable` still require peer swarm verification to re-enter full use. |

---

##  3. Threat Scenarios

| Threat | Mitigation |
|--------|------------|
| Fake Sensor Data | SensorAdapter uses signal history and confidence decay |
| Compromised Node | Limits on regrowth rate; requires multiple swarm approvals |
| Rogue Agent (Ant) | No agent has global influence; memory length is short |
| Infinite Loop | Swarm refresh rate + global convergence halt triggers |
| External Overload | Nodes throttle pheromone emissions under stress |

---

##  4. Future Work

- Cryptographic agent IDs (🪪 swarm signatures)
- ZK proofs for knowledge acquisition
- Temporal decay for confidence scoring

---

##  TL;DR

You don’t trust the ants.  
You trust the swarm.  
And even then… only a little.
