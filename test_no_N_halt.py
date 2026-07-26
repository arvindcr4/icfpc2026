import sim, subprocess, sys, json

# Remove N from row 13: A is already -1, so s directly sends -1 to pipe_M_in to halt M man!

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
        "|^ Hs`0`s `1`< <|", # row 13: s sends -1 to pipe_M_in, then `0`s sends 0 to pipe_O, then H halts!
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

from verify_final_pass import verify
verify()
