# ALL NUMBERS HERE ARE ASSUMPTIONS FOR THE MVP

RISK_WEIGHTS = {
    "threat_severity": 0.40,
    "asset_criticality": 0.35,
    "confidence_score": 0.25
}

# New Policy Thresholds
MIN_CONFIDENCE_TO_BLOCK = 0.90
MIN_CONFIDENCE_TO_INVESTIGATE = 0.50

ASSUMED_TRIAGE_COST_PER_ALERT = 50.0

ASSUMED_DOWNTIME_HOURS = {
    "DoS/DDoS": 2.0,
    "PortScan": 0.0,
    "Brute Force": 0.0,
    "Web Attack": 1.0,
    "Benign": 0.0
}

ASSUMED_P_BREACH = {
    "DoS/DDoS": 0.0,
    "PortScan": 0.02,
    "Brute Force": 0.05,
    "Web Attack": 0.15,
    "Benign": 0.0
}
