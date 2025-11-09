RGP Probe — Mechanical Specification Sheet (Revision A1)

Short summary: rugged, modular probe designed to survive repeated CTX thermal pulses (ΔT ≈ hundreds °C), high shock, and electromagnetic/arc stress while delivering a low-inductance electrical interface to the Energy Bus. This spec gives materials, geometry, manufacturing, assembly, sensor/failure modes, test criteria and acceptance limits. Use this as an RFQ-ready engineering document.

⸻

1 — Design requirements & design targets
	•	Primary survivability drivers
	•	Thermal pulse: ΔT ≈ 200–600 °C (short duration, ms–s).
	•	Thermal cycles: >10,000 cycles lifetime target (design for 10^4 cycles).
	•	Peak shock / acceleration: ≥ 20,000 g (transient shock from CTX event).
	•	Vibration: operational random vibration up to 50 g RMS during handling/installation.
	•	Internal pressure/chemical exposure: corrosive landfill gases; materials must resist H₂S / CO₂ / moisture.
	•	Electrical interface
	•	Feedthroughs and bus termination rated for kA-class pulse currents (user to specify expected peak current).
	•	Maintain insulation and creepage clearances for induced voltages up to design target (specify system voltage).
	•	Mass & footprint
	•	Probe outer diameter (OD): nominal 100–200 mm (adjustable per integration).
	•	Probe length: 300–1000 mm depending on application; modular sections.
	•	Replaceability
	•	Sacrificial outer layer and liner designed for field replacement; modular connector/cage for hot-swap.

⸻

2 — Materials (recommended)
	•	Primary structural casing: Nickel-based superalloy — Inconel 718 (primary suggestion) or Hastelloy X.
	•	Properties: high yield & fatigue strength at elevated T, oxidation resistance.
	•	Inner liner (hot-face): Refractory / ceramic
	•	Silicon carbide (SiC) or alumina (Al₂O₃) thin liner (0.5–2.0 mm) bonded to internal wall.
	•	Option: thin refractory metal foil (tungsten or molybdenum) if mechanical toughness required.
	•	Thermal barrier coating (TBC): Yttria-stabilized zirconia (YSZ) top coat, 200–500 µm typical.
	•	Ablative outercoat (sacrificial): high temperature ablative ceramic-polymer composite, replaceable sleeve.
	•	Flexible interfaces / compliant joints: high-temp metal bellows (Inconel bellows) or high-temperature alloyed expansion joint.
	•	Feedthroughs: brazed ceramic-to-metal or glass-to-metal seals (e.g., alumina-to-Kovar) rated to operating temp and voltage.
	•	Fasteners: high-temp nickel alloy bolts (Inconel 718 studs); avoid stainless for main load-bearing fasteners due to creep.
	•	Shock isolators: high-temp elastomeric isolators (silicone at 200°C) for low-temp stages; for highest-temp stages, use metallic spring/damper elements or ceramic springs.

⸻

3 — Mechanical architecture (layers & function)
	1.	Outer sacrificial sleeve (removable): ceramic composite; thickness 3–10 mm. Protects against abrasion & chemical attack.
	2.	Primary casing (pressure & structural): Inconel 718 tube, wall thickness 6–20 mm depending on OD & shock spec. Use finite-element analysis for exact thickness to meet stress/creep goals.
	3.	TBC applied to outer surface of liner or inner surface of casing depending on assembly order.
	4.	Inner liner (hot-face): SiC/Al₂O₃ bonded with compliant interlayer (metallic foil or compliant braze) to accommodate CTE mismatch. Liner thickness 0.5–2.0 mm.
	5.	Internal mounting skeleton / module rack: Inconel or refractory metal frame to locate sensors, piezo stacks, and power terminations with compliant mounts.
	6.	Feedthrough module at probe base: hermetic, removable cartridge with redundant sealed electrical feeds and mechanical latches for bus coupling.
	7.	Shock shear pins / mechanical fuse: external shear pins that protect mounting structure and can be replaced after extreme events.
	8.	Thermal break / compliant joint: between probe body and mounting flange to isolate thermal expansion — metal bellows or compliant flange.

