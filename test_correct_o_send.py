import sim, subprocess, sys

# Correct pipe routing: s for output is placed at col 5 (under pipe_O at col 5)

prog = """+-+ +-+ +------+
|I| |O| |M     |
| | | | | s<   |
| | | | |@rXv  |
| | | | | vH   |
+-+ +-+ +------+
 v   ^   ^    v
 v   ^   ^    v
+---------------+
|@rN X          |
|    v          |
|    `0`s1NsH   |
+---------------+"""

with open('/home/claude/icfpc2026/test_o_correct.man', 'w') as f:
    f.write(prog.strip() + '\n')

out, ticks, w, h = sim.run(prog.strip(), [0], trace=30)
print("Output:", out, "Ticks:", ticks)
