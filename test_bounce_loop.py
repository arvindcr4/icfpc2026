import subprocess, sys

# Room M has a man @ that receives from pipe 1 and sends to pipe 2
# main sends 42 to pipe 1, then receives from pipe 2, then sends to O pipe!

prog = """+-+ +-+ +----+
|I| |O| |M   |
+-+ +-+ +----+
 v   ^   ^  |
 v   ^   |  v
+------------+
|@`42`s.r.sH |
+------------+"""

with open('/home/claude/icfpc2026/test_bounce_loop.man', 'w') as f:
    f.write(prog.strip() + '\n')

cmd = [sys.executable, '/home/claude/icfpc2026/sim.py', '/home/claude/icfpc2026/test_bounce_loop.man', '--in', '0', '--trace', '20']
res = subprocess.run(cmd, capture_output=True, text=True)
print("Exit code:", res.returncode)
print("Stderr:\n", res.stderr)
print("Stdout:\n", res.stdout)
