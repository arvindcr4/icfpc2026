import sys
sys.path.append('/home/claude/icfpc2026')
import sim, json

# Let's write the complete sort.man content
prog = '''
+-+                  +-+
|I|                  |O|
+-+                  +-+
 v                    ^
 v                    ^
+-----------------------+         +-------+
|@r                      |>>>>>>>>>|r s   v|
|                        |<<<<<<<<<|^ < < <|
+-----------------------+         +-------+
'''

# Let's test
g, w, h = sim.load_grid(prog)
rooms = sim.find_rooms(g, w, h)
print("Rooms:", len(rooms), rooms)
pipes = sim.trace_pipes(g, w, h, rooms)
print("Pipes:", len(pipes))
for p in pipes:
    print(" ", p)
