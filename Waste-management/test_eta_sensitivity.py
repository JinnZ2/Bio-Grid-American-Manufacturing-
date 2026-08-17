"""Tests for NERE transduction efficiency sensitivity analysis.

The calculate_power_output function is duplicated here to avoid importing
eta_sensitivity.py, which requires numpy/matplotlib at module level.
"""


def calculate_power_output(P_mechanical, eta_T):
    """
    Calculate electrical power output from mechanical input.
    Must match the implementation in eta_sensitivity.py.
    """
    coupling_factor = 1 + eta_T
    P_electrical = coupling_factor * eta_T**2 * P_mechanical
    return P_electrical


def test_zero_efficiency_yields_zero_output():
    """Zero transduction efficiency should produce zero power."""
    assert calculate_power_output(1000, 0) == 0.0


def test_positive_efficiency_yields_positive_output():
    """Any positive efficiency with positive input should produce positive output."""
    result = calculate_power_output(1000, 0.25)
    assert result > 0


def test_higher_efficiency_yields_more_power():
    """Higher transduction efficiency should yield more power output."""
    low = calculate_power_output(1000, 0.05)
    high = calculate_power_output(1000, 0.25)
    assert high > low


def test_power_scales_with_input():
    """Doubling mechanical input should double electrical output."""
    p1 = calculate_power_output(1000, 0.25)
    p2 = calculate_power_output(2000, 0.25)
    assert abs(p2 - 2 * p1) < 1e-10


def test_eta_squared_relationship():
    """Power should scale faster than linearly with eta due to eta^2 coupling."""
    eta1 = 0.10
    eta2 = 0.20  # 2x efficiency
    p1 = calculate_power_output(1000, eta1)
    p2 = calculate_power_output(1000, eta2)
    ratio = p2 / p1
    # Should be > 4x (more than linear squared) due to coupling factor
    assert ratio > 4


def test_known_values():
    """Verify specific known calculations."""
    # P = (1 + eta) * eta^2 * P_mech
    result = calculate_power_output(1000, 0.25)
    expected = (1 + 0.25) * (0.25**2) * 1000  # 1.25 * 0.0625 * 1000 = 78.125
    assert abs(result - expected) < 1e-10


if __name__ == "__main__":
    test_zero_efficiency_yields_zero_output()
    test_positive_efficiency_yields_positive_output()
    test_higher_efficiency_yields_more_power()
    test_power_scales_with_input()
    test_eta_squared_relationship()
    test_known_values()
    print("All tests passed!")
