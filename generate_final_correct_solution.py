import sim, subprocess, sys, json

# Complete brackets solver with separated setup track and termination track

def build_brackets():
    m_room = [
        "+-+ +-+ +------+",
        "|I| |O| |M     |",
        "| | | | | v<s< |",
        "| | | | |>@rXv |",
        "| | | | |  vH  |",
        "+-+ +-+ +------+"
    ]

    pipes_connecting = [
        " v   ^   ^    v ",
        " v   ^   ^    v ",
        " v   ^   ^    v ",
        "+---------------+"
    ]

    r9  = "|v<............v|" # Top loop return track
    r10 = "|   b`0`M`1`s. v|" # Setup track for n > 0 (b, stack=0, pos=1, send pos to M)
    r11 = "|@r ` 1`W - X   |" # Entry row (r, compute n-1, X branch)
    r12 = "|        v      |" # South branch for n = 0
    r13 = "|  Hs`0`sN`1`<  |" # Termination track for n = 0

    lines = m_room + pipes_connecting + [r9, r10, r11, r12, r13, "+---------------+"]
    
    # Format all main room lines to exactly 17 chars
    for i in range(10, len(lines)-1):
        lines[i] = lines[i].ljust(17)
    lines[-1] = "+---------------+".ljust(17)

    return "\n".join(lines)

text = build_brackets()
with open('/home/claude/icfpc2026/brackets.man', 'w') as f:
    f.write(text.strip() + '\n')

g, w, h = sim.load_grid(text.strip())
rooms = sim.find_rooms(g, w, h)
print('Rooms:', len(rooms))
pipes = sim.trace_pipes(g, w, h, rooms)
print('Pipes:', len(pipes))
