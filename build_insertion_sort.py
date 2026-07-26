import sys
sys.path.append('/home/claude/icfpc2026')
import sim, json

# Build a compact Littleman program layout for insertion sort
# Rooms:
# I: Input room (top-left)
# O: Output room (top-right)
# Main: Central controller room
# R2: Storage Pipe ring (bottom-right)
# R1: N-counter pipe (bottom-left)

prog = '''+-+                  +-+
|I|                  |O|
+-+                  +-+
 v                    ^
 v                    ^
+-----------------------+         +-------+
|> >r                s v|>>>>>>>>>|r s   v|
|^> @>r       s b v    <|<<<<<<<<<|^ < < <|
|^ <          < < <     |         |       |
+-----------------------+         +-------+
          v   ^
          v   ^
       +-------+
       |r s   v|
       |^ < < <|
       +-------+'''

with open('/home/claude/icfpc2026/sort.man', 'w') as f:
    f.write(prog)

print("sort.man written.")

