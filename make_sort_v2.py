import sys
sys.path.append('/home/claude/icfpc2026')
import sim, json

prog = '''+-+                  +-+
|I|                  |O|
+-+                  +-+
 v                    ^
 v                    ^
+-----------------------+
|@                      |
|                       |
+-----------------------+
    v   ^        v   ^   
    v   ^        v   ^   
+-------+    +-------+   
|r s   v|    |r s   v|   
|^ < < <|    |^ < < <|   
+-------+    +-------+   '''

g, w, h = sim.load_grid(prog)
rooms = sim.find_rooms(g, w, h)
print("Rooms:", len(rooms), rooms)
pipes = sim.trace_pipes(g, w, h, rooms)
print("Pipes:", len(pipes))
for p in pipes:
    print(" ", p)
