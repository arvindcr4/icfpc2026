import sim, subprocess, sys

prog = """+-+ +-+ +------+
|I| |O| |M     |
| | | | | s<   |
| | | | |@rXv  |
| | | | | vH   |
+-+ +-+ +------+
 v   ^   ^    v
 v   ^   ^    v
+---------------+
|@`42`s.r.`1`NsH|
+---------------+"""

with open('/home/claude/icfpc2026/test_2x2_fixed.man', 'w') as f:
    f.write(prog.strip() + '\n')

text = prog.strip()
g, w, h = sim.load_grid(text)
rooms = sim.find_rooms(g, w, h)
print('Rooms:', rooms)

out, ticks, w, h = sim.run(text, [0], trace=30)
print("Output:", out, "Ticks:", ticks)
