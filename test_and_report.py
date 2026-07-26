import sim, subprocess, sys, json

# Run all 9 public test cases against sim.py and report status

def verify_all():
    with open('/home/claude/icfpc2026/spec_brackets.json') as f:
        spec = json.load(f)
    public_tests = spec['publicTestData']

    with open('/home/claude/icfpc2026/brackets.man') as f:
        man_text = f.read()

    passed = 0
    total = len(public_tests)
    details = []

    for tc in public_tests:
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
            details.append((tc['name'], ok, out_str, exp_out, res.stderr))
        except subprocess.TimeoutExpired:
            details.append((tc['name'], False, "TIMEOUT", exp_out, "timeout > 5s"))

    print(f"\n--- VERIFICATION RESULTS ({passed}/{total}) ---")
    for name, ok, got, exp, err in details:
        st = "PASS" if ok else "FAIL"
        print(f"[{st}] {name}: got '{got}', expected '{exp}'")
        if not ok and err:
            print(f"      stderr: {err.strip()[:150]}")

    return passed, total

if __name__ == '__main__':
    verify_all()
