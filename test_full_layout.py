import subprocess, sys

prog = """+-+ +-+ +-------+
|I| |O| |M      |
| | | | |@r.s.. |
+-+ +-+ +-------+
 v   ^   ^     v
 v   ^   ^     v
 v   ^   ^     v
+---------------+
|@rNX`0`sH      |
|   v           |
|   Nb`0`M`1`   |
+---------------+"""

with open('/home/claude/icfpc2026/brackets.man', 'w') as f:
    f.write(prog.strip() + '\n')

import gen_sol
gen_sol.run_tests()
