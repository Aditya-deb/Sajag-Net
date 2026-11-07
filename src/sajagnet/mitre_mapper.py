def get_mitre_info(threat_class):
    mapping = {
        "Brute Force": {"id": "T1110", "mitigation": "Block source IP + enforce account lockout/MFA.", "severity": 0.7},
        "Web Attack": {"id": "T1190", "mitigation": "Block source IP + deploy WAF rules and sanitize input.", "severity": 0.8},
        "DoS/DDoS": {"id": "T1498", "mitigation": "Block source IP + rate-limit.", "severity": 0.9},
        "PortScan": {"id": "T1046", "mitigation": "Block source IP + review firewall rules.", "severity": 0.4}
    }
    return mapping.get(threat_class, {"id": "T1078", "mitigation": "Block source IP + Review access logs.", "severity": 0.5})

get_threat_intel = get_mitre_info
