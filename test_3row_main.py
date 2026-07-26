import sim, subprocess, sys

# 3-row main room:
# row 8: north path for n > 0
# row 9: entry row with X branch
# row 10: south path for n = 0

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
|@r`1 `W-X      |
|     v         |
|   ` 0`s1NsH   |
+---------------+"""

with open('/home/claude/icfpc2026/brackets.man', 'w') as f:
    f.write(prog.strip() + '\n')

out, ticks, w, h = sim.run(prog.strip(), [0], trace=25)
print("Empty string test: Output:", out, "Ticks:", ticks)
