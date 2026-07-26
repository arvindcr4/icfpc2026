import sim

man_code = """
+-+ +-+
|I| |O|
+-+ +-+
 v   ^
 v   ^
+-----------------------+           +-----+
|@`27`b                 |           |@r s |
|>0 s m d|>------------>|v>-------->|v^  <|
|^      <|v             |^|         |^   v|
|        |              | |         |<v--<|
|        |              | |         |     |
|        |              | |         |     |
|        | <------------<-<|        +-----+
+-----------------------+
"""

try:
    g, w, h = sim.load_grid(man_code)
    print("Grid loaded OK, size:", w, "x", h)
    rooms = sim.find_rooms(g, w, h)
    print("Rooms found:", len(rooms), rooms)
    pipes = sim.trace_pipes(g, w, h, rooms)
    print("Pipes found:", len(pipes))
    for p in pipes:
        print("  ", p)
except Exception as e:
    import traceback
    traceback.print_exc()

