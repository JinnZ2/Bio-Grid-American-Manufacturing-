"""
NERE Transduction Efficiency Sensitivity Analysis

Demonstrates why η_T² relationship dominates system performance.
Shows that material improvements (η_T: 0.05 → 0.25) matter more 
than source energy increases.
"""

import numpy as np
import matplotlib.pyplot as plt

def calculate_power_output(P_mechanical, eta_T):
    """
    Calculate electrical power output from mechanical input.
    
    Args:
        P_mechanical: Mechanical power input (W)
        eta_T: Transduction efficiency (dimensionless, 0-1)
    
    Returns:
        P_electrical: Electrical power output (W)
    """
    # Power scales with η_T² due to coupling effects
    # (impedance matching improves mechanical input when conversion improves)
    coupling_factor = 1 + eta_T  # simplified model
    P_electrical = coupling_factor * eta_T**2 * P_mechanical
    return P_electrical

def plot_eta_sensitivity():
    """Generate plots showing η_T sensitivity."""
    
    # Parameters
    P_mech_base = 1000  # 1 kW mechanical input from CTX pulse
    eta_range = np.linspace(0.01, 0.50, 100)
    
    # Calculate power output across efficiency range
    P_out = [calculate_power_output(P_mech_base, eta) for eta in eta_range]
    
    # Key reference points
    eta_typical = 0.05  # Standard piezoelectric in waste
    eta_target = 0.25   # SAMG target with PMN-PT
    eta_optimistic = 0.40  # Upper bound with perfect coupling
    
    P_typical = calculate_power_output(P_mech_base, eta_typical)
    P_target = calculate_power_output(P_mech_base, eta_target)
    P_optimistic = calculate_power_output(P_mech_base, eta_optimistic)
    
    # Plot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Left plot: Absolute power output
    ax1.plot(eta_range * 100, P_out, 'b-', linewidth=2)
    ax1.axhline(P_typical, color='r', linestyle='--', alpha=0.5, 
                label=f'Typical: η={eta_typical:.2f} → {P_typical:.1f}W')
    ax1.axhline(P_target, color='g', linestyle='--', alpha=0.5,
                label=f'NERE Target: η={eta_target:.2f} → {P_target:.1f}W')
    ax1.axhline(P_optimistic, color='orange', linestyle='--', alpha=0.5,
                label=f'Optimistic: η={eta_optimistic:.2f} → {P_optimistic:.1f}W')
    ax1.set_xlabel('Transduction Efficiency η_T (%)', fontsize=12)
    ax1.set_ylabel('Electrical Power Output (W)', fontsize=12)
    ax1.set_title('Power Output vs. Transduction Efficiency', fontsize=14, weight='bold')
    ax1.legend()
    ax1.grid(alpha=0.3)
    
    # Right plot: Multiplication factor
    multiplication = np.array(P_out) / P_typical
    ax2.plot(eta_range * 100, multiplication, 'b-', linewidth=2)
    ax2.axhline(1, color='r', linestyle='--', alpha=0.5, label='Baseline (η=0.05)')
    ax2.axhline(P_target/P_typical, color='g', linestyle='--', alpha=0.5,
                label=f'NERE Target: {P_target/P_typical:.1f}× gain')
    ax2.set_xlabel('Transduction Efficiency η_T (%)', fontsize=12)
    ax2.set_ylabel('Multiplication Factor', fontsize=12)
    ax2.set_title('Energy Multiplication from η_T Improvement', fontsize=14, weight='bold')
    ax2.legend()
    ax2.grid(alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('eta_sensitivity.png', dpi=150)
    print(f"Plot saved as 'eta_sensitivity.png'")
    
    # Print key numbers
    print("\n=== NERE Transduction Efficiency Analysis ===")
    print(f"\nMechanical input: {P_mech_base}W")
    print(f"\nTypical system (η_T = {eta_typical:.2f}):")
    print(f"  Output: {P_typical:.1f}W")
    print(f"\nNERE target (η_T = {eta_target:.2f}):")
    print(f"  Output: {P_target:.1f}W")
    print(f"  Multiplication: {P_target/P_typical:.1f}×")
    print(f"\nOptimistic case (η_T = {eta_optimistic:.2f}):")
    print(f"  Output: {P_optimistic:.1f}W")
    print(f"  Multiplication: {P_optimistic/P_typical:.1f}×")
    print(f"\n=== Key Insight ===")
    print(f"Improving η_T from 0.05 to 0.25 (5× improvement)")
    print(f"yields {P_target/P_typical:.1f}× power gain (not 5×!)")
    print(f"This is the η_T² effect + coupling improvements.\n")

def analyze_system_scaling():
    """Analyze how system scales with multiple zones."""
    
    print("\n=== NERE System Scaling Analysis ===")
    
    # Single zone parameters
    P_mech_single = 1000  # W mechanical per CTX pulse
    eta_T = 0.25  # NERE target
    P_elec_single = calculate_power_output(P_mech_single, eta_T)
    pulse_duration = 300  # seconds (5 minutes)
    cooldown_time = 3000  # seconds (50 minutes)
    duty_cycle = pulse_duration / (pulse_duration + cooldown_time)
    
    print(f"\nSingle zone:")
    print(f"  Peak power: {P_elec_single:.1f}W")
    print(f"  Pulse duration: {pulse_duration}s")
    print(f"  Duty cycle: {duty_cycle:.2%}")
    print(f"  Average power: {P_elec_single * duty_cycle:.1f}W")
    
    # Multi-zone system
    num_zones = [1, 5, 10, 25, 50, 100]
    for n in num_zones:
        avg_power = P_elec_single * min(n * duty_cycle, 1.0)  # can't exceed 100%
        annual_energy = avg_power * 8760 / 1000  # kWh/year
        print(f"\n{n} zones:")
        print(f"  Average power: {avg_power:.0f}W")
        print(f"  Annual energy: {annual_energy:.0f} kWh")
        if n >= 10:
            print(f"  → Continuous output (zones staggered)")

if __name__ == "__main__":
    plot_eta_sensitivity()
    analyze_system_scaling()