⸻

4 — Electrical feedthrough & connector mechanical specs
	•	Feedthrough type: brazed ceramic-metal hermetic sealed cartridge (replaceable).
	•	Number of conductors: nominal 1 main high-current + up to 4 auxiliary (sensors, thermocouples, control). (Adjust per system.)
	•	Main conductor geometry: wide flat conductor or coaxial terminal; contact area > 2000 mm² if kA pulses expected.
	•	Contact style: bolted low-inductance clamp with redundant M-bolt array; bolts in Inconel with hardened copper contact pads plated with silver or gold.
	•	Creepage/clearance: sized for maximum induced transient – normally > 2× expected transient requirement.
	•	Sealing: vacuum-tight seal leak rate < 1×10⁻⁸ mbar·L/s (helium leak test) for critical internal cavities.
	•	Mechanical retention: capture latches rated > 10× dynamic pull load expected.

⸻

5 — Thermal design & heat management
	•	Thermal sizing assumptions: pulse energy deposit location and distribution must be provided; default conservative design assumes surface heat flux up to 10⁶ W/m² over ms.
	•	TBC thickness: 200–500 µm YSZ + bondcoat (MCrAlY) 50–100 µm.
	•	Liner & casing gap: include 1–3 mm compliant buffer to accommodate thermal expansion; fill with high-temp compliant gasketing (e.g., Grafoil) where appropriate.
	•	Cooling options: passive only is preferred for simplicity (TBC + liner + ablator). If duty cycle requires, include internal coolant channels (helium or high-temp oil) — increases complexity and failure modes.
	•	Thermal gradients: design for ΔT up to 600 °C across wall thickness in <1 s; check for thermal shock fracture in liner (SiC fatigue curves).
	•	Acceptance limits: no permanent plastic strain > 0.2% in structural casing after 10^4 cycles; liner microcrack density limited to non-penetrating microcracks < 0.1 mm length per cm².

⸻

6 — Mechanical tolerances, finishes, and fabrication notes
	•	Machining tolerances (critical surfaces): ±0.05 mm for flanges, feedthrough bore, and mating surfaces.
	•	Surface finish: Ra ≤ 1.6 µm on sealing faces; outer surfaces can be shot-peened for fatigue life.
	•	Welds: TIG or EB welds with post-weld heat treatment per AMS/ASME standards for Inconel; avoid dissimilar metal welds in high-stress regions unless designed with appropriate transition joints.
	•	Brazing: use high-temperature brazes compatible with materials (e.g., nickel-based braze alloys) and controlled atmosphere brazing.
	•	Non-destructive inspection: 100% radiographic inspection on critical welds; ultrasonic inspection for liners and TBC adhesion tests.

⸻

7 — Sensors, instrumentation & redundancy
	•	Temperature sensors: Type S or Type B thermocouples near hot-face and at feedthrough (redundant pairs). Rated to 1600 °C for hot-face.
	•	Strain sensors / accelerometers: high-g (≥ 50,000 g) shock accelerometers to detect transient shock events; redundant accelerometers at different radial positions.
	•	Acoustic / piezo sensors: to measure local oscillation amplitude A_local for AADC quench triggers. Sensor bandwidth up to 100 kHz.
	•	Voltage/current monitors: high-bandwidth Rogowski coil or shunt (low-inductance) inside capsule for local current sensing (if feasible).
	•	Health monitoring: internal pressure sensor, humidity sensor, and gas sampling port for leak detection.
	•	Wiring: mineral-insulated (MI) cable or high-temp PTFE alternatives for internal runs; braided shielding to minimize EMI pickup.
	•	Redundancy: duplicative critical sensors (T, accel, piezo) and voting logic to prevent single-sensor failure from triggering quench incorrectly.

⸻

