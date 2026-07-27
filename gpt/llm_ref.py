#!/usr/bin/env python3
"""Reference model for the ICFP-2026 `little-little-man` (LLM) problem.

Given the round-1 input (W H then W*H ASCII codes) it parses the LLM program,
steps it, and renders the 16x16 display frame exactly as the judge expects.
Validated cell-for-cell against every frame of all 14 public test cases.
"""
import json, sys

HBORD = ('-', '=')
VBORD = ('|', ':')
ARROW = {'>': (1, 0), '<': (-1, 0), 'v': (0, 1), '^': (0, -1)}

COL_MAN, COL_WALL, COL_PIPE, COL_PIPEV, COL_SPACE = 9, 4, 6, 14, 0


def find_rooms(g, w, h):
    rooms = []
    for y in range(h):
        for x in range(w):
            if g[y][x] != '+':
                continue
            x1 = None
            for xx in range(x + 1, w):
                if g[y][xx] in HBORD:
                    continue
                if g[y][xx] == '+':
                    x1 = xx
                break
            if x1 is None:
                continue
            y1 = None
            for yy in range(y + 1, h):
                if g[yy][x] in VBORD:
                    continue
                if g[yy][x] == '+':
                    y1 = yy
                break
            if y1 is None or g[y1][x1] != '+':
                continue
            if not (all(g[y1][xx] in HBORD for xx in range(x + 1, x1)) and
                    all(g[yy][x1] in VBORD for yy in range(y + 1, y1))):
                continue
            if any(r[0] <= x <= r[2] and r[1] <= y <= r[3] for r in rooms):
                continue
            rooms.append((x, y, x1, y1))
    return rooms


def on_border(r, x, y):
    x0, y0, x1, y1 = r
    return x0 <= x <= x1 and y0 <= y <= y1 and (x in (x0, x1) or y in (y0, y1))


def inside(r, x, y):
    x0, y0, x1, y1 = r
    return x0 < x < x1 and y0 < y < y1


class Pipe:
    def __init__(self, cells, src, dst):
        self.cells, self.src, self.dst = cells, src, dst
        self.slots = [None] * len(cells)


def trace_pipes(g, w, h, rooms):
    pipes, seen = [], set()
    for y in range(h):
        for x in range(w):
            c = g[y][x]
            if c not in ARROW or (x, y) in seen:
                continue
            if any(inside(r, x, y) or on_border(r, x, y) for r in rooms):
                continue
            d = ARROW[c]
            bx, by = x - d[0], y - d[1]
            src = next((r for r in rooms if on_border(r, bx, by)), None)
            if src is None:
                continue
            cells, cx, cy, cd = [], x, y, d
            while 0 <= cx < w and 0 <= cy < h:
                ch = g[cy][cx]
                cells.append((cx, cy))
                if ch in ARROW:
                    cd = ARROW[ch]
                fx, fy = cx + cd[0], cy + cd[1]
                dst = next((r for r in rooms if on_border(r, fx, fy) and r is not src), None)
                if ch in ARROW and dst is not None and len(cells) >= 2:
                    pipes.append(Pipe(cells, src, dst))
                    seen.update(cells)
                    break
                cx, cy = fx, fy
            else:
                raise ValueError("pipe ran off grid")
    return pipes


class Man:
    __slots__ = ('x', 'y', 'd', 'A', 'B', 'room', 'halted')

    def __init__(self, x, y, room):
        self.x, self.y, self.d = x, y, (1, 0)
        self.A = self.B = 0
        self.room, self.halted = room, False


