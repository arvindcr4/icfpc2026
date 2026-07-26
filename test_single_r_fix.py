import sim, subprocess, sys, json

# Remove duplicate 'r' in main room row 11!

def make_brackets_clean():
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
        "|@r ` 1`W-X    v|",
        "|        v      |",
        "|   s<0  ` 1`NsH|",
        "+---------------+"
    ]
    return "\n".join(lines)

text = make_brackets_clean()
with open('/home/claude/icfpc2026/brackets.man', 'w') as f:
    f.write(text.strip() + '\n')

out, ticks, w, h = sim.run(text.strip(), [0], trace=25)
print("SUCCESS! Output:", out, "Ticks:", ticks, "w:", w, "h:", h)
