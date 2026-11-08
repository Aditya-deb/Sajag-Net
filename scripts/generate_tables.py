from pathlib import Path

from sajagnet import config
from sajagnet.risk_engine import ASSET_REGISTRY

lines = []
lines.append("| Threat class | Severity (0-1) | Downtime (hours) | Breach probability |")
lines.append("| :--- | :--- | :--- | :--- |")
for cls, sev in config.THREAT_SEVERITY.items():
    hours = config.ASSUMED_DOWNTIME_HOURS.get(cls, 0.0)
    p = config.ASSUMED_P_BREACH.get(cls, 0.0)
    lines.append(f"| {cls} | {sev} | {hours} | {p:.0%} |")
lines.append("")
lines.append("| Port | Asset | Criticality (0-1) | Hourly downtime cost | Breach liability | Cost of blocking |")
lines.append("| :--- | :--- | :--- | :--- | :--- | :--- |")
for port, a in ASSET_REGISTRY.items():
    lines.append(
        f"| {port} | {a['server_type']} | {a['criticality_score']} | "
        f"${a['assumed_hourly_downtime_cost']:,} | ${a['assumed_breach_liability']:,} | "
        f"${a['assumed_cost_of_blocking_legit_traffic']:,} |"
    )
lines.append("")
w = config.RISK_WEIGHTS
lines.append(
    f"Risk weights: severity {w['threat_severity']}, asset criticality {w['asset_criticality']}, "
    f"model score {w['confidence_score']}. Triage cost per alert: ${config.ASSUMED_TRIAGE_COST_PER_ALERT:,.0f}."
)

out = "\n".join(lines)
print(out)
Path("reports").mkdir(exist_ok=True)
Path("reports/readme_tables.md").write_text(out, encoding="utf-8")
