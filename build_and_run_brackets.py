import subprocess, sys, json

# Full generator for brackets.man

# Let's design the layout of rooms:
# Room I: (0, 0, 2, 2)
# Room O: (4, 0, 6, 2)
# Room M: (8, 0, 16, 2) -- Memory repeater room
# Room main: (0, 5, 26, 12)

# Grid layout:
# Top row: I, O, M rooms
# Pipes from I to main, main to O, main to M (2-way)

def get_brackets_man():
    lines = [
        "+-+ +-+ +--------+",
        "|I| |O| |M       |",
        "| | | | |@rNXsH< |",
        "+-+ +-+ +--------+",
        " v   ^   ^      v ",
        " v   ^   ^      v ",
        "+----------------+",
        "|@rNX`0`s`1`NsH  |",
        "+----------------+"
    ]
    return "\n".join(lines)

man_text = get_brackets_man()
with open('/home/claude/icfpc2026/brackets.man', 'w') as f:
    f.write(man_text.strip() + '\n')

print("Wrote initial brackets.man")
