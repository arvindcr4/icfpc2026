import sim, subprocess, sys, json

# Complete brackets.man generator and solver test

def make_brackets_man():
    # Rooms layout:
    # I: (0, 0, 2, 5)
    # O: (4, 0, 6, 5)
    # M: (8, 0, 15, 5)
    # main: (0, 8, 30, 18)

    # Let's construct a clean grid:
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
        "|@rNX`0`s`1`NsH |",
        "+---------------+"
    ]
    return "\n".join(lines)

with open('/home/claude/icfpc2026/brackets.man', 'w') as f:
    f.write(make_brackets_man() + '\n')

print("Wrote brackets.man grid")
