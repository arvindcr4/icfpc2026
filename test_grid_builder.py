import subprocess, sys, json
from run_all_tests import test_program

# Let's construct brackets.man step by step

prog = """+-+ +-+ +---+
|I| |O| |M  |
+-+ +-+ +---+
 v   ^   ^ |
 v   ^   | v
+-----------+
|@r         |
+-----------+"""

test_program(prog)
