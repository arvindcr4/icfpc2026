import sim

prog = """+-+ +-+ +---+
|I| |O| |M  |
+-+ +-+ +---+
 v   ^   ^ v
 v   ^   ^ v
+---------------+
|@`42`s.r.sH    |
+---------------+"""

g, w, h = sim.load_grid(prog.strip())
rooms = sim.find_rooms(g, w, h)
print('Rooms:', rooms)
out, ticks, w, h = sim.run(prog.strip(), [0])
print('Output:', out, 'Ticks:', ticks)
