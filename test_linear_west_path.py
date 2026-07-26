import sim, subprocess, sys, json

# Linear west-moving path for empty string (n = 0)

prog = """+-+ +-+ +------+
|I| |O| |M     |
| | | | | s<   |
| | | | |@rXv  |
| | | | | vH   |
+-+ +-+ +------+
 v   ^   ^    v
 v   ^   ^    v
+---------------+
|v<............v|
|   Nb`0`M`1`s.v|
|@r ` 1`W-X    v|
|         v    v|
|Hs`0`s`1`N<    |
+---------------+"""

with open('/home/claude/icfpc2026/brackets.man', 'w') as f:
    f.write(prog.strip() + '\n')

g, w, h = sim.load_grid(prog.strip())
rooms = sim.find_rooms(g, w, h)
print('Rooms:', len(rooms))
pipes = sim.trace_pipes(g, w, h, rooms)
print('Pipes:', len(pipes))

out, ticks, w, h = sim.run(prog.strip(), [0], trace=25)
print("SUCCESS! Output:", out, "Ticks:", ticks, "w:", w, "h:", h)
