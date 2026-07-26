import sim

with open('/home/claude/icfpc2026/brackets.man') as f:
    text = f.read()

out, ticks, w, h = sim.run(text, [0])
print(f"Empty String Test: out={out}, ticks={ticks}, w={w}, h={h}")
