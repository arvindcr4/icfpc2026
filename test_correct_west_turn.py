import sim, subprocess, sys, json

# Place '<' at index 10 (col 10) on row 13 so man turns WEST!

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
|@r ` 1`W-X    v|
|         v    v|
|Hs`0`s`1`N<    |
+---------------+"""

# Align line 13: index 10 must be '<'
lines = prog.strip().split('\n')
# line 13: |Hs`0`s`1`N<    |
# Index 0: |
# Index 1: H
# Index 2: s
# Index 3: `
# Index 4: 0
# Index 5: `
# Index 6: s
# Index 7: `
# Index 8: 1
# Index 9: `
# Index 10: N
# Index 11: <
# Let's shift row 13 so index 10 is '<'!
lines[13] = "|Hs`0`s`1`N<     |".ljust(17) # Wait! Let's build exact row 13 in python!

row13_chars = ['|'] + list("Hs`0`s`1`N<".rjust(10)) + ['|']
row13_str = "".join(row13_chars)
print("Row 13:", repr(row13_str), "len:", len(row13_str))

with open('/home/claude/icfpc2026/brackets.man', 'w') as f:
    f.write(prog.strip() + '\n')

out, ticks, w, h = sim.run(prog.strip(), [0], trace=25)
print("SUCCESS! Output:", out, "Ticks:", ticks, "w:", w, "h:", h)
