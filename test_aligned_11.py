import sim, subprocess, sys, json

# Exact index 11 alignment for X, v, and <

r9  = "|v<............v|"
r10 = "|   Nb`0`M`1`s.v|"
r11 = "|@r ` 1`W - X  v|"
r12 = "|          v   v|"
r13 = "|Hs`0`s`1`N<    |"

# Index check:
# r11:
# Index 0: |
# Index 1: @
# Index 2: r
# Index 3:  
# Index 4: `
# Index 5:  
# Index 6: 1
# Index 7: `
# Index 8: W
# Index 9:  
# Index 10: -
# Index 11: X
# Index 12:  
# Index 13:  
# Index 14:  
# Index 15: v
# Index 16: |

# r12:
# Index 0: |
# Index 1..10: 10 spaces
# Index 11: v
# Index 12..14: 3 spaces
# Index 15: v
# Index 16: |

# r13:
# Index 0: |
# Index 1: H
# Index 2: s
# Index 3: `
# Index 4: 0
# Index 5: `
# Index 6: s
# Index 7: `
# Index 8: 1
# Index 9: `
# Index 10: N
# Index 11: <
# Index 12..15: 4 spaces
# Index 16: |

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

out, ticks, w, h = sim.run(text.strip(), [0], trace=25)
print("SUCCESS! Output:", out, "Ticks:", ticks, "w:", w, "h:", h)
