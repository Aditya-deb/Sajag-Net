import json, os, sys
sys.path.append(os.path.abspath('src'))
print("\n--- PER-CLASS TABLE ---")
try:
    from sajagnet.config import THREAT_SEVERITY, DOWNTIME_HOURS, BREACH_PROBABILITY
    for k in THREAT_SEVERITY.keys():
        print(f"| {k} | {THREAT_SEVERITY[k]} | {DOWNTIME_HOURS.get(k, 0)} | {BREACH_PROBABILITY.get(k, 0)} |")
except:
    print("Config error")
print("\n--- ASSET TABLE ---")
try:
    with open("data/asset_registry.json", "r") as f:
        assets = json.load(f)
    for p, d in assets.items():
        print(f"| {p} | {d.get('asset')} | {d.get('criticality')} | {d.get('hourly_cost')} | {d.get('liability')} | {d.get('cost_to_block')} |")
except:
    print("Asset registry error")
