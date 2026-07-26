import sim, subprocess, sys, json

# Generator for final brackets.man with @ spawn point in main room

def generate_brackets_man():
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
        "|@r` 1`W-X     v|",
        "|        v      |",
        "|   s<0  ` 1`NsH|",
        "+---------------+"
    ]
    return "\n".join(lines)

text = generate_brackets_man()
with open('/home/claude/icfpc2026/brackets.man', 'w') as f:
    f.write(text.strip() + '\n')

g, w, h = sim.load_grid(text.strip())
rooms = sim.find_rooms(g, w, h)
print('Rooms:', len(rooms))
men = []
for r in rooms:
    for y in range(r[1] + 1, r[3]):
        for x in range(r[0] + 1, r[2]):
            if g[y][x] == '@':
                men.append((x, y))
print('Men spawned at:', men)
