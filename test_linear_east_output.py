import sim, subprocess, sys, json

# Linear east-moving output path for empty string (n = 0)

prog = """+-+ +-+ +------+
|I| |O| |M     |
| | | | | s<   |
| | | | |@rXv  |
| | | | | vH   |
+-+ +-+ +------+
 v   ^   ^    v
 v   ^   ^    v
+---------------+
|v<............v|
|   Nb`0`M`1`s.v|
|>r` 1`W-X      |
|        v      |
|       `0`s`1`NsH|
+---------------+"""

with open('/home/claude/icfpc2026/brackets.man', 'w') as f:
    f.write(prog.strip() + '\n')

from verify_all_cases import verify_all
verify_all()
