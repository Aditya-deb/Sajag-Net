| Threat class | Severity (0-1) | Downtime (hours) | Breach probability |
| :--- | :--- | :--- | :--- |
| Brute Force | 0.7 | 0.0 | 5% |
| Web Attack | 0.8 | 1.0 | 15% |
| DoS/DDoS | 0.9 | 2.0 | 0% |
| PortScan | 0.4 | 0.0 | 2% |

| Port | Asset | Criticality (0-1) | Hourly downtime cost | Breach liability | Cost of blocking |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 80 | Public Web Server | 0.7 | $5,000 | $50,000 | $1,000 |
| 443 | Secure Web Gateway | 0.9 | $10,000 | $250,000 | $2,500 |
| 22 | Internal SSH/Admin | 1.0 | $2,000 | $500,000 | $500 |
| default | General Endpoint | 0.3 | $500 | $5,000 | $100 |

Risk weights: severity 0.4, asset criticality 0.35, model score 0.25. Triage cost per alert: $50.