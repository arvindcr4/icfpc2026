import sim, subprocess, sys, json

# Opener logic straight ahead (east), closer logic on branch (north/south)

def make_brackets_program():
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
        "|>r` 1`W-X` 4`*s|",
        "|     v         |",
        "|   s<0  ` 1`NsH|",
        "+---------------+"
    ]
    return "\n".join(lines)

with open('/home/claude/icfpc2026/brackets.man', 'w') as f:
    f.write(make_brackets_program().strip() + '\n')

print("Generated brackets.man with opener logic straight ahead")
