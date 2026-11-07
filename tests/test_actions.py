import pytest
import sys, os
sys.path.append(os.path.abspath("src"))
from sajagnet.risk_engine import calculate_risk

@pytest.mark.parametrize("threat, conf, port, expected_action", [
    ("DoS/DDoS", 0.95, 80, "Block & Remediate"),
    ("Web Attack", 0.90, 443, "Block & Remediate"), # Boundary
    ("DoS/DDoS", 0.60, 80, "Investigate"),
    ("Web Attack", 0.50, 443, "Investigate"), # Boundary
    ("DoS/DDoS", 0.40, 80, "Log & Alert"),
    ("Web Attack", 0.20, 443, "Log & Alert")
])
def test_three_action_tiers(threat, conf, port, expected_action):
    res = calculate_risk(threat, conf, port)
    assert res["recommended_action"] == expected_action
    
def test_cost_rule_fails():
    # Extreme block cost vs low exposure (c* is around 9% for DoS, so 5% conf fails the cost rule)
    res = calculate_risk("DoS/DDoS", 0.05, 80)
    assert res["recommended_action"] == "Log & Alert"
