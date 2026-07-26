import sys
sys.path.append('/home/claude/icfpc2026')
import sim, json

prog = '''+-+                  +-+
|I|                  |O|
+-+                  +-+
 v                    ^
 v                    ^
+-----------------------+         +-------+
|@>r       <           s|>>>>>>>>>|r s   v|
|  ^>     s b^         <|<<<<<<<<<|^ < < <|
+-----------------------+         +-------+
          v   ^
          v   ^
       +-------+
       |r s   v|
       |^ < < <|
       +-------+'''

with open('/home/claude/icfpc2026/sort.man', 'w') as f:
    f.write(prog)

g, w, h = sim.load_grid(prog)
rooms = sim.find_rooms(g, w, h)
print("Rooms:", len(rooms), rooms)
pipes = sim.trace_pipes(g, w, h, rooms)
print("Pipes:", len(pipes))
for p in pipes:
    print(" ", p)
