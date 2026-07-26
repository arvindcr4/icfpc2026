import sys
sys.path.append('/home/claude/icfpc2026')
import sim, json

spec = json.load(open('/home/claude/icfpc2026/spec_sort.json'))

# Let's test python simulation of selection sort logic first to ensure 100% mathematical correctness
def py_sort(inputs):
    # inputs is a list of ints for all rounds in a testcase
    # each round: N, then N items
    idx = 0
    out = []
    while idx < len(inputs):
        N = inputs[idx]
        idx += 1
        items = inputs[idx:idx+N]
        idx += N
        # Selection sort
        items_sorted = sorted(items)
        out.extend(items_sorted)
    return out

print("Py sort logic test:")
tc0 = spec['publicTestData'][0]
inp0 = []
for r in tc0['rounds']:
    inp0.append(int(r['in'][0]))
    inp0.extend([int(x) for x in r['in'][1:]])
print("Input:", inp0)
print("Output:", py_sort(inp0))
