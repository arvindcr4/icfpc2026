import sim, subprocess, sys, json

# Add 'v' at end of row 9 and '<' on row 10 to turn back into loop!

prog = """+-+ +-+ +------+
|I| |O| |M     |
| | | | | s<   |
| | | | |@rXv  |
| | | | | vH   |
+-+ +-+ +------+
 v   ^   ^    v
 v   ^   ^    v
+---------------+
|   Nb`0`M`1`s.v|
|@r` 1`W-X     <|
|     v         |
|   s<0  ` 1`NsH|
+---------------+"""

with open('/home/claude/icfpc2026/brackets.man', 'w') as f:
    f.write(prog.strip() + '\n')

from solve_brackets_complete import generate_and_test
generate_and_test()
