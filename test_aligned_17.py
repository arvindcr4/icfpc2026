import sim, subprocess, sys, json

# Exact 17-char line width for all main room rows with X, v, and < at index 11

def make_grid_17():
    r9  = "|v<............v|"
    r10 = "|   Nb`0`M`1`s.v|"
    r11 = "|@r ` 1` W - X v|"
    r12 = "|            v v|"
    r13 = "||Hs`0`s`1`N < |" # Wait! Let's format r13 cleanly to 17 chars
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
    # Index 12:  
    # Index 13:  
    # Index 14:  
    # Index 15:  
    # Index 16: |
    r13 = "|Hs`0`s`1`N<    |"

    # Check r11:
    # Index 0: |
    # Index 1: @
    # Index 2: r
    # Index 3:  
    # Index 4: `
    # Index 5:  
    # Index 6: 1
    # Index 7: `
    # Index 8: W
    # Index 9: -
    # Index 10:  
    # Index 11: X
    # Index 12:  
    # Index 13:  
    # Index 14:  
    # Index 15: v
    # Index 16: |
    r11 = "|@r ` 1`W - X  v|"

    # Check r12:
    # Index 11: v
    r12 = "|           v  v|"

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
    return "\n".join(lines)

text = make_grid_17()
with open('/home/claude/icfpc2026/brackets.man', 'w') as f:
    f.write(text.strip() + '\n')

g, w, h = sim.load_grid(text.strip())
rooms = sim.find_rooms(g, w, h)
print('Rooms:', len(rooms))
pipes = sim.trace_pipes(g, w, h, rooms)
print('Pipes:', len(pipes))

out, ticks, w, h = sim.run(text.strip(), [0], trace=25)
print("SUCCESS! Output:", out, "Ticks:", ticks, "w:", w, "h:", h)
