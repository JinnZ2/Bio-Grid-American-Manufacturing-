# Self-Healing Network: Mycelium-Inspired Infrastructure Logic

> “When the system breaks, it doesn't stop. It regrows.”

BioGrid's self-healing mechanism is modeled after **mycelial networks** — underground fungal systems that repair, reroute, and grow in response to local stimuli without central control.

---

## Biological Inspiration

- **Mycelium** spreads by expanding filaments (hyphae) that explore and reinforce paths to nutrients.
- It responds to damage by rerouting around the injured zone.
- It thrives in **decentralized**, **redundant**, and **resilient** patterns — ideal for infrastructure.

---

## 🛠 Technical Mechanism

Each grid node (sensor, energy, data, or manufacturing) has a *health state*:

```text
[Healthy] → [Weakened] → [Isolated] → [Healed or Recycled]

Triggers for healing:
	•	Detected failure (signal loss, latency spike)
	•	Surrounding node activity remains high
	•	Decay threshold exceeded

Healing logic:
	1.	Mark failed node in a decayMap
	2.	Scan for adjacent viable nodes with open bandwidth or idle cycles
	3.	Attempt up to max_regrowth_attempts using signal gradient logic
	4.	Establish new path with reduced strength → reinforce if usage increases

⸻

 Core Parameters

Defined in config/parameters.json:

{
  "enable_mycelial_repair": true,
  "decay_threshold": 0.6,
  "max_regrowth_attempts": 5
}

Nodes also require a flag: "healable": true


###example

{
  "id": "sensor_42",
  "value": "Air Quality",
  "strength": 5,
  "healable": true
}###

If sensor_42 fails but is surrounded by active swarm paths and hits the decay threshold, it may regrow via neighbor relay.

⸻

🧠 Future Additions
	•	Signal visualization with animated hyphae trails
	•	Nutrient-mapping model for energy prioritization
	•	Regrowth costs to simulate real-world resource draw

⸻

BioGrid grows. It does not rebuild from scratch.
Like the forest floor, it forgets nothing and forgives slowly.
