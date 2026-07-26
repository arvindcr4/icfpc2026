import sim, subprocess, sys, json

# Shift backticks on row 14 so col 8 is outside backticks!

r9  = "|v<............v|"
r10 = "|   Nb`0`M`1`s.v|"
r11 = "|@r ` 1`W - X  v|"
r12 = "|          v   v|"
r13 = "|Hs`0`s N`1`<   |"

lines = [
    "+-+ +-+ +------+",
    "|I| |O| |M     |",
    "| | | | | s<   |",
    "| | | | |@rXv  |",
    "| | | | | vH   |",
    "+-+ +-+ +------+",
    " v   ^   ^    v ",
    " v   ^   ^    v ",
    " v   ^   ^    v ",
    "+---------------+",
    r9,
    r10,
    r11,
    r12,
    r13,
    "+---------------+"
]

text = "\n".join(lines)
with open('/home/claude/icfpc2026/brackets.man', 'w') as f:
    f.write(text.strip() + '\n')

out, ticks, w, h = sim.run(text.strip(), [0], trace=30)
print("SUCCESS! Output:", out, "Ticks:", ticks, "w:", w, "h:", h)
