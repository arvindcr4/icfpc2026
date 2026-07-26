import sim

man_code = """
+-+ +-+
|I| |O|
+-+ +-+
 v   ^
 v   ^
+---------------------------------------+           +-----+
|@27b v                                 |           |@r s |
|>0                                 s md|>--------->|v^  <|
|^                                    < |           |^   v|
|        |>r M r M r W 1 W { M          |<---------<|<v--<|
|        | M W 9 + M W                  |           +-----+
|        | M 3 / * M W 3 / + 18 +       |
|        | M                            |
|        |                              |
|        |                              |
|        |                              |
|        |                              |
|        |                              |
+---------------------------------------+
"""
try:
    g, w, h = sim.load_grid(man_code)
    rooms = sim.find_rooms(g, w, h)
    print("Rooms:", len(rooms), rooms)
    pipes = sim.trace_pipes(g, w, h, rooms)
    print("Pipes:", len(pipes))
    out, ticks, w, h = sim.run(man_code, [4, 5, 4], max_ticks=500, trace=0)
    print("Run finished! Ticks:", ticks, "Out len:", len(out), "Out:", out)
except Exception as e:
    import traceback
    traceback.print_exc()
