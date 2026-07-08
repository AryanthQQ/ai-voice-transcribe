import sys, json
sys.path.insert(0, 'mcp')

from tools.knowledge_base import handle

print("=== KNOWLEDGE BASE TEST ===")
print("1. Reading entire KB...")
res = handle("read")
kb = res.get("data", {})
for topic, notes in kb.items():
    print(f"  {topic}: {len(notes)} notes")

print("\n2. Reading specific topic (coding_rules)...")
res = handle("read", topic="coding_rules")
print(f"  Found {len(res.get('data', []))} coding rules.")

print("\n3. Adding a new rule...")
res = handle("add_note", topic="coding_rules", note="Test Rule: Always run tests.")
print(f"  Message: {res.get('message')}")

print("\n4. Reading updated topic...")
res = handle("read", topic="coding_rules")
rules = res.get("data", [])
print(f"  Total rules now: {len(rules)}")
print(f"  Last rule: {rules[-1]}")

print("\n5. Removing the test rule...")
res = handle("remove_note", topic="coding_rules", index=len(rules)-1)
print(f"  Message: {res.get('message')}")

print("\nTest completed successfully.")
