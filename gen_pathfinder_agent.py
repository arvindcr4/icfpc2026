#!/usr/bin/env python3
"""Pathfinder SETUP-round program generator (see report)."""

W, H = 200, 130
g = [[' '] * W for _ in range(H)]


def put(x, y, ch):
    assert 0 <= x < W and 0 <= y < H, (x, y, ch)
    g[y][x] = ch


def text(x, y, s):
    for i, c in enumerate(s):
        put(x + i, y, c)


def room(x0, y0, x1, y1, disp=False):
    hb = '=' if disp else '-'
    vb = ':' if disp else '|'
    for x in range(x0, x1 + 1):
        put(x, y0, hb); put(x, y1, hb)
    for y in range(y0, y1 + 1):
        put(x0, y, vb); put(x1, y, vb)
    for c in ((x0, y0), (x1, y0), (x0, y1), (x1, y1)):
        put(c[0], c[1], '+')


ARR = {(1, 0): '>', (-1, 0): '<', (0, 1): 'v', (0, -1): '^'}


def pipe(cells, final_dir):
    n = len(cells)
    for i, (x, y) in enumerate(cells):
        d = (cells[i + 1][0] - x, cells[i + 1][1] - y) if i < n - 1 else final_dir
        prev = None if i == 0 else (x - cells[i - 1][0], y - cells[i - 1][1])
        if i == 0 or i == n - 1 or d != prev:
            put(x, y, ARR[d])
        else:
            put(x, y, '-' if d[1] == 0 else '|')


# ------------------------------------------------------------------ I room
room(0, 0, 2, 2)
put(1, 1, 'I')
pipe([(1, 3), (1, 4)], (0, 1))

# ------------------------------------------------------------------ room A
AX0, AY0, AX1, AY1 = 0, 5, 42, 12
room(AX0, AY0, AX1, AY1)
text(1, 6, '@8M8*M4*b')        # A=256 ; BP=256
text(10, 6, '>rsmd')           # 256x { read input, push into snake }
text(10, 7, '^...<')
for x in range(15, 28):
    put(x, 6, '.')
text(28, 6, 'rsrM+M+M+M+s')    # rx -> short pipe ; 16*ry -> short pipe
put(40, 6, 'H')

# ------------------------------------------------------------------ snake
serp = []
rows = list(range(15, 40, 2))
left, right = 4, 27
for i, ry in enumerate(rows):
    seq = [(xx, ry) for xx in range(left, right + 1)]
    if i % 2:
        seq.reverse()
    serp += seq
    if i + 1 < len(rows):
        serp.append((seq[-1][0], ry + 1))
ly = rows[-1]

BX0, BY0, BX1, BY1 = 60, ly + 3, 92, ly + 12
snake = [(12, 13), (12, 14)]
snake += [(xx, 14) for xx in range(11, 3, -1)]
snake += serp
snake += [(27, yy) for yy in range(ly + 1, BY1 + 5)]
snake += [(xx, BY1 + 4) for xx in range(28, BX1 - 2)]
snake += [(BX1 - 3, yy) for yy in range(BY1 + 3, BY1, -1)]
SNAKE_LEN = len(snake)

# ------------------------------------------------------------------ room B
room(BX0, BY0, BX1, BY1)
pipe(snake, (0, -1))           # enters B's bottom border, east end

# short pipe A(top) -> B(top, west end)
sp = [(30, 4), (30, 3)] + [(xx, 3) for xx in range(31, 58)] + \
     [(57, yy) for yy in range(4, BY0 + 2)] + [(58, BY0 + 1), (59, BY0 + 1)]
pipe(sp, (1, 0))               # enters B's left border, top row

R1 = BY0 + 1
text(BX0 + 1, R1, '@rMr+b7M')      # p = rx + 16*ry ; BP=p ; B=7
for x in range(BX0 + 9, BX1 - 8):
    put(x, R1, '.')
text(BX1 - 8, R1, '>r*smd')        # loop1: p cells, colour = v*7
text(BX1 - 8, R1 + 1, '^....<')
put(BX1 - 2, R1, 'v')              # loop1 exit -> down
put(BX1 - 2, R1 + 1, '.')
put(BX1 - 2, R1 + 2, '<')
for x in range(BX1 - 10, BX1 - 2):
    put(x, R1 + 2, '.')
put(BX1 - 11, R1 + 2, 'v')
put(BX1 - 11, R1 + 3, '>')
text(BX1 - 10, R1 + 3, 'r8M2+s7Mq')   # robot pixel = 10 ; BP = 255-p
put(BX1 - 1, R1 + 3, 'v')
put(BX1 - 1, R1 + 4, '<')
for x in range(BX1 - 8, BX1 - 1):
    put(x, R1 + 4, '.')
put(BX1 - 9, R1 + 4, 'v')
put(BX1 - 9, R1 + 5, '>')
text(BX1 - 8, R1 + 5, 'r*smd')     # loop2 body (do-while, 255-p >= 1)
text(BX1 - 9, R1 + 6, '^....<')
put(BX1 - 3, R1 + 5, 'v')          # loop2 exit
put(BX1 - 3, R1 + 6, '.')
put(BX1 - 3, R1 + 7, '<')
for x in range(BX0 + 3, BX1 - 3):
    put(x, R1 + 7, '.')
put(BX0 + 2, R1 + 7, 's')          # token -> C (west side, nearest = token pipe)
put(BX0 + 1, R1 + 7, 'H')

# ------------------------------------------------------------------ display
DX0, DY0 = 100, BY0 - 4
room(DX0, DY0, DX0 + 17, DY0 + 17, disp=True)
# DATA pipe: B east border -> display left border
dy = R1 + 5
pipe([(x, dy) for x in range(BX1 + 1, DX0)], (1, 0))

# ------------------------------------------------------------------ room C
CX0, CY0, CX1, CY1 = DX0 + 2, DY0 + 20, DX0 + 10, DY0 + 24
room(CX0, CY0, CX1, CY1)
text(CX0 + 1, CY0 + 1, '@r0sH')
# SWAP pipe: C top border -> display bottom border
cx = CX0 + 3
pipe([(cx, y) for y in range(CY0 - 1, DY0 + 17, -1)], (0, -1))
# token pipe: B bottom border (west end) -> C left border
tk = [(BX0 + 2, y) for y in range(BY0 - 1, DY0 - 3, -1)]
tk += [(x, DY0 - 2) for x in range(BX0 + 3, 126)]
tk += [(125, y) for y in range(DY0 - 1, CY0 + 3)]
tk += [(x, CY0 + 2) for x in range(124, CX1, -1)]
pipe(tk, (-1, 0))

with open('/home/claude/icfpc2026/gpt/pathfinder-agent.man', 'w') as f:
    f.write('\n'.join(''.join(r).rstrip() for r in g) + '\n')
print('snake', SNAKE_LEN, 'ly', ly)
