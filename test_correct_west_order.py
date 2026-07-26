import sim, subprocess, sys, json

# Shift backticks on row 13 to avoid column 8 alignment

r9  = "|v<............v|"
r10 = "|   Nb`0`M`1`s.v|"
r11 = "|@r ` 1`W - X  v|"
r12 = "|          v   v|"
r13 = "|Hs`0`sN `1`<   |"

lines = [
    "+-+ +-+ +------+",
    "|I| |O| |M     |",
    "| | | | | s<   |",
    "| | | | |@rXv  |",
    "| | | | | vH   |",
    "+-+ +-+ +------+",
    " v   ^   ^    v ",
    " v   ^   ^    v ",
    "+---------------+",
    r9,
    r10,
    r11,
    r12,
    r13,
    "+---------------+"
]

text = "\n".join(lines)
with open('/home/claude/icfpc2026/brackets.man', 'w') as f:
    f.write(text.strip() + '\n')

g, w, h = sim.load_grid(text.strip())
rooms = sim.find_rooms(g, w, h)
print('Rooms:', len(rooms))
pipes = sim.trace_pipes(g, w, h, rooms)
print('Pipes:', len(pipes))

out, ticks, w, h = sim.run(text.strip(), [0], trace=30)
print("SUCCESS! Output:", out, "Ticks:", ticks, "w:", w, "h:", h)
