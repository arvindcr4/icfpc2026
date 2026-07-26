import json, subprocess, sys

# Load problem spec
with open('/home/claude/icfpc2026/spec_brackets.json') as f:
    spec = json.load(f)

public_tests = spec['publicTestData']

def run_test(prog_file, test_case):
    inp_str = " ".join(test_case['in'])
    exp_out = " ".join(test_case['out'])
    cmd = [sys.executable, '/home/claude/icfpc2026/sim.py', prog_file, '--in', inp_str]
    res = subprocess.run(cmd, capture_output=True, text=True)
    out_str = res.stdout.strip()
    passed = (out_str == exp_out) and (res.returncode == 0)
    return passed, out_str, exp_out, res.stderr

print(f"Loaded {len(public_tests)} public test cases.")
