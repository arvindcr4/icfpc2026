import sys
sys.path.append('/home/claude/icfpc2026')
import sim, json

# Complete, exact Littleman Selection Sort program for sort.man
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
