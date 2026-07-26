import sim

man_code = """
+-+ +-+
|I| |O|
+-+ +-+
 v   ^
 v   ^
+---------------------------------------+           +-----+
|  @`27`b   v                           |           |@r s |
|>0         >smd                        |>--------->|v^  <|
|^<            <                        |<---------<|<v--<|
|        |>r M r M r W `1` W { M v      |           +-----+
|        | v  M W `9` + M W <-----<     |
|        | >M `3` / * M W `3` / + `18` +|
|        |                              |
|        |                              |
|        |                              |
|        |                              |
|        |                              |
|        |                              |
+---------------------------------------+
"""
lines = man_code.strip().split('\n')
lines.insert(5, ' v   ^')
lines[6] = '+---------------------------------------+           +-----+'

try:
    g, w, h = sim.load_grid('\n'.join(lines))
    pipes = sim.trace_pipes(g, w, h, sim.find_rooms(g, w, h))
    print("Pipes:", len(pipes))
    out, ticks, w, h = sim.run('\n'.join(lines), [], max_ticks=500, trace=30)
    print("Run completed cleanly! Ticks:", ticks)
except Exception as e:
    import traceback
    traceback.print_exc()
