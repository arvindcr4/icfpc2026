import sim

# Main room: x=0..8
# Mem pipe: x=9..21 (13 cells)
# Mem room: x=22..28 (7 cells width)
man_code = """
+-+ +-+
|I| |O|
+-+ +-+
 v   ^
 v   ^
+-------+             +-----+
|@27b   |             |@r s |
|v>0s  m|>----------->|v^  <|
|^< a  d|^            |^   v|
|   <  <|<-----------<|<v--<|
+-------+             +-----+
"""

try:
    g, w, h = sim.load_grid(man_code)
    rooms = sim.find_rooms(g, w, h)
    print("Rooms found:", len(rooms), rooms)
    pipes = sim.trace_pipes(g, w, h, rooms)
    print("Pipes found:", len(pipes))
    for p in pipes:
        print("  ", p)
except Exception as e:
    import traceback
    traceback.print_exc()
