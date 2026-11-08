import json
from pathlib import Path

import pandas as pd

from sajagnet.config import (
    RISK_WEIGHTS,
    ASSUMED_DOWNTIME_HOURS,
    ASSUMED_P_BREACH,
    MIN_CONFIDENCE_TO_BLOCK,
    MIN_CONFIDENCE_TO_INVESTIGATE,
)
from sajagnet.mitre_mapper import get_threat_intel

# Single source of truth for asset values: data/asset_registry.json (all numbers are assumptions)
_REGISTRY_PATH = Path(__file__).resolve().parents[2] / "data" / "asset_registry.json"
ASSET_REGISTRY = json.loads(_REGISTRY_PATH.read_text(encoding="utf-8-sig"))


def calculate_risk(prediction_class, confidence, dest_port):
    port_str = str(int(dest_port)) if not pd.isna(dest_port) else "default"
    asset = ASSET_REGISTRY.get(port_str, ASSET_REGISTRY["default"])

    if prediction_class == "Benign":
        return {"threat_class": "Benign", "mitre_id": "None", "asset_targeted": asset["server_type"], "risk_score": 0.0, "expected_financial_exposure_usd": 0.0, "recommended_action": "Allow", "technical_mitigation": "Allow traffic."}

    intel = get_threat_intel(prediction_class)

    score = ((intel["severity"] * RISK_WEIGHTS["threat_severity"]) + (asset["criticality_score"] * RISK_WEIGHTS["asset_criticality"]) + (confidence * RISK_WEIGHTS["confidence_score"])) * 100

    downtime_h = ASSUMED_DOWNTIME_HOURS.get(prediction_class, 0.0)
    p_breach = ASSUMED_P_BREACH.get(prediction_class, 0.0)

    exposure = confidence * ((downtime_h * asset["assumed_hourly_downtime_cost"]) + (p_breach * asset["assumed_breach_liability"]))
    block_cost = asset["assumed_cost_of_blocking_legit_traffic"]

    cost_rule_holds = exposure > ((1 - confidence) * block_cost)

    if cost_rule_holds and confidence >= MIN_CONFIDENCE_TO_BLOCK:
        action = "Block & Remediate"
    elif cost_rule_holds and confidence >= MIN_CONFIDENCE_TO_INVESTIGATE:
        action = "Investigate"
    else:
        action = "Log & Alert"

    return {
        "threat_class": prediction_class,
        "mitre_id": intel["id"],
        "asset_targeted": asset["server_type"],
        "risk_score": round(score, 2),
        "expected_financial_exposure_usd": round(exposure, 2),
        "recommended_action": action,
        "technical_mitigation": intel["mitigation"]
    }


def calculate_false_alarm_cost(false_alarms, cost_per_alert=50.0):
    return false_alarms * cost_per_alert
