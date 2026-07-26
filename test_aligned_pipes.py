import subprocess, sys

prog = """+-+ +-+ +---+
|I| |O| |M  |
| | | | |@r |
+-+ +-+ +---+
 v   ^   ^ ^
 v   ^   | |
+-----------+
|@`42`s.r.sH|
+-----------+"""

with open('/home/claude/icfpc2026/test_aligned.man', 'w') as f:
    f.write(prog.strip() + '\n')

cmd = [sys.executable, '/home/claude/icfpc2026/sim.py', '/home/claude/icfpc2026/test_aligned.man', '--in', '0', '--trace', '15']
res = subprocess.run(cmd, capture_output=True, text=True)
print("Exit code:", res.returncode)
print("Stderr:\n", res.stderr)
print("Stdout:\n", res.stdout)
