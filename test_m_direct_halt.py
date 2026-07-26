import sim, subprocess, sys

# Helper man receives value.
# If value > 0 (positive pos): X turns right (north) -> executes s (send pos back), turns around, loops!
# If value < 0 (negative signal -1): X turns left (south) -> executes H (halt)!

prog = """+-+ +-+ +---------+
|I| |O| |M        |
| | | | |   s<    |
| | | | |@rX      |
| | | | |  vH     |
+-+ +-+ +---------+
 v   ^   ^       v
 v   ^   ^       v
+-----------------+
|@`42`s.r.`1`NsH  |
+-----------------+"""

with open('/home/claude/icfpc2026/test_direct_halt.man', 'w') as f:
    f.write(prog.strip() + '\n')

out, ticks, w, h = sim.run(prog.strip(), [0], trace=30)
print("Output:", out, "Ticks:", ticks)
