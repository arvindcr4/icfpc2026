import sim, subprocess, sys, json

with open('/home/claude/icfpc2026/spec_brackets.json') as f:
    spec = json.load(f)

public_tests = spec['publicTestData']

passed = 0
total = len(public_tests)

for idx, tc in enumerate(public_tests):
    inp_str = " ".join(tc['in'])
    exp_out = " ".join(tc['out'])
    cmd = [sys.executable, '/home/claude/icfpc2026/sim.py', '/home/claude/icfpc2026/brackets.man', '--in', inp_str]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        out_str = res.stdout.strip()
        ok = (res.returncode == 0) and (out_str == exp_out)
        if ok:
            passed += 1
        status = "OK" if ok else "FAIL"
        print(f"[{status}] Test {idx+1} ({tc['name']}): got '{out_str}', expected '{exp_out}'")
        if not ok:
            print(f"    stderr: {res.stderr.strip()[:200]}")
    except subprocess.TimeoutExpired:
        print(f"[FAIL] Test {idx+1} ({tc['name']}): TIMEOUT (>5s)")

print(f"\nFinal Result: {passed}/{total} passed.")
