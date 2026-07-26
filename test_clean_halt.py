import subprocess, sys

# M room man halts when it receives -1
prog = """+-+ +-+ +-------+
|I| |O| |M      |
| | | | |@rNXsH<|
+-+ +-+ +-------+
 v   ^   ^     v
 v   ^   ^     v
+---------------+
|@rNX`0`s`1`NsH |
+---------------+"""

# main sends 0, then sends -1 to M pipe, then halts
with open('/home/claude/icfpc2026/test_clean.man', 'w') as f:
    f.write(prog.strip() + '\n')

cmd = [sys.executable, '/home/claude/icfpc2026/sim.py', '/home/claude/icfpc2026/test_clean.man', '--in', '0', '--trace', '15']
res = subprocess.run(cmd, capture_output=True, text=True)
print("Exit code:", res.returncode)
print("Stderr:\n", res.stderr)
print("Stdout:\n", res.stdout)
