import sys, json
sys.path.insert(0, 'mcp')

from tools.memory_engine import handle

print("=== MEMORY ENGINE TEST ===")
print("1. Reading memory...")
res = handle("read")
mem = res.get("memory", {})
print(f"Current version: {mem.get('current_version')}")
print(f"Project goals: {len(mem.get('project_goals', []))}")
print(f"Completed features: {len(mem.get('completed_features', []))}")

print("\n2. Updating version...")
res = handle("set_version", value="0.1.1")
print(res.get("message"))

print("\n3. Adding a new pending feature...")
res = handle("add", category="pending_features", value="Test Feature XYZ")
print(res.get("message"))

print("\n4. Reading updated memory...")
res = handle("read")
pending = res["memory"]["pending_features"]
print(f"Pending features count: {len(pending)}")
print(f"Last pending feature: {pending[-1]}")

print("\n5. Removing the test feature...")
res = handle("remove", category="pending_features", index=len(pending)-1)
print(res.get("message"))

print("\n6. Restoring version...")
res = handle("set_version", value="0.1.0")
print(res.get("message"))

print("\nTest completed successfully.")
