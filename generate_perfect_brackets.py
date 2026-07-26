import sim, subprocess, sys, json

# Generate complete brackets.man grid with east-facing loop entry track

def get_man_grid():
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
        "|@r` 1`W-X      |",
        "|     v         |",
        "|   s<0  ` 1`NsH|",
        "+---------------+"
    ]
    return "\n".join(lines)

with open('/home/claude/icfpc2026/brackets.man', 'w') as f:
    f.write(get_man_grid().strip() + '\n')

print("Generated brackets.man grid with loop entry track")
