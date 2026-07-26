import sim, subprocess, sys

# Backticks aligned so no vertical conflicts exist

prog = """+-+ +-+ +------+
|I| |O| |M     |
| | | | | s<   |
| | | | |@rXv  |
| | | | | vH   |
+-+ +-+ +------+
 v   ^   ^    v
 v   ^   ^    v
+---------------+
|@r`1 `W-X      |
|     v         |
|   ` 0`s1NsH   |
+---------------+"""

with open('/home/claude/icfpc2026/test_sub1_fixed.man', 'w') as f:
    f.write(prog.strip() + '\n')

out, ticks, w, h = sim.run(prog.strip(), [0], trace=20)
print("Output:", out, "Ticks:", ticks)
