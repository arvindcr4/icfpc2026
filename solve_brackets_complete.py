import sim, subprocess, sys, json

# Build complete working Littleman brackets program generator and verifier

def generate_and_test():
    with open('/home/claude/icfpc2026/spec_brackets.json') as f:
        spec = json.load(f)
    public_tests = spec['publicTestData']

    # Complete tested grid layout
    lines = [
        "+-+ +-+ +------+",
        "|I| |O| |M     |",
        "| | | | | s<   |",
        "| | | | |@rXv  |",
        "| | | | | vH   |",
        "+-+ +-+ +------+",
        " v   ^   ^    v ",
        " v   ^   ^    v ",
        "+---------------+",
        "|   Nb`0`M`1`s. |",
        "|@r` 1`W-X      |",
        "|     v         |",
        "|   s<0  ` 1`NsH|",
        "+---------------+"
    ]
    code = "\n".join(lines).strip() + "\n"
    with open('/home/claude/icfpc2026/brackets.man', 'w') as f:
        f.write(code)

    passed = 0
    total = len(public_tests)
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
            print(f"[{status}] {tc['name']}: got '{out_str}', expected '{exp_out}'")
        except subprocess.TimeoutExpired:
            print(f"[FAIL] {tc['name']}: TIMEOUT")

    print(f"\nPassed: {passed}/{total}")
    return passed == total

if __name__ == '__main__':
    generate_and_test()
