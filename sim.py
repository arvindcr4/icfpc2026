#!/usr/bin/env python3
"""Littleman (.man) simulator — ICFP Contest 2026.

Best-effort local interpreter so programs can be iterated without spending
submissions. It implements rooms, men, pipes, I/O rooms and the whole documented
instruction set except the LM-75 display.

  python3 sim.py prog.man --in "4"            # space-separated input ints
  python3 sim.py prog.man --in-file cases.txt
  python3 sim.py prog.man --in "0" --trace 40 # show the first 40 ticks

Exit status is 0 when the run ends cleanly. Output integers go to stdout, one per
line; diagnostics go to stderr.

THIS IS NOT THE JUDGE. It is a reimplementation from the language reference; when
it disagrees with the real judge, the judge is right. Two rules it *does* enforce
because they cost us real submissions:
  * a pipe must START with an arrowhead whose backward cell is on the source room
    border, and END at an arrowhead whose forward cell is on another room border
  * backticks pair down COLUMNS as well as along rows; a non-digit between a
    vertical pair is a load error
"""
import sys, argparse

WALL = set('+-|')
ARROW = {'>': (1, 0), '<': (-1, 0), 'v': (0, 1), 'V': (0, 1), '^': (0, -1)}
DIRNAME = {(1, 0): 'E', (-1, 0): 'W', (0, 1): 'S', (0, -1): 'N'}


class LoadError(Exception):
    pass


class RunError(Exception):
    pass


def load_grid(text):
    lines = text.split('\n')
    while lines and lines[-1] == '':
        lines.pop()
    w = max((len(l) for l in lines), default=0)
    return [list(l.ljust(w)) for l in lines], w, len(lines)


# Ordinary rooms are drawn with '-' and '|'. LM-75 DISPLAY rooms use '=' and ':' for the same
# job — confirmed against the accepted plotter and snake programs, both of which draw their
# display that way. Treating ':'/'=' as ordinary cells makes every pipe that legitimately
# reaches a display report a bogus "pipe hit ':'" load error.
HBORD = ('-', '=')
VBORD = ('|', ':')


def find_rooms(g, w, h):
    """Return list of rooms as (x0,y0,x1,y1) inclusive borders."""
    rooms = []
    for y in range(h):
        for x in range(w):
            if g[y][x] != '+':
                continue
            # top-left corner? scan right along a horizontal border to another '+'
            x1 = None
            for xx in range(x + 1, w):
                if g[y][xx] in HBORD:
                    continue
                if g[y][xx] == '+':
                    x1 = xx
                break
            if x1 is None or x1 == x + 1 and False:
                continue
            y1 = None
            for yy in range(y + 1, h):
                if g[yy][x] in VBORD:
                    continue
                if g[yy][x] == '+':
                    y1 = yy
                break
            if y1 is None:
                continue
            if g[y1][x1] != '+':
                continue
            ok = all(g[y1][xx] in HBORD for xx in range(x + 1, x1)) and \
                 all(g[yy][x1] in VBORD for yy in range(y + 1, y1))
            if not ok:
                continue
            if any(r[0] <= x and x <= r[2] and r[1] <= y <= r[3] for r in rooms):
                continue
            rooms.append((x, y, x1, y1))
    return rooms


def on_border(room, x, y):
    x0, y0, x1, y1 = room
    return (x0 <= x <= x1 and y0 <= y <= y1) and (x in (x0, x1) or y in (y0, y1))


def inside(room, x, y):
    x0, y0, x1, y1 = room
    return x0 < x < x1 and y0 < y < y1


class Pipe:
    def __init__(self, cells, src, dst):
        self.cells = cells                 # ordered source -> destination
        self.src, self.dst = src, dst
        self.slots = [None] * len(cells)

    def __repr__(self):
        return f"Pipe({self.cells[0]}->{self.cells[-1]}, len={len(self.cells)})"


def trace_pipes(g, w, h, rooms):
    pipes = []
    seen = set()
    for y in range(h):
        for x in range(w):
            c = g[y][x]
            if c not in ARROW or (x, y) in seen:
                continue
            d = ARROW[c]
            bx, by = x - d[0], y - d[1]
            src = next((r for r in rooms if on_border(r, bx, by)), None)
            if src is None:
                continue                    # not a pipe start; maybe a direction op in a room
            if any(inside(r, x, y) for r in rooms):
                continue
            cells, cx, cy, cd = [], x, y, d
            while True:
                if not (0 <= cx < w and 0 <= cy < h):
                    raise LoadError(f"pipe from ({x},{y}) ran off the grid")
                ch = g[cy][cx]
                cells.append((cx, cy))
                if ch in ARROW:
                    cd = ARROW[ch]
                fx, fy = cx + cd[0], cy + cd[1]
                dst = next((r for r in rooms if on_border(r, fx, fy) and r is not src), None)
                if ch in ARROW and dst is not None:
                    if len(cells) < 2:
                        raise LoadError(f"pipe at ({x},{y}) is a single cell")
                    p = Pipe(cells, src, dst)
                    pipes.append(p)
                    seen.update(cells)
                    break
                cx, cy = fx, fy
                nxt = g[cy][cx] if (0 <= cx < w and 0 <= cy < h) else ' '
                if nxt in ('-', '|'):
                    want = '-' if cd[1] == 0 else '|'
                    if nxt != want:
                        raise LoadError(f"pipe body {nxt!r} wrong for direction at ({cx},{cy})")
                elif nxt in ARROW:
                    pass
                else:
                    raise LoadError(f"pipe from ({x},{y}) hit {nxt!r} at ({cx},{cy})")
    return pipes