class LLM:
    def __init__(self, w, h, cells):
        self.w, self.h = w, h
        self.g = [list(cells[y * w:(y + 1) * w]) for y in range(h)]
        self.rooms = find_rooms(self.g, w, h)
        self.pipes = trace_pipes(self.g, w, h, self.rooms)
        self.pipecell = {}
        for p in self.pipes:
            for i, c in enumerate(p.cells):
                self.pipecell[c] = (p, i)
        self.wall = set()
        for (x0, y0, x1, y1) in self.rooms:
            for x in range(x0, x1 + 1):
                self.wall.add((x, y0)); self.wall.add((x, y1))
            for y in range(y0, y1 + 1):
                self.wall.add((x0, y)); self.wall.add((x1, y))
        self.men = []
        for y in range(h):
            for x in range(w):
                if self.g[y][x] == '@':
                    self.g[y][x] = ' '
                    rm = next((r for r in self.rooms if inside(r, x, y)), None)
                    self.men.append(Man(x, y, rm))
        self.frozen = False

    # nearest pipe whose arrowhead at this room is closest to (x,y)
    def _pick(self, man, outgoing):
        best, bestkey = None, None
        for p in self.pipes:
            if outgoing:
                if p.src is not man.room:
                    continue
                ax, ay = p.cells[0]
            else:
                if p.dst is not man.room:
                    continue
                ax, ay = p.cells[-1]
            key = (abs(ax - man.x) + abs(ay - man.y), ay, ax)
            if bestkey is None or key < bestkey:
                best, bestkey = p, key
        return best

    def halted_all(self):
        return all(m.halted for m in self.men)

    def step(self):
        """One tick. Returns False if the program is already stopped."""
        if self.frozen or self.halted_all():
            return False
        # 1. pipe values advance (conveyor: front-most first)
        for p in self.pipes:
            for i in range(len(p.slots) - 2, -1, -1):
                if p.slots[i] is not None and p.slots[i + 1] is None:
                    p.slots[i + 1] = p.slots[i]
                    p.slots[i] = None
        # 2. every man executes then advances
        for m in self.men:
            if m.halted:
                continue
            c = self.g[m.y][m.x]
            move = True
            if c in ARROW:
                m.d = ARROW[c]
            elif c.isdigit():
                m.A = int(c)
            elif c == 'M':
                m.B = m.A
            elif c == '+':
                m.A = m.A + m.B
            elif c == '-':
                m.A = m.A - m.B
            elif c == 'X':
                if m.A > 0:
                    m.d = (-m.d[1], m.d[0])
                elif m.A < 0:
                    m.d = (m.d[1], -m.d[0])
            elif c == 'H':
                m.halted = True
                move = False
            elif c == 's':
                p = self._pick(m, True)
                if p is None or p.slots[0] is not None:
                    move = False
                else:
                    p.slots[0] = m.A
            elif c == 'r':
                p = self._pick(m, False)
                if p is None or p.slots[-1] is None:
                    move = False
                else:
                    m.A = p.slots[-1]
                    p.slots[-1] = None
            if move:
                m.x += m.d[0]
                m.y += m.d[1]
        # 3. a man on a wall freezes the whole program (this tick completed)
        if any((m.x, m.y) in self.wall for m in self.men):
            self.frozen = True
        return True

    def stopped(self):
        return self.frozen or self.halted_all()

    def frame(self, dw=16, dh=16):
        px = {(m.x, m.y) for m in self.men}
        out = []
        for y in range(dh):
            row = []
            for x in range(dw):
                if (x, y) in px:
                    row.append(COL_MAN)
                elif y >= self.h or x >= self.w:
                    row.append(COL_SPACE)
                elif (x, y) in self.pipecell:
                    p, i = self.pipecell[(x, y)]
                    row.append(COL_PIPEV if p.slots[i] is not None else COL_PIPE)
                elif (x, y) in self.wall:
                    row.append(COL_WALL)
                else:
                    c = self.g[y][x]
                    if c in '<>^vXH':
                        row.append(3)
                    elif c.isdigit():
                        row.append(8)
                    elif c == 'M':
                        row.append(12)
                    elif c in '+-':
                        row.append(10)
                    elif c in 'sr':
                        row.append(13)
                    else:
                        row.append(COL_SPACE)
            out.append(''.join(str(v) if v < 10 else chr(ord('a') + v - 10) for v in row))
        return out


def run_case(case):
    """Return list of frames, one per round."""
    r0 = case['rounds'][0]['in']
    W, H = int(r0[0]), int(r0[1])
    cells = ''.join(chr(int(c)) for c in r0[2:])
    m = LLM(W, H, cells)
    frames = [m.frame()]
    for rnd in case['rounds'][1:]:
        k = int(rnd['in'][0])
        for _ in range(k):
            if not m.step():
                break
        frames.append(m.frame())
    return frames


if __name__ == '__main__':
    spec = json.load(open(sys.argv[1] if len(sys.argv) > 1
                          else '/home/claude/icfpc2026/spec_little-little-man.json'))
    total = ok = 0
    for case in spec['publicTestData']:
        want = [r['frames'][0] for r in case['rounds']]
        try:
            got = run_case(case)
        except Exception as e:
            print(f"  {case['name']:20s} EXCEPTION {e}")
            total += len(want)
            continue
        good = sum(1 for a, b in zip(got, want) if a == b)
        total += len(want); ok += good
        flag = 'OK ' if good == len(want) else 'BAD'
        print(f"  {flag} {case['name']:20s} {good}/{len(want)} frames")
        if good != len(want) and '-v' in sys.argv:
            for i, (a, b) in enumerate(zip(got, want)):
                if a != b:
                    print(f"    round {i}:")
                    for ra, rb in zip(a, b):
                        print(f"      got {ra}   want {rb}   {'' if ra == rb else '<<<'}")
                    break
    print(f"TOTAL {ok}/{total} frames exact")
