import pytest
from sajagnet.risk_engine import calculate_risk

def calculate_false_alarm_cost(false_alarms, flows, cost_per_alert=50.0):
    return (false_alarms / flows), (false_alarms * cost_per_alert)

def test_false_alarm_ratio():
    ratio, cost = calculate_false_alarm_cost(130, 1_000_000)
    assert cost == 6500

def test_block_rule_no_double_confidence():
    # With the new 3-tier policy, a 0.50 score on Web Attack (which passes the cost rule) 
    # should trigger "Investigate", not "Block & Remediate".
    res = calculate_risk("Web Attack", 0.5, 80)
    assert res["recommended_action"] == "Investigate"
