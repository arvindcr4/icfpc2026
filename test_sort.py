import sys
sys.path.append('/home/claude/icfpc2026')
import sim, json

spec = json.load(open('/home/claude/icfpc2026/spec_sort.json'))
prog = open('/home/claude/icfpc2026/sort.man').read()

print("Testing all 7 test cases in publicTestData...")
all_passed = True
total_rounds = 0
passed_rounds = 0

for idx, tc in enumerate(spec['publicTestData']):
    rounds = tc['rounds']
    for r_idx, r in enumerate(rounds):
        total_rounds += 1
        inp = r['in']
        expected = r['out']
        try:
            out, ticks, w, h = sim.run(prog, inp, max_ticks=50000)
            if out == expected:
                passed_rounds += 1
                print(f"Case {idx+1} Round {r_idx+1}: PASS (ticks={ticks})")
            else:
                print(f"Case {idx+1} Round {r_idx+1}: FAIL\n  Expected: {expected}\n  Got:      {out}")
                all_passed = False
        except Exception as e:
            print(f"Case {idx+1} Round {r_idx+1}: ERROR: {e}")
            all_passed = False

print(f"\nResult: {passed_rounds}/{total_rounds} rounds passed.")
if all_passed:
    print("ALL TEST CASES PASSED PERFECTLY!")
