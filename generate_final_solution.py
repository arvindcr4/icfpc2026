import sim, subprocess, sys, json

# Generate complete brackets.man file

def build_brackets_man():
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
        "|@r`1 `W-X      |",
        "|     v         |",
        "|   ` 0`s` 1`NsH|",
        "+---------------+"
    ]
    return "\n".join(lines)

with open('/home/claude/icfpc2026/brackets.man', 'w') as f:
    f.write(build_brackets_man() + '\n')

print("Wrote brackets.man grid")
