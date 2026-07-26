import sim, subprocess, sys

# Helper man receives value. If value is -1 (negative), it halts!
# If value >= 0, it sends value back to main and loops.

prog = """+-+ +-+ +---------+
|I| |O| |M        |
| | | | |@rNXs.H  |
| | | | |   ^<    |
+-+ +-+ +---------+
 v   ^   ^       v
 v   ^   ^       v
+-----------------+
|@`42`s.r.`1`NsH  |
+-----------------+"""

# main sends 42 to M, receives 42 back, then sends -1 to M, then sends 42 to O, then halts!

with open('/home/claude/icfpc2026/test_halt.man', 'w') as f:
    f.write(prog.strip() + '\n')

out, ticks, w, h = sim.run(prog.strip(), [0], trace=25)
print("Output:", out, "Ticks:", ticks)
