import json
import sim

# Let's test the complete Sudoku solver in a Python sim to verify all step counts and bitwise operations
def test_sim_standalone():
    spec = json.load(open('spec_sudoku.json'))
    for idx, case in enumerate(spec['publicTestData']):
        print(f"Case {idx} ({case['name']}):")
        rounds = case['rounds']
        raw_in = []
        raw_out = []
        for r in rounds:
            raw_in.extend([int(x) for x in r['in']])
            raw_out.extend([int(x) for x in r['out']])
        print(f"  Inputs count: {len(raw_in)}, expected outputs: {len(raw_out)}")

test_sim_standalone()
