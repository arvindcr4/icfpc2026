import sim, subprocess, sys, json

# Aligned backticks at col 8

prog = """+-+ +-+ +------+
|I| |O| |M     |
| | | | | s<   |
| | | | |@rXv  |
| | | | | vH   |
+-+ +-+ +------+
 v   ^   ^    v
 v   ^   ^    v
+---------------+
|v<............v|
|   Nb`0`M`1`s.v|
|>r` 1`W-X      |
|        v      |
|        `0`s`1`NsH|
+---------------+"""

with open('/home/claude/icfpc2026/brackets.man', 'w') as f:
    f.write(prog.strip() + '\n')

from run_verification import public_tests
import run_verification

passed = 0
total = len(public_tests)

for idx, tc in enumerate(public_tests):
    inp_str = " ".join(tc['in'])
    exp_out = " ".join(tc['out'])
    cmd = [sys.executable, '/home/claude/icfpc2026/sim.py', '/home/claude/icfpc2026/brackets.man', '--in', inp_str]
    res = subprocess.run(cmd, capture_output=True, text=True)
    out_str = res.stdout.strip()
    ok = (res.returncode == 0) and (out_str == exp_out)
    if ok:
        passed += 1
    status = "OK" if ok else "FAIL"
    print(f"[{status}] {tc['name']}: got '{out_str}', expected '{exp_out}'")
    if not ok and res.stderr:
        print(f"    stderr: {res.stderr.strip()[:150]}")

print(f"\nFinal Result: {passed}/{total} public cases passed.")
