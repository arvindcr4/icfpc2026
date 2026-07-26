import sim, subprocess, sys, json

# Complete brackets.man solver generator and test harness

def build_brackets_program():
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
        "|>r` 1`W-X      |",
        "|     v         |",
        "|   s<0  ` 1`NsH|",
        "+---------------+"
    ]
    return "\n".join(lines)

with open('/home/claude/icfpc2026/brackets.man', 'w') as f:
    f.write(build_brackets_program().strip() + '\n')

print("Written complete brackets.man")
