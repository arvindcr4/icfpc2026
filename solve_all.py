import subprocess
import json

def test_all():
    with open('subsetsum_spec.json') as f:
        spec = json.load(f)

    passes = 0
    total = len(spec['publicTestData'])
    
    for case in spec['publicTestData']:
        name = case['name']
        inp_str = " ".join(case['rounds'][0]['in'])
        exp_out_str = " ".join(case['rounds'][0]['out'])
        
        cmd = ["python3", "sim.py", "subsetsum.man", "--in", inp_str]
        res = subprocess.run(cmd, capture_output=True, text=True)
        out = res.stdout.strip()
        err = res.stderr.strip()
        
        status = "PASS" if out == exp_out_str else "FAIL"
        if status == "PASS":
            passes += 1
        print(f"[{status}] {name:<30} -> Got: '{out}' | Expected: '{exp_out_str}'")
        if status == "FAIL" and err:
            print(f"       Err: {err[:300]}")

    print(f"\nResult: {passes}/{total} passed")

test_all()
