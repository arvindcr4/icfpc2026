import sim, subprocess, sys

# Fixed M room layout with turns

prog = """+-+ +-+ +---------+
|I| |O| |M        |
| | | | |  <s<    |
| | | | |@rX      |
| | | | |  vH     |
+-+ +-+ +---------+
 v   ^   ^       v
 v   ^   ^       v
+-----------------+
|@`42`s.r.`1`NsH  |
+-----------------+"""

with open('/home/claude/icfpc2026/test_turn.man', 'w') as f:
    f.write(prog.strip() + '\n')

out, ticks, w, h = sim.run(prog.strip(), [0], trace=30)
print("Output:", out, "Ticks:", ticks)
