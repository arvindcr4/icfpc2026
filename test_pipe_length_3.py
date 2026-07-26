import sim, subprocess, sys, json

# Make input pipe 3 cells long so values are read perfectly!

prog = """+-+ +-+ +------+
|I| |O| |M     |
| | | | | s<   |
| | | | |@rXv  |
| | | | | vH   |
+-+ +-+ +------+
 v   ^   ^    v
 v   ^   ^    v
 v   ^   ^    v
+---------------+
|v<............v|
|   Nb`0`M`1`s.v|
|@r ` 1`W - X  v|
|          v   v|
|Hs`0`sN `1`<   |
+---------------+"""

text = prog.strip()
with open('/home/claude/icfpc2026/brackets.man', 'w') as f:
    f.write(text + '\n')

g, w, h = sim.load_grid(text)
rooms = sim.find_rooms(g, w, h)
print('Rooms:', len(rooms))
pipes = sim.trace_pipes(g, w, h, rooms)
print('Pipes lengths:', [len(p.cells) for p in pipes])

out, ticks, w, h = sim.run(text, [0], trace=30)
print("SUCCESS! Output:", out, "Ticks:", ticks, "w:", w, "h:", h)
