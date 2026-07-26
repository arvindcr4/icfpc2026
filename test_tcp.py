import sys, json
import sim

def test_all_cases(man_path):
    with open('/home/claude/icfpc2026/tcp_spec.json') as f:
        spec = json.load(f)
    
    text = open(man_path).read()
    all_pass = True
    for idx, tc in enumerate(spec['publicTestData']):
        print(f"=== Testing Case {idx+1}: {tc['name']} ===")
        # Concatenate all round inputs
        full_inputs = []
        expected_outs = []
        for r in tc['rounds']:
            full_inputs.extend([int(x) for x in r['in']])
            expected_outs.extend([int(x) for x in r['out']])
        
        try:
            out, ticks, w, h = sim.run(text, full_inputs, max_ticks=500_000)
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
    man_file = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/icfpc2026/tcp.man'
    res = test_all_cases(man_file)
    print('\nOVERALL RESULT:', 'PASS' if res else 'FAIL')
