import json
import sim

# Let's construct a python test runner that tests sudoku.man against all cases in spec_sudoku.json
def test_all_cases(man_file):
    spec = json.load(open('spec_sudoku.json'))
    text = open(man_file).read()
    
    all_passed = True
    for idx, case in enumerate(spec['publicTestData']):
        raw_in = []
        raw_out = []
        for r in case['rounds']:
            raw_in.extend([int(x) for x in r['in']])
            raw_out.extend([int(x) for x in r['out']])
            
        try:
            out, ticks, w, h = sim.run(text, raw_in, max_ticks=2_000_000, trace=0)
            passed = (out == raw_out)
            score = max(w, h)**2 * ticks
            print(f"Case {idx} ({case['name']}): {'PASS' if passed else 'FAIL'} | ticks={ticks}, score~{score}")
            if not passed:
                print(f"  Expected: {raw_out}")
                print(f"  Got:      {out}")
                all_passed = False
        except Exception as e:
            print(f"Case {idx} ({case['name']}): ERROR {e}")
            all_passed = False
            
    return all_passed

if __name__ == '__main__':
    import sys
    fn = sys.argv[1] if len(sys.argv) > 1 else 'sudoku.man'
    test_all_cases(fn)
