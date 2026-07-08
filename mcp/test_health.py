import sys, json
sys.path.insert(0, 'mcp')

from tools.project_health import handle

print("=== PROJECT HEALTH TEST ===")
print("Running health diagnostics...\n")
res = handle()

print(f"Health Score: {res['health_score']}/100")
print(f"Timestamp: {res['timestamp']}")

print("\n--- Statistics ---")
print(json.dumps(res['project_statistics'], indent=2))

print("\n--- Diagnostics ---")
for k, v in res['diagnostics'].items():
    print(f"{k}: {len(v)} items")
    if v:
        for item in v[:3]:
            print(f"  - {item}")
        if len(v) > 3:
            print(f"  - ... and {len(v) - 3} more")

print("\nTest completed successfully. Output is fully structured JSON.")
