import sim, subprocess, sys, json

# Completely separated setup loopback (row 12) and termination track (row 13)

def build_full_grid():
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
        "+---------------+",
        "|v<............v|", # row 9
        "|   b`0`M`1`s. v|", # row 10 (setup track for n > 0)
        "|@r ` 1`W - X  v|", # row 11 (entry row & X branch)
        "|^<............<|", # row 12 (setup loopback track, returns to @r at index 1!)
        "|  Hs`0`s `1`N <|", # row 13 (termination track)
        "+---------------+"
    ]

    lines = m_room + pipes_connecting
    
    for i in range(9, len(lines)-1):
        lines[i] = lines[i].ljust(17)
    lines[-1] = "+---------------+".ljust(17)

    return "\n".join(lines)

text = build_full_grid()
with open('/home/claude/icfpc2026/brackets.man', 'w') as f:
    f.write(text.strip() + '\n')

g, w, h = sim.load_grid(text.strip())
rooms = sim.find_rooms(g, w, h)
print('Rooms:', len(rooms))
pipes = sim.trace_pipes(g, w, h, rooms)
print('Pipes:', len(pipes))

from verify_final_pass import verify
verify()
