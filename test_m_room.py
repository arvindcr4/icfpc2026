import subprocess, sys

prog = """
+-+ +-+ +--+
|I| |O| |M |
+-+ +-+ +--+
 v   ^   ^ v
 v   ^   v ^
+----------+
|@r1sH     |
+----------+
"""

# Let's test loading this layout in sim.py
with open('/home/claude/icfpc2026/test_layout.man', 'w') as f:
    f.write(prog.strip() + '\n')

cmd = [sys.executable, '/home/claude/icfpc2026/sim.py', '/home/claude/icfpc2026/test_layout.man', '--in', '1 40', '--trace', '10']
res = subprocess.run(cmd, capture_output=True, text=True)
print("Exit code:", res.returncode)
print("Stderr:\n", res.stderr)
print("Stdout:\n", res.stdout)
