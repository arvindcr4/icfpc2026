import subprocess, sys, json, os

# Let's build brackets.man and run sim.py on all 9 public test cases!

prog = """+-+ +-+ +---+
|I| |O| |M  |
+-+ +-+ +---+
 v   ^   ^ |
 v   ^   | v
+----------+
|@rXb1s    |
|   v      |
|  0sH     |
+----------+"""

# Let's test basic sim loading
with open('/home/claude/icfpc2026/brackets.man', 'w') as f:
    f.write(prog.strip() + '\n')

print("Wrote brackets.man skeleton")
