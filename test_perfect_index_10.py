import sim, subprocess, sys, json

# Exact index 10 alignment on rows 11, 12, 13

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
|          v   v|
|  Hs`0`s`1`N<  |
+---------------+"""

# Let's inspect line indices:
# Row 11: |@r ` 1`W-X    v|
# Index 0: |
# Index 1: @
# Index 2: r
# Index 3: ` `
# Index 4: ` `
# Index 5: `1`
# Index 6: ` `
# Index 7: `W`
# Index 8: `-`
# Index 9: `X`
# Index 10: ` `
# Index 11: ` `
# Index 12: ` `
# Index 13: ` `
# Index 14: ` `
# Index 15: `v`
# Index 16: |

# Wait! On row 11 above: `W` is at 7, `-` is at 8, `X` is at 9!
# So `X` is at Index 9!
# Therefore, `v` on row 12 must be at Index 9!
# And `<` on row 13 must be at Index 9!

row11 = "|@r ` 1`W-X     v|".ljust(17)
row12 = "|         v     v|".ljust(17)
row13 = "|  Hs`0`s`1`N<   |".ljust(17)

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
    "|v<............v|",
    "|   Nb`0`M`1`s.v|",
    row11,
    row12,
    row13,
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

out, ticks, w, h = sim.run(text.strip(), [0], trace=25)
print("SUCCESS! Output:", out, "Ticks:", ticks, "w:", w, "h:", h)
