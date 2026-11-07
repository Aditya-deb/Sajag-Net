import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from src.sajagnet.risk_engine import calculate_risk, calculate_false_alarm_cost
from src.sajagnet.config import ASSUMED_TRIAGE_COST_PER_ALERT

def test_risk_score_bounds():
    res = calculate_risk("DoS/DDoS", 1.0, 22)
    assert 0 <= res["risk_score"] <= 100
    
def test_confidence_increases_exposure():
    res_low = calculate_risk("Web Attack", 0.5, 443)
    res_high = calculate_risk("Web Attack", 0.9, 443)
    assert res_high["expected_financial_exposure_usd"] > res_low["expected_financial_exposure_usd"]
    
def test_asset_tier_impact():
    res_tier1 = calculate_risk("Brute Force", 0.9, 22)
    res_tier3 = calculate_risk("Brute Force", 0.9, 9999)
    assert res_tier1["risk_score"] >= res_tier3["risk_score"]
    
def test_benign_keys():
    res_benign = calculate_risk("Benign", 0.9, 80)
    res_attack = calculate_risk("PortScan", 0.9, 80)
    assert set(res_benign.keys()) == set(res_attack.keys())
    
def test_false_alarm_ratio():
    a1, cost_1 = calculate_false_alarm_cost(130, 1_000_000)
    a2, cost_2 = calculate_false_alarm_cost(2365, 1_000_000)
    ratio = cost_2 / cost_1
    assert abs(ratio - 18.2) < 0.1

def test_block_rule_no_double_confidence():
    # Ensures the double-confidence math bug is fixed
    res = calculate_risk("Web Attack", 0.5, 80)
    assert res["recommended_action"] == "Block & Remediate"

if __name__ == "__main__":
    print("=== SAJAGNET BUSINESS RISK SCENARIOS ===")
    print("\n[*] False Alarm Cost Assumptions:")
    print(f"    Cost per alert: ${ASSUMED_TRIAGE_COST_PER_ALERT}")
    volumes = {"Low": 100_000, "Base": 1_000_000, "High": 10_000_000}
    
    model1_fa = 130
    model2_fa = 2365
    
    for name, vol in volumes.items():
        a1, c1 = calculate_false_alarm_cost(model1_fa, vol)
        a2, c2 = calculate_false_alarm_cost(model2_fa, vol)
        ratio = c2 / c1 if c1 > 0 else 0
        # FIX: Added alerts per day next to the dollar figures
        print(f"    Volume {name} ({vol:,} flows/day): Model 1 ({a1:,} alerts): ${c1:,.2f} | Model 2 ({a2:,} alerts): ${c2:,.2f} | RATIO: {ratio:.1f}")

    print("\n[*] Example Attack Scenarios:")
    s1 = calculate_risk("Web Attack", 0.95, 443)
    print(f"    Web Attack (Port 443, 95% Conf): Score {s1['risk_score']} | Exp: ${s1['expected_financial_exposure_usd']:,.2f} | Action: {s1['recommended_action']}")
    
    s2 = calculate_risk("PortScan", 0.40, 80)
    print(f"    PortScan (Port 80, 40% Conf): Score {s2['risk_score']} | Exp: ${s2['expected_financial_exposure_usd']:,.2f} | Action: {s2['recommended_action']}")
    
    s3 = calculate_risk("Benign", 0.99, 22)
    print(f"    Benign (Port 22, 99% Conf): Score {s3['risk_score']} | Exp: ${s3['expected_financial_exposure_usd']:,.2f} | Action: {s3['recommended_action']}")
