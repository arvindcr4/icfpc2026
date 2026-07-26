import subprocess, sys

# Generate the complete brackets.man file

def generate():
    # Rooms layout:
    # I room: (0, 0, 2, 2)
    # O room: (4, 0, 6, 2)
    # M room (memory repeater): (8, 0, 16, 2)
    # main room: (0, 5, 20, 15)

    grid = """+-+ +-+ +--------+
|I| |O| |M       |
| | | | |@rNXsH< |
+-+ +-+ +--------+
 v   ^   ^      v 
 v   ^   ^      v 
+----------------+
|@rNX`0`s`1`NsH  |
+----------------+"""

    with open('/home/claude/icfpc2026/brackets.man', 'w') as f:
        f.write(grid.strip() + '\n')

    print("Generated brackets.man grid")

if __name__ == '__main__':
    generate()
