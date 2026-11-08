import json, os, sys
sys.path.append(os.path.abspath('src'))
try:
    from sajagnet.config import THREAT_SEVERITY, DOWNTIME_HOURS, BREACH_PROBABILITY
    print("--- PER-CLASS TABLE ---")
    for k in THREAT_SEVERITY.keys():
        print(f"| {k} | {THREAT_SEVERITY[k]} | {DOWNTIME_HOURS.get(k, 0)} | {BREACH_PROBABILITY.get(k, 0)} |")
except Exception as e:
    print("Config error:", e)

try:
    with open("data/asset_registry.json", "r") as f:
        assets = json.load(f)
    print("\n--- ASSET TABLE ---")
    for p, d in assets.items():
        print(f"| {p} | {d.get('asset')} | {d.get('criticality')} | {d.get('hourly_cost')} | {d.get('liability')} | {d.get('cost_to_block')} |")
except Exception as e:
    print("Asset registry error:", e)
