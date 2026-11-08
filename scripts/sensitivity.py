from pathlib import Path

import pandas as pd

from sajagnet import config
from sajagnet.risk_engine import ASSET_REGISTRY
from sajagnet.incidents import build_incidents

CONF = 0.9999  # assumed model score for every incident (illustrative)
INCIDENT_TYPES = [
    ("Brute Force", 22),
    ("Web Attack", 80),
    ("DoS/DDoS", 80),
    ("Brute Force", 21),
    ("PortScan", 1021),
]
stream = pd.DataFrame(INCIDENT_TYPES, columns=["Predicted_Class", "Destination_Port"])
stream["Confidence"] = CONF

BASE_P = config.ASSUMED_P_BREACH["Brute Force"]
BASE_LIAB = ASSET_REGISTRY["22"]["assumed_breach_liability"]


def is_ssh(inc):
    return (inc["Threat Class"] == "Brute Force") & (inc["Target Asset"] == "Internal SSH/Admin")


def run(p=None, liab=None):
    config.ASSUMED_P_BREACH["Brute Force"] = BASE_P if p is None else p
    ASSET_REGISTRY["22"]["assumed_breach_liability"] = BASE_LIAB if liab is None else liab
    inc = build_incidents(stream)
    ssh_exp = inc[is_ssh(inc)].iloc[0]["Exposure"]
    greater = int((inc["Exposure"] > ssh_exp + 0.005).sum())
    ties = int(((inc["Exposure"] - ssh_exp).abs() <= 0.005).sum()) - 1
    return inc, ssh_exp, greater + 1, ties


scenarios = [
    (f"Baseline ({BASE_P:.1%} breach probability, ${BASE_LIAB:,} liability)", None, None),
    ("Breach probability 2.5%", 0.025, None),
    ("Breach probability 1.5%", 0.015, None),
    ("Breach probability 7.5%", 0.075, None),
    ("Liability -50% ($250,000)", None, BASE_LIAB * 0.5),
    ("Liability $150,000", None, 150000),
    ("Liability +50% ($750,000)", None, BASE_LIAB * 1.5),
]

lines = ["| Scenario | SSH Brute Force exposure | Rank among incidents |", "| :--- | :--- | :--- |"]
for label, p, liab in scenarios:
    _, exp, rank, ties, = run(p, liab)
    note = " (tie)" if ties else ""
    lines.append(f"| {label} | ${exp:,.2f} | #{rank}{note} |")

inc, _, _, _ = run()
others = inc[~is_ssh(inc)].sort_values("Exposure", ascending=False)
ctx = ", ".join(f"{r['Threat Class']} on {r['Target Asset']} ${r['Exposure']:,.2f}" for _, r in others.iterrows())
dos = others[others["Threat Class"] == "DoS/DDoS"]["Exposure"].iloc[0]
lines.append("")
lines.append(f"Other incidents at baseline: {ctx}.")
lines.append(f"The SSH incident drops below the DoS incident when breach probability x liability is under ${dos / CONF:,.0f}.")
lines.append(f"Computed by calling the real incident and risk code with model score {CONF} for every incident. All inputs are illustrative assumptions.")

out = "\n".join(lines)
print(out)
Path("reports").mkdir(exist_ok=True)
Path("reports/sensitivity.md").write_text(out, encoding="utf-8")
