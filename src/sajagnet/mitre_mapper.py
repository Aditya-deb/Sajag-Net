# Maps raw model predictions to MITRE ATT&CK tactics and severity assumptions
MITRE_KNOWLEDGE_BASE = {
    "Brute Force": {
        "mitre_id": "T1110",
        "severity": 0.8,
        "action": "Force password reset and lock account temporarily.",
        "iptables_example": "iptables -A INPUT -p tcp --dport 22 -m conntrack --ctstate NEW -m recent --set; iptables -A INPUT -p tcp --dport 22 -m conntrack --ctstate NEW -m recent --update --seconds 60 --hitcount 4 -j DROP"
    },
    "DoS/DDoS": {
        "mitre_id": "T1498",
        "severity": 0.9,
        "action": "Activate rate-limiting and route traffic through DDoS scrubbing center.",
        "iptables_example": "iptables -A INPUT -p tcp --dport 80 -m limit --limit 25/minute --limit-burst 100 -j ACCEPT"
    },
    "PortScan": {
        "mitre_id": "T1046",
        "severity": 0.4,
        "action": "Log source IP and monitor for subsequent targeted attacks. No immediate block required.",
        "iptables_example": "iptables -A INPUT -p tcp --tcp-flags SYN,ACK,FIN,RST RST -m limit --limit 1/s -j ACCEPT"
    },
    "Web Attack": {
        "mitre_id": "T1190",
        "severity": 0.85,
        "action": "Update WAF rules to block malicious payload signatures and sanitize inputs.",
        "iptables_example": "iptables -A INPUT -p tcp --dport 443 -m string --algo bm --string 'UNION SELECT' -j DROP"
    },
    "Benign": {
        "mitre_id": "None",
        "severity": 0.0,
        "action": "Allow traffic.",
        "iptables_example": "None"
    }
}

def get_threat_intel(prediction_class):
    return MITRE_KNOWLEDGE_BASE.get(prediction_class, MITRE_KNOWLEDGE_BASE["Benign"])
