import sim, subprocess, sys, json

# Matched width for all lines of main room (x0=0, x1=16, width=17)

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
|>r` 1`W-X     v|
|        v      |
|        `0`s`1`NsH
+---------------+"""

# Let's align all lines to 17 chars
lines = prog.strip().split('\n')
for i in range(len(lines)):
    lines[i] = lines[i].ljust(17)

# Fix bottom border of main room
lines[-1] = '+---------------+'.ljust(17)

text = "\n".join(lines)

with open('/home/claude/icfpc2026/brackets.man', 'w') as f:
    f.write(text + '\n')

g, w, h = sim.load_grid(text)
rooms = sim.find_rooms(g, w, h)
print('Rooms:', rooms)
pipes = sim.trace_pipes(g, w, h, rooms)
print('Pipes:', len(pipes))

out, ticks, w, h = sim.run(text, [0], trace=30)
print("Output:", out, "Ticks:", ticks)
