import json
import os
import pandas as pd
from .config import (
    RISK_WEIGHTS, THRESHOLDS, ASSUMED_TRIAGE_COST_PER_ALERT, 
    ASSUMED_DOWNTIME_HOURS, ASSUMED_P_BREACH
)
from .mitre_mapper import get_threat_intel

registry_path = os.path.join("data", "asset_registry.json")
with open(registry_path, "r", encoding="utf-8-sig") as f:
    ASSET_REGISTRY = json.load(f)

def calculate_risk(prediction_class, confidence, dest_port):
    port_str = str(int(dest_port)) if not pd.isna(dest_port) else "default"
    asset = ASSET_REGISTRY.get(port_str, ASSET_REGISTRY["default"])
    
    if prediction_class == "Benign":
        return {
            "threat_class": "Benign",
            "mitre_id": "None",
            "asset_targeted": asset["server_type"],
            "risk_score": 0.0,
            "expected_financial_exposure_usd": 0.0,
            "recommended_action": "Allow",
            "technical_mitigation": "Allow traffic."
        }

    intel = get_threat_intel(prediction_class)
    
    score = (
        (intel["severity"] * RISK_WEIGHTS["threat_severity"]) +
        (asset["criticality_score"] * RISK_WEIGHTS["asset_criticality"]) +
        (confidence * RISK_WEIGHTS["confidence_score"])
    ) * 100

    downtime_h = ASSUMED_DOWNTIME_HOURS.get(prediction_class, 0.0)
    p_breach = ASSUMED_P_BREACH.get(prediction_class, 0.0)
    
    # Exposure already factors in confidence
    exposure = confidence * (
        (downtime_h * asset["assumed_hourly_downtime_cost"]) +
        (p_breach * asset["assumed_breach_liability"])
    )

    block_cost = asset["assumed_cost_of_blocking_legit_traffic"]
    
    # FIX: Removed the double-application of confidence on the exposure side
    if exposure > ((1 - confidence) * block_cost):
        action = "Block & Remediate"
    elif score >= THRESHOLDS["investigate"]:
        action = "Investigate"
    else:
        action = "Log & Alert"

    return {
        "threat_class": prediction_class,
        "mitre_id": intel["mitre_id"],
        "asset_targeted": asset["server_type"],
        "risk_score": round(score, 2),
        "expected_financial_exposure_usd": round(exposure, 2),
        "recommended_action": action,
        "technical_mitigation": intel["action"]
    }

def calculate_false_alarm_cost(false_alarms_per_100k, volume_flows_day):
    daily_alerts = (volume_flows_day / 100_000) * false_alarms_per_100k
    daily_cost = daily_alerts * ASSUMED_TRIAGE_COST_PER_ALERT
    # FIX: Now returning the number of alerts to print alongside the cost
    return int(daily_alerts), round(daily_cost, 2)
