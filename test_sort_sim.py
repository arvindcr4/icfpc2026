import sys
sys.path.append('/home/claude/icfpc2026')
import sim, json

spec = json.load(open('/home/claude/icfpc2026/spec_sort.json'))

# Let's inspect all public test data cases to understand the exact requirements
for idx, tc in enumerate(spec['publicTestData']):
    print(f"Case {idx+1}: {tc.get('description')}, rounds={len(tc['rounds'])}")
    for r in tc['rounds']:
        print(f"  N={r['in'][0]}, in={r['in'][1:]}, out={r['out']}")

