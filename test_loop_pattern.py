import sim

man_code = """
+-+ +-+
|I| |O|
+-+ +-+
 v   ^
 v   ^
+---------+           +-----+
|@27bv    |           |@r s |
|>r  >sm d|>--------->|v^  <|
|^<      <|<|<--------|<v--<|
|        H|           +-----+
+---------+
"""
try:
    g, w, h = sim.load_grid(man_code)
    rooms = sim.find_rooms(g, w, h)
    print("Rooms:", rooms)
    pipes = sim.trace_pipes(g, w, h, rooms)
    print("Pipes:", len(pipes))
    out, ticks, w, h = sim.run(man_code, [], max_ticks=150, trace=35)
    print("Run completed cleanly! Ticks:", ticks)
except Exception as e:
    import traceback
    traceback.print_exc()
