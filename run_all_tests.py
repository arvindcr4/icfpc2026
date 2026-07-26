import sys
sys.path.append('/home/claude/icfpc2026')
import sim, json

spec = json.load(open('/home/claude/icfpc2026/spec_sort.json'))

# Let's write the complete sort.man program
prog = '''+-+                  +-+
|I|                  |O|
+-+                  +-+
 v                    ^
 v                    ^
+-----------------------+         +-------+
|@ r      s b v        s|>>>>>>>>>|r s   v|
|>^<        < <        <|<<<<<<<<<|^ < < <|
+-----------------------+         +-------+
          v   ^
          v   ^
       +-------+
       |r s   v|
       |^ < < <|
       +-------+'''

with open('/home/claude/icfpc2026/sort.man', 'w') as f:
    f.write(prog)

total_passed = 0
total_cases = len(spec['publicTestData'])
for tc in spec['publicTestData']:
    print(f"Testing case: {tc['name']}")
    case_ok = True
    for r_idx, r in enumerate(tc['rounds']):
        inp = [int(x) for x in r['in']]
        expected_out = [int(x) for x in r['out']]
        try:
            out, ticks, w, h = sim.run(prog, inp, max_ticks=2_000_000, trace=0)
            if out != expected_out:
                print(f"  FAIL round {r_idx+1}: expected {expected_out}, got {out}")
                case_ok = False
                break
            else:
                print(f"  PASS round {r_idx+1}: ticks={ticks}")
        except Exception as e:
            print(f"  ERROR round {r_idx+1}: {e}")
            case_ok = False
            break
    if case_ok:
        total_passed += 1

print(f"\nSummary: {total_passed}/{total_cases} cases passed.")
