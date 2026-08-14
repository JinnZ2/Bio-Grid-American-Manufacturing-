BioGrid 3D Energy System – Core Technical Equations

Welcome, seeker of formulas. These equations define the flow, storage, conversion, and optimization mechanisms inside the BioGrid system. May your whiteboard never be blank again.

> **Reviewed August 2026.** Two equations on this page contained mechanical errors and have
> been corrected: the phi self-repair recursion diverged rather than converged, and the CAES
> expression combined isothermal and adiabatic terms. Both corrections are derived in
> [docs/SCIENCE_UPDATE_2026.md §11](docs/SCIENCE_UPDATE_2026.md#11-equation-corrections).
> Sources for all performance figures are in [REFERENCES.md](REFERENCES.md).

Energy Capture

Helical Wind Collector Output: P = 0.5 × ρ × A × Cp × v³

•	P = power (W)
	•	ρ = air density (kg/m³)
	•	A = swept area of helical rotor (m²)
	•	Cp = power coefficient
	•	v = wind velocity (m/s)

**On Cp.** The Betz limit caps any wind turbine at Cp = 16/27 ≈ 0.593 — no geometry
exceeds it. Helical vertical-axis rotors typically underperform horizontal-axis turbines,
so the 0.35–0.5 range previously stated here is optimistic at its upper end. Treat 0.35 as
a planning ceiling for helical designs until a specific rotor is characterised.

**Reality check.** The 2025 U.S. annual average wind capacity factor was 34.2%
(`eia_capacity_factors_2025`). Any siting model producing a materially higher figure is
describing an exceptional site, not a typical one.


Solar Skin Efficiency: E_total = η × I × A × t

	•	E_total = total energy generated (Wh)
	•	η = solar conversion efficiency (decimal)
	•	I = plane-of-array irradiance (W/m²)
	•	A = total panel area (m²)
	•	t = time exposed (h)

**This is an upper bound, not an output.** Real generation requires derates for cell
temperature coefficient, soiling, shading, mismatch and inverter efficiency. The 2025 U.S.
utility-scale solar capacity factor was 24.4% (`eia_capacity_factors_2025`) — use that to
sanity-check any annual energy estimate.

**On η.** Perovskite–silicon tandems reached 34.85% NREL-certified in April 2025, but
commercial tandem modules ship at 24.5% (`perovskite_record`). Silicon modules at 22–23%
remain the correct planning assumption; record-cell efficiencies are not purchasable.


Storage & Conversion

Compressed Air Energy Storage (CAES)

The expression previously given here — `E_air = P × V × ln(P2/P1) / (γ - 1)` — combined the
isothermal work integral `ln(P₂/P₁)` with the adiabatic factor `1/(γ-1)`. That describes no
physical process. State whichever process is intended:

	Isothermal:  E = P₁V₁ × ln(P₂/P₁)
	Adiabatic:   E = (P₁V₁)/(γ-1) × [(P₂/P₁)^((γ-1)/γ) - 1]

	•	E = stored energy (J)
	•	P₁, V₁ = initial pressure (Pa) and volume (m³)
	•	P₂ = final pressure (Pa)
	•	γ = heat capacity ratio (≈ 1.4 for air)

**Both are ideal.** Real CAES is neither isothermal nor adiabatic. Multiply by measured
round-trip efficiency (`caes_efficiency_2025`):

	•	Liquid piston adiabatic + packed-bed thermal storage: 72.6% (modelled)
	•	Underwater adiabatic, real operating conditions: 64.1% (measured)
	•	Gravity-assisted isobaric shaft: 87.1% (modelled only — not built)

**Use 60–73% for planning.** Adiabatic CAES is assessed as viable for 10–100 hour storage
durations (`caes_iscience_2025`) — the regime where lithium-ion is uneconomic, making CAES
a complement to batteries here rather than a competitor.


Gravity Battery System: E_grav = m × g × h

	•	E_grav = energy stored (J)
	•	m = mass lifted (kg)
	•	g = gravity (9.81 m/s²)
	•	h = height (m)


Biological Optimization

Phi-Based Network Self-Repair (Neural Ant Model)

	W(t+1) = φ⁻¹ × W(t) + (1 - φ⁻¹) × ΔL          φ⁻¹ = 1/φ = φ - 1 ≈ 0.618

	•	W = weight of the recovery pathway
	•	φ = golden ratio ≈ 1.618 (BioGrid base tuning constant)
	•	φ⁻¹ ≈ 0.618 = smoothing constant
	•	ΔL = loss differential based on decay/error rate

**Why the reciprocal.** The form previously given here used φ itself:
`W(t+1) = φ × W(t) + ΔL × (1 - φ)`. That recursion **diverges**. Its homogeneous solution is
`W(t) = φᵗ·W(0)`, and since φ > 1 the weight grows without bound; the fixed point at
`W* = ΔL` exists but is unstable, with any perturbation growing 1.618× per step. The
`(1 - φ)` coefficient is also negative, pushing away from the loss differential.

With φ⁻¹ the coefficients are positive and sum to 1, the fixed point is still `W* = ΔL`, and
it is **stable** — geometric convergence at 0.618 per step leaves about 1.6% of initial
error after 9 steps. This is an exponential moving average with a golden-ratio smoothing
constant, which is what the original text described. The golden ratio is preserved; only the
form that converges is used.


Wireless Energy Transmission (Sky Network)

Rectenna Efficiency:  η_rf = P_dc / P_rf

•	η_rf = RF conversion efficiency
	•	P_dc = DC power output (W)
	•	P_rf = RF power input (W)

**η_rf is strongly input-power dependent — a single value is misleading.** Reported peaks
reach 97.18% (`rectenna_review_2025`), but that is measured at high input power in a
controlled setup. For ambient harvesting, use **32% average across 2–18 GHz at −5 dBm**
(`rectenna_broadband_2025`); a representative 5G-band prototype yields 0.91 V DC at 0 dBm
input. Losses are dominated by rectifier diode non-linearity, transmission-line attenuation
and antenna–rectifier impedance mismatch, all of which worsen as input power falls.

Ambient RF power density supports sensor-class loads. It does not support
infrastructure-class ones.


Beam Path Loss (Free Space):  L_fs(dB) = 20 × log10(d) + 20 × log10(f) + 92.45

	•	d = distance (km)
	•	f = frequency (GHz)


Ant Colony Recovery Optimization (Simplified)

Probabilistic Path Selection:  P_i = (τ_i^α) × (η_i^β) / Σ(τ_j^α × η_j^β)

	•	P_i = probability of choosing path i
	•	τ_i = pheromone trail strength
	•	η_i = heuristic value (energy efficiency, redundancy)
	•	α, β = tunable parameters to favor exploration or exploitation

This is the standard ACO transition rule and is correct as written. The underlying
Physarum-derived network optimisation — reinforcing high-load links, pruning unused ones —
is well established for shortest path, minimum-risk path and network design
(`physarum_review`).

Worth knowing for grid routing: increasing substrate viscosity slows Physarum network
expansion but does **not** change final network complexity — fractal dimension converges to
the same value regardless (`physarum_viscosity_2025`). Translated to this domain, the cost
of laying cable should affect the build schedule, not the converged topology.

Free-space path loss above is also correct as written (d in km, f in GHz).

