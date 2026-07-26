import sim, subprocess, sys

# Aligned backtick columns to avoid vertical backtick conflicts

prog = """+-+ +-+ +------+
|I| |O| |M     |
| | | | | s<   |
| | | | |@rXv  |
| | | | | vH   |
+-+ +-+ +------+
 v   ^   ^    v
 v   ^   ^    v
+---------------+
|   Nb`0`M`1`s. |
|@r` 1`W-X      |
|     v         |
|   s<0  ` 1`NsH|
+---------------+"""

with open('/home/claude/icfpc2026/test_col5_fixed.man', 'w') as f:
    f.write(prog.strip() + '\n')

out, ticks, w, h = sim.run(prog.strip(), [0], trace=30)
print("Output:", out, "Ticks:", ticks)
