import sys, json
import sim

def solve_with_sim(grid_text, inp_list, max_t=500000, trace=0):
    return sim.run(grid_text, inp_list, max_ticks=max_t, trace=trace)

def run_test_suite(grid_text):
    with open('/home/claude/icfpc2026/tcp_spec.json') as f:
        spec = json.load(f)
    
    all_pass = True
    for idx, tc in enumerate(spec['publicTestData']):
        print(f"=== Test {idx+1}: {tc['name']} ===")
        full_inputs = []
        expected_outs = []
        for r in tc['rounds']:
            full_inputs.extend([int(x) for x in r['in']])
            expected_outs.extend([int(x) for x in r['out']])
        
        try:
            out, ticks, w, h = solve_with_sim(grid_text, full_inputs)
            score = max(w, h)**2 * ticks
            if out == expected_outs:
                print(f"  PASS! ticks={ticks}, bbox={w}x{h}, score={score}")
            else:
                print(f"  FAIL!")
                print(f"   Actual:   {out}")
                print(f"   Expected: {expected_outs}")
                all_pass = False
        except Exception as e:
            print(f"  ERROR: {type(e).__name__}: {e}")
            all_pass = False

    return all_pass

if __name__ == '__main__':
    grid = open('/home/claude/icfpc2026/tcp.man').read()
    res = run_test_suite(grid)
    print('\nOVERALL RESULT:', 'PASS' if res else 'FAIL')
