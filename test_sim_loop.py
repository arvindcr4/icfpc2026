import sim

# Line 10:
# x=8: '|'
# x=9: '<'
# x=10..26: '-'
# x=27: '<'
# x=28: '|'
man_code = """
+-+ +-+
|I| |O|
+-+ +-+
 v   ^
 v   ^
+-------+                   +-----+
|@27b   |                   |@r s |
|v>0s  m|>----------------->|v^  <|
|^< a  d|^                  |^   v|
|   <  <|<-----------------<|<v--<|
+-------+                   +-----+
"""

try:
    g, w, h = sim.load_grid(man_code)
    print("Grid w, h:", w, h)
    rooms = sim.find_rooms(g, w, h)
    print("Rooms found:", len(rooms), rooms)
    pipes = sim.trace_pipes(g, w, h, rooms)
    print("Pipes found:", len(pipes))
    for p in pipes:
        print("  ", p)
except Exception as e:
    import traceback
    traceback.print_exc()
