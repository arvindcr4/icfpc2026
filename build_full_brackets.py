import sys, subprocess, json
from run_all_tests import test_program

# Let's test a complete implementation of brackets.man
# We will lay out the instructions cleanly inside main room.

prog = """+-+ +-+ +---+
|I| |O| |M  |
+-+ +-+ +---+
 v   ^   ^ |
 v   ^   | v
+-----------+
|@rXb`0`M`1`|
|  v        |
| `0`sH     |
+-----------+"""

test_program(prog)
