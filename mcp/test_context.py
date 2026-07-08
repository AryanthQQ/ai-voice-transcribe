import sys, json
sys.path.insert(0, 'mcp')

from tools.context_builder import handle

result = handle(include_file_tree=False)
ctx = result['context']

print('=== CONTEXT BUILDER TEST ===')
print('Build time:           ', result['build_duration_ms'], 'ms')
print('Implemented features :', ctx['features']['counts']['implemented'])
print('Pending TODO items   :', len(ctx['current_todo']))
print('Known issues         :', len(ctx['known_issues']))
print('Dependencies         :', len(ctx['dependencies']))
print('API routes           :', len(result['api_surface']))

print()
print('--- CURRENT SPRINT ---')
print(json.dumps(ctx['current_sprint'], indent=2))

print()
print('--- TOP 5 TODO ---')
for t in ctx['current_todo'][:5]:
    print(f"  {t['priority']}. {t['item']} -- {t['detail'][:60]}")

print()
print('--- KNOWN ISSUES ---')
for i in ctx['known_issues']:
    print(f"  [{i['severity']}] {i['id']}: {i['title']}")

print()
warnings = result.get('build_warnings', [])
if warnings:
    print('WARNINGS:', warnings)
else:
    print('No build warnings. All 7 sections built successfully.')
