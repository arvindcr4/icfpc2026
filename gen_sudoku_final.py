import json
import sim

man_code = """
+-+ +-+
|I| |O|
+-+ +-+
 v   ^
 v   ^
+---------------------------------------+           +-----+
|@`27`b                                 |           |@r s |
|v>0 s m d                              |>--------->|v^  <|
|^      <|v                             |^|         |^   v|
|        |>r M r M r W `1` W { M        | |         |<v--<|
|        | M W `9` + M W                | |         |     |
|        | M `3` / * M W `3` / + `18` + | |         |     |
|        | M                            | |         |     |
|        |                              | |         |     |
|        |                              | |         |     |
|        |                              | |         |     |
|        |<-----------------------------|<|<--------|<v--<|
+---------------------------------------+           +-----+
"""
lines = man_code.split('\n')
# Move +-----+ down 1 line to line 17 (y=18)
lines[16] = '|        |<----------------------------<|         |     |'
lines.append('+---------------------------------------+           +-----+')
padded = '\n'.join(lines)

try:
    g, w, h = sim.load_grid(padded)
    rooms = sim.find_rooms(g, w, h)
    print("Rooms found:", len(rooms), rooms)
    pipes = sim.trace_pipes(g, w, h, rooms)
    print("Pipes found:", len(pipes))
    for p in pipes:
        print("  ", p)
except Exception as e:
    import traceback
    traceback.print_exc()
