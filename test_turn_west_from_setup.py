import sim, subprocess, sys, json

# Shift row 14 backticks to indices 11..13 so col 10 is outside backticks!

r9  = "|v<............v|"
r10 = "|   Nb`0`M`1`s.v|"
r11 = "|@r ` 1`W - X  v|"
r12 = "|          v   v|"
r13 = "|Hs`0`s N  `1`<<|"

lines = [
    "+-+ +-+ +------+",
    "|I| |O| |M     |",
    "| | | | | s<   |",
    "| | | | |@rXv  |",
    "| | | | | vH   |",
    "+-+ +-+ +------+",
    " v   ^   ^    v ",
    " v   ^   ^    v ",
    " v   ^   ^    v ",
    "+---------------+",
    r9,
    r10,
    r11,
    r12,
    r13,
    "+---------------+"
]

text = "\n".join(lines)
with open('/home/claude/icfpc2026/brackets.man', 'w') as f:
    f.write(text.strip() + '\n')

from run_verification import public_tests

passed = 0
total = len(public_tests)

for idx, tc in enumerate(public_tests):
    inp_str = " ".join(tc['in'])
    exp_out = " ".join(tc['out'])
    cmd = [sys.executable, '/home/claude/icfpc2026/sim.py', '/home/claude/icfpc2026/brackets.man', '--in', inp_str]
    res = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
    out_str = res.stdout.strip()
    ok = (res.returncode == 0) and (out_str == exp_out)
    if ok:
        passed += 1
    status = "OK" if ok else "FAIL"
    print(f"[{status}] {tc['name']}: got '{out_str}', expected '{exp_out}'")

print(f"\nFinal Result: {passed}/{total} public cases passed.")
