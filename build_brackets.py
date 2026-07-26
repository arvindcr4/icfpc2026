import subprocess, sys, json

# Let's draft a complete Littleman program for brackets
# Layout:
# Rooms:
# I: input room
# O: output room
# M: memory room for pos
# main: worker room

man_code = """
+-+ +-+ +-+
|I| |O| |M|
+-+ +-+ +-+
 v   ^   ^
 v   ^   v
+---------+
|@rM1     |
+---------+
"""

with open('/home/claude/icfpc2026/brackets.man', 'w') as f:
    f.write(man_code.strip() + '\n')

print("Written draft brackets.man")
