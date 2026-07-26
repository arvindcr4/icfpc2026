import sim, subprocess, sys, json

# Shift row 13 backticks to indices 12..14 so col 11 on row 13 is '<' (outside backticks!)

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
        "|   b`0`M`1`s. v|", # row 10
        "|@r ` 1`W - X  v|", # row 11
        "|^         v   v|", # row 12
        "|^ Hs`0`sN< `1`<|", # row 13
        "+---------------+"
    ]

    lines = m_room + pipes_connecting
    
    # Format all main room lines to exactly 17 chars
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
