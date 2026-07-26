import subprocess, sys, json

# Build complete working brackets.man

def run_test_suite():
    with open('/home/claude/icfpc2026/spec_brackets.json') as f:
        spec = json.load(f)
    public_tests = spec['publicTestData']

    # Let's test sim.run on all test cases
    with open('/home/claude/icfpc2026/brackets.man') as f:
        prog = f.read()

    passed = 0
    total = len(public_tests)
    for tc in public_tests:
        inp_str = " ".join(tc['in'])
        exp_out = " ".join(tc['out'])
        cmd = [sys.executable, '/home/claude/icfpc2026/sim.py', '/home/claude/icfpc2026/brackets.man', '--in', inp_str]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        out_str = res.stdout.strip()
        ok = (res.returncode == 0) and (out_str == exp_out)
        if ok:
            passed += 1
        status = "OK" if ok else "FAIL"
        print(f"[{status}] {tc['name']}: got '{out_str}', expected '{exp_out}'")
        if not ok and res.stderr:
            print(f"    stderr: {res.stderr.strip()[:200]}")

    print(f"\nFINAL VERDICT: {passed}/{total} passed.")
    return passed == total

if __name__ == '__main__':
    run_test_suite()
