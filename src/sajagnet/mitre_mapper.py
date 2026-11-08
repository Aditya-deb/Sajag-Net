from sajagnet.config import THREAT_SEVERITY, UNMAPPED_SEVERITY

_MITRE = {
    "Brute Force": {"id": "T1110", "mitigation": "Block source IP + enforce account lockout/MFA."},
    "Web Attack": {"id": "T1190", "mitigation": "Block source IP + deploy WAF rules and sanitize input."},
    "DoS/DDoS": {"id": "T1498", "mitigation": "Block source IP + rate-limit."},
    "PortScan": {"id": "T1046", "mitigation": "Block source IP + review firewall rules."},
}

_UNMAPPED = {"id": "UNMAPPED", "mitigation": "Block source IP + review access logs.", "severity": UNMAPPED_SEVERITY}


def get_mitre_info(threat_class):
    if threat_class not in _MITRE:
        return dict(_UNMAPPED)
    info = dict(_MITRE[threat_class])
    info["severity"] = THREAT_SEVERITY[threat_class]
    return info


get_threat_intel = get_mitre_info
