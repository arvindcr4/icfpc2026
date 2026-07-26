import json, sys
from sim import run

with open("reverse_spec.json") as f:
    spec = json.load(f)

with open("reverse.man") as f:
    code = f.read()

test_cases = spec["publicTestData"]
total_cases = 0
passed_cases = 0

for t_idx, test_case in enumerate(test_cases, 1):
    name = test_case["name"]
    rounds = test_case["rounds"]
    
    # Each test case is a sequence of rounds run in succession!
    # A test case carries 1 to 3 rounds.
    # In multi-round test cases, inputs from all rounds are passed to the program in sequence,
    # and the expected outputs from all rounds are produced in sequence.
    all_inputs = []
    all_expected = []
    for r in rounds:
        all_inputs.extend([int(x) for x in r["in"]])
        all_expected.extend([int(x) for x in r["out"]])
        
    total_cases += 1
    try:
        out, ticks, w, h = run(code, all_inputs, max_ticks=500000)
        if out == all_expected:
            passed_cases += 1
            print(f"PASS: Case {t_idx} '{name}' ({ticks} ticks, grid {w}x{h})")
        else:
            print(f"FAIL: Case {t_idx} '{name}'")
            print(f"  Got:      {out}")
            print(f"  Expected: {all_expected}")
    except Exception as e:
        print(f"ERROR: Case {t_idx} '{name}' -> {e}")

print(f"\nSummary: Passed {passed_cases}/{total_cases} public test cases.")
