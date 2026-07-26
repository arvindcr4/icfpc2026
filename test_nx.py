import subprocess, sys

prog = """+-+ +-+ +---+
|I| |O| |M  |
+-+ +-+ +---+
 v   ^   ^ v
 v   ^   | v
+-----------+
|@rN X`0`sH |
|    v      |
+-----------+"""

with open('/home/claude/icfpc2026/test_nx.man', 'w') as f:
    f.write(prog.strip() + '\n')

cmd = [sys.executable, '/home/claude/icfpc2026/sim.py', '/home/claude/icfpc2026/test_nx.man', '--in', '0', '--trace', '10']
res = subprocess.run(cmd, capture_output=True, text=True)
print("Exit code:", res.returncode)
print("Stderr:\n", res.stderr)
print("Stdout:\n", res.stdout)
