import sim, subprocess, sys, json

# Build complete working Littleman brackets program generator

def build():
    # Rooms layout:
    # I: (0, 0, 2, 5)
    # O: (4, 0, 6, 5)
    # M: (8, 0, 15, 5)
    # main: (0, 8, 32, 24)

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
        "|   Nb`0`M`1`s. |",
        "|@r` 1`W-X      |",
        "|     v         |",
        "|   s<0  ` 1`NsH|",
        "+---------------+"
    ]
    code = "\n".join(lines).strip() + "\n"
    with open('/home/claude/icfpc2026/brackets.man', 'w') as f:
        f.write(code)

if __name__ == '__main__':
    build()
    print("Updated brackets.man")
