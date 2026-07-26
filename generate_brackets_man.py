import subprocess, sys, json
from run_all_tests import test_program

# Let's construct the complete brackets.man program!
# Layout:
# Rooms:
# I: (0, 0, 2, 2)
# O: (4, 0, 6, 2)
# M: (8, 0, 16, 2)  - Memory repeater room
# main: (0, 5, 16, 12) - main worker room

man_text = """+-+ +-+ +--------+
|I| |O| |M       |
| | | | |@r.s.<  |
+-+ +-+ +--------+
 v   ^   ^      v
 v   ^   ^      v
 v   ^   ^      v
+----------------+
|@rNX`0`sH       |
|   v            |
|   Nb`0`M`1`s...|
+----------------+"""

with open('/home/claude/icfpc2026/brackets.man', 'w') as f:
    f.write(man_text.strip() + '\n')

test_program(man_text)
