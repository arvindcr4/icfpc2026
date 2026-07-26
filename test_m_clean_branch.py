import sim, subprocess, sys

# Test M room man termination on negative signal

prog = """+-+ +-+ +---------+
|I| |O| |M        |
| | | | |   s<    |
| | | | |@rX      |
| | | | |  vH     |
+-+ +-+ +---------+
 v   ^   ^       v
 v   ^   ^       v
+-----------------+
|@`42`s.r.s`1`NsH |
+-----------------+"""

with open('/home/claude/icfpc2026/test_clean_b.man', 'w') as f:
    f.write(prog.strip() + '\n')

cmd = [sys.executable, '/home/claude/icfpc2026/sim.py', '/home/claude/icfpc2026/test_clean_b.man', '--in', '0', '--trace', '30']
res = subprocess.run(cmd, capture_output=True, text=True)
print("Exit code:", res.returncode)
print("Stderr:\n", res.stderr)
print("Stdout:\n", res.stdout)
