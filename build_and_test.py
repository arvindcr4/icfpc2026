import sys
sys.path.append('/home/claude/icfpc2026')
import sim, json

spec = json.load(open('/home/claude/icfpc2026/spec_sort.json'))

# Let's test a simple round first
tc0 = spec['publicTestData'][0] # warm up: [3, 3, 1, 2] -> [1, 2, 3]
print("Target warm up round 1:", tc0['rounds'][0])