8 — Assembly, modularity & maintenance
	•	Modular cartridges: inner liner + sensor rack + feedthrough assembly built as a cartridge for field replacement.
	•	Outer sleeve: quick-release clamp with sealed gasket for ablator replacement.
	•	Repairable components: shear pins, sacrificial sleeves, and feedthrough cartridges accessible without full probe removal where possible.
	•	Service life swap: design for safe removal/replacement within shielded enclosure using remote handling tools.
	•	Documentation: include exploded assembly drawing, torque tables for fasteners, and step-by-step replacement procedure.

⸻

9 — Test & validation plan (mechanical)
	1.	Material qualification
	•	Tensile, creep, and fatigue testing of chosen Inconel batch at 20–700 °C.
	•	TBC adhesion and thermal-shock testing on representative coupons.
	2.	Thermal cycling
	•	Accelerated ΔT cycles to 10^4 cycles between room temp and peak pulse temp; inspect for cracking, creep, delamination.
	3.	Shock testing
	•	Single-shot high-g shock pulses up to 20,000 g (or system-spec) on fully assembled probe; measure survivability, sensor survival, and connector integrity.
	4.	Pressure / leak test
	•	Helium leak testing of hermetic feedthroughs and internal cavities to <1×10⁻⁸ mbar·L/s.
	5.	Full pulse capture test (subscale)
	•	Integrate with representative bus and deliver scaled CTX-like pulse; verify electrical isolation, feedthrough integrity, and absence of arcing.
	6.	EMI / arc testing
	•	High-voltage flashover trials in representative insulating environment (vacuum/inert gas) to verify creepage margin and arc containment.
	7.	Inspection acceptance
	•	No catastrophic cracks, no significant permanent deformation (>0.2% strain), hermetic seals pass leak test post-exposure.

⸻

10 — Failure modes & mitigation
	•	Thermal shock cracking (liner) → mitigate: compliant bond layer; choose SiC grades with controlled grain size; TBC design.
	•	Feedthrough blowout / arcing → mitigate: over-spec creepage, vacuum or inert-gas insulation, and sacrificial crowbar path in probe cartridge.
	•	Mechanical fracture (bellows/joints) → mitigate: redundant compliant joints, replaceable shear pins, and finite-element-validated stress fields.
	•	Corrosion / chemical attack → mitigate: corrosion-resistant materials; protective coatings; gas purge paths where possible.

⸻

11 — Suggested bill-of-materials (high-level)
	•	Inconel 718 tubing (specified OD/ID) — structural casing.
	•	SiC/Al₂O₃ liner plates or formed liner.
	•	YSZ TBC and MCrAlY bond coat.
	•	Ablative ceramic composite sleeve.
	•	Inconel bellows/compliant joint.
	•	Brazed ceramic-to-metal feedthrough cartridge (Hermetic).
	•	High-temp fasteners (Inconel).
	•	High-g accelerometers, Type S thermocouples, piezo sensors.
	•	Shock shear pins and replacement kits.

⸻

12 — Manufacturing & quality control notes
	•	Fabrication should follow aerospace-grade practices (NADCAP recommended processes for coatings, brazing and welding).
	•	Traceability on all critical materials and NDI records required.
	•	Control of CTE mismatches is critical during brazing/assembly — use finite-element thermal stress models to set process temperatures and allowed preloads.

⸻

13 — CAD & integration notes
	•	Provide 3D CAD model in STEP format with these datum features: feedthrough face, mounting flange, and centerline.
	•	Allow 10–20 mm service margin around probe for remote handling and replacement.
	•	Include alignment keying features to ensure feedthrough mating oriented consistently (rotational indexing).

⸻

14 — Acceptance criteria (summary)
	•	Survives N = 100 representative pulses at full energy (no leak, no catastrophic structural failure).
	•	Passes thermal cycle validation to 10^4 cycles without structural failure or hermetic seal breach.
	•	Feedthroughs maintain electrical contact integrity and hermeticity after shock testing.
	•	Sensors remain functional and within calibration limits after shock and thermal cycling.