def check_backticks(g, w, h):
    for y in range(h):
        ticks = [x for x in range(w) if g[y][x] == '`']
        for i in range(0, len(ticks) - 1, 2):
            for x in range(ticks[i] + 1, ticks[i + 1]):
                if not (g[y][x].isdigit() or g[y][x] == ' '):
                    raise LoadError(f"expected a digit or a space between backticks, "
                                    f"but found {g[y][x]!r} at ({x}, {y})")
    for x in range(w):
        ticks = [y for y in range(h) if g[y][x] == '`']
        for i in range(0, len(ticks) - 1, 2):
            for y in range(ticks[i] + 1, ticks[i + 1]):
                if not (g[y][x].isdigit() or g[y][x] == ' '):
                    raise LoadError(f"expected a digit or a space between backticks, "
                                    f"but found {g[y][x]!r} at ({x}, {y}) [vertical pair]")


class Man:
    __slots__ = ('x', 'y', 'd', 'A', 'B', 'BP', 'room', 'alive', 'lit', 'blocked')

    def __init__(self, x, y, room):
        self.x, self.y, self.d = x, y, (1, 0)
        self.A = self.B = self.BP = 0
        self.room, self.alive, self.lit = room, True, None
        self.blocked = False


def run(text, inputs, max_ticks=2_000_000, trace=0):
    g, w, h = load_grid(text)
    check_backticks(g, w, h)
    rooms = find_rooms(g, w, h)
    if not rooms:
        raise LoadError("no rooms found")
    pipes = trace_pipes(g, w, h, rooms)
    # '+', '-' and '|' are BOTH wall glyphs and the add/sub/or instructions. Whether a cell
    # is a wall depends on it being on a room border, never on the character alone.
    borders = set()
    for (x0, y0, x1, y1) in rooms:
        for xx in range(x0, x1 + 1):
            borders.add((xx, y0)); borders.add((xx, y1))
        for yy in range(y0, y1 + 1):
            borders.add((x0, yy)); borders.add((x1, yy))

    def room_of(x, y):
        return next((r for r in rooms if inside(r, x, y)), None)

    inroom = outroom = None
    for r in rooms:
        cells = [(x, y) for y in range(r[1] + 1, r[3]) for x in range(r[0] + 1, r[2])]
        vals = {g[y][x] for x, y in cells}
        if vals == {'I'}:
            inroom = r
        elif vals == {'O'}:
            outroom = r

    men = []
    for r in rooms:
        for y in range(r[1] + 1, r[3]):
            for x in range(r[0] + 1, r[2]):
                if g[y][x] == '@':
                    men.append(Man(x, y, r))

    out, pending = [], list(inputs)
    inpipe = next((p for p in pipes if p.src is inroom), None) if inroom else None
    outpipe = next((p for p in pipes if p.dst is outroom), None) if outroom else None

    def near(m, incoming):
        best, bestkey = None, None
        for p in pipes:
            if incoming and p.dst is not m.room:
                continue
            if not incoming and p.src is not m.room:
                continue
            cx, cy = (p.cells[-1] if incoming else p.cells[0])
            key = (abs(cx - m.x) + abs(cy - m.y), cy, cx)
            if bestkey is None or key < bestkey:
                best, bestkey = p, key
        return best

    ticks = 0
    while ticks < max_ticks and any(m.alive for m in men):
        ticks += 1
        # 1. pipes shift
        for p in pipes:
            for i in range(len(p.slots) - 1, 0, -1):
                if p.slots[i] is None and p.slots[i - 1] is not None:
                    p.slots[i], p.slots[i - 1] = p.slots[i - 1], None
        # 2. I/O
        if outpipe and outpipe.slots[-1] is not None:
            out.append(outpipe.slots[-1]); outpipe.slots[-1] = None
        if inpipe and pending and inpipe.slots[0] is None:
            inpipe.slots[0] = pending.pop(0)
        # 3. execute
        for m in men:
            if not m.alive:
                continue
            c = g[m.y][m.x]
            blocked = False
            if c == '`':
                if m.lit is None:
                    m.lit = ''
                else:
                    if m.lit.strip():
                        m.A = int(m.lit)
                    m.lit = None
            elif m.lit is not None:
                if c.isdigit():
                    m.lit += c
                elif c == ' ':
                    pass
                else:
                    raise LoadError(f"non-digit {c!r} inside literal at ({m.x},{m.y})")
            elif c.isdigit():
                m.A = int(c)
            elif c == 'M':
                m.B = m.A
            elif c == 'W':
                m.A, m.B = m.B, m.A
            elif c == '+':
                m.A = m.A + m.B
            elif c == '-':
                m.A = m.A - m.B
            elif c == '*':
                m.A = m.A * m.B
            elif c == '%':
                m.A = 0 if m.B == 0 else m.A - m.B * (m.A // m.B)
            elif c == '/':
                if m.B == 0:
                    m.B, m.A = m.A, 0
                else:
                    q = m.A // m.B; r = m.A - q * m.B; m.A, m.B = q, r
            elif c == 'N':
                m.A = -m.A
            elif c == '&':
                m.A &= m.B
            elif c == '|':
                m.A |= m.B
            elif c == '~':
                m.A ^= m.B
            elif c == '{':
                m.A = 0 if not (0 <= m.B <= 63) else m.A << m.B
            elif c == '}':
                m.A = 0 if m.B < 0 else (m.A >> min(m.B, 63))
            elif c in ARROW:
                m.d = ARROW[c]
            elif c == 'X':
                if m.A > 0:   m.d = (-m.d[1], m.d[0])
                elif m.A < 0: m.d = (m.d[1], -m.d[0])
            elif c == 'b':
                m.BP = m.A
            elif c == 'm':
                m.BP -= 1
            elif c == 'd':
                if m.BP > 0: m.d = (-m.d[1], m.d[0])
            elif c == 'a':
                if m.BP > 0: m.d = (m.d[1], -m.d[0])
            elif c == ']':
                m.BP >>= 1
            elif c == 'x':
                m.d = (-m.d[1], m.d[0]) if (m.BP & 1) else (m.d[1], -m.d[0])
            elif c == 'q':
                p = near(m, True)
                if p is None: raise RunError('no-pipe')
                m.BP = sum(1 for s in p.slots if s is not None)
            elif c in 'sS':
                ps = [p for p in pipes if p.src is m.room] if c == 'S' else [near(m, False)]
                if not ps or ps[0] is None: raise RunError('no-pipe')
                if all(p.slots[0] is None for p in ps):
                    for p in ps: p.slots[0] = m.A
                else:
                    blocked = True
            elif c in 'rRU':
                cands = [p for p in pipes if p.dst is m.room]
                if not cands: raise RunError('no-pipe')
                if c == 'r':
                    cands = [near(m, True)]
                ready = [p for p in cands if p.slots[-1] is not None]
                if not ready:
                    blocked = True
                else:
                    ready.sort(key=lambda p: (p.cells[-1][1], p.cells[-1][0]))
                    p = ready[0]; m.A = p.slots[-1]; p.slots[-1] = None
                    if c == 'U':
                        ex, ey = p.cells[-1]
                        m.d = (1, 0) if ex < m.x else (-1, 0) if ex > m.x else ((0, 1) if ey < m.y else (0, -1))
            elif c == 'H':
                m.alive = False
            elif c in ('.', ' ', '@'):
                pass
            elif c in 'IO':
                pass
            else:
                raise RunError(f"bad-op {c!r} at ({m.x},{m.y})")
            if trace and ticks <= trace:
                print(f"  t{ticks:<5} ({m.x:>3},{m.y:<3}) {c!r:<5} A={m.A:<12} B={m.B:<12} BP={m.BP}",
                      file=sys.stderr)
            m.blocked = blocked
        # 4. move
        for m in men:
            if m.alive and not m.blocked:
                nx, ny = m.x + m.d[0], m.y + m.d[1]
                if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in borders:
                    raise RunError(f"wall at ({nx},{ny}) tick {ticks}")
                m.x, m.y = nx, ny
    # drain the output pipe
    if outpipe:
        for _ in range(len(outpipe.slots) + 2):
            if outpipe.slots[-1] is not None:
                out.append(outpipe.slots[-1]); outpipe.slots[-1] = None
            for i in range(len(outpipe.slots) - 1, 0, -1):
                if outpipe.slots[i] is None and outpipe.slots[i - 1] is not None:
                    outpipe.slots[i], outpipe.slots[i - 1] = outpipe.slots[i - 1], None
    return out, ticks, w, h


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('prog')
    ap.add_argument('--in', dest='inp', default='')
    ap.add_argument('--in-file')
    ap.add_argument('--trace', type=int, default=0)
    ap.add_argument('--max-ticks', type=int, default=2_000_000)
    a = ap.parse_args()
    text = open(a.prog).read()
    raw = open(a.in_file).read() if a.in_file else a.inp
    inputs = [int(t) for t in raw.split()] if raw.strip() else []
    try:
        out, ticks, w, h = run(text, inputs, a.max_ticks, a.trace)
    except (LoadError, RunError) as e:
        print(f"{type(e).__name__}: {e}", file=sys.stderr)
        sys.exit(1)
    print(' '.join(str(v) for v in out))
    print(f"[{w}x{h}  area2={max(w,h)**2}  ticks={ticks}  score~{max(w,h)**2*ticks}]",
          file=sys.stderr)


if __name__ == '__main__':
    main()
