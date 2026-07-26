import sim, subprocess, sys

prog = """+-+ +-+ +------+
|I| |O| |M     |
| | | | |  s<   |
| | | | |@rXv  |
| | | | |  vH  |
+-+ +-+ +------+
 v   ^   ^    v
 v   ^   ^    v
+---------------+
|@`42`s.r.`1`NsH|
+---------------+"""

with open('/home/claude/icfpc2026/test_2x2.man', 'w') as f:
    f.write(prog.strip() + '\n')

out, ticks, w, h = sim.run(prog.strip(), [0], trace=30)
print("Output:", out, "Ticks:", ticks)
