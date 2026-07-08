import sys, json
sys.path.insert(0, 'mcp')

from tools.ai_context_api import handle

print("=== AI CONTEXT API TEST ===")
print("Fetching complete machine-readable context...\n")
res = handle(include_file_tree=False)

print(f"Timestamp: {res['timestamp']}")
print(f"Disk State Keys: {list(res['project_disk_state'].keys())}")
print(f"Memory State Keys: {list(res['project_memory_state'].keys())}")
print(f"Knowledge Base Keys: {list(res['project_knowledge_base'].keys())}")

print("\n--- Project Disk State Summary ---")
print(json.dumps(res['project_disk_state']['summary'], indent=2))

print("\n--- Project Memory State (Truncated) ---")
print(f"Goals: {len(res['project_memory_state'].get('project_goals', []))}")
print(f"Next Sprint: {len(res['project_memory_state'].get('next_sprint', []))}")

print("\n--- Knowledge Base State (Truncated) ---")
for topic, notes in res['project_knowledge_base'].items():
    print(f"  {topic}: {len(notes)} items")

print("\nTest completed successfully. Output is fully structured JSON.")
