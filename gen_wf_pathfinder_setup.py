#!/usr/bin/env python3
"""Build gpt/wf-pathfinder-setup.man : setup round only (256 board pixels + robot + commit)."""
W, H = 48, 36
g = [[' '] * W for _ in range(H)]


def put(x, y, s):
    for i, c in enumerate(s):
        g[y][x + i] = c


def vput(x, y, s):
    for i, c in enumerate(s):
        g[y + i][x] = c


# ---------------- display room : outer x30..47, y3..20, interior 16x16 -------------
put(30, 3, '+' + '=' * 16 + '+')
put(30, 20, '+' + '=' * 16 + '+')
for y in range(4, 20):
    g[y][30] = ':'
    g[y][47] = ':'

# ---------------- main room : outer x0..27, y5..30 --------------------------------
put(0, 5, '+' + '-' * 26 + '+')
put(0, 30, '+' + '-' * 26 + '+')
for y in range(6, 30):
    g[y][0] = '|'
    g[y][27] = '|'

# ---------------- input room : outer x0..2, y33..35 -------------------------------
put(0, 33, '+-+')
put(0, 34, '|I|')
put(0, 35, '+-+')

# ---------------- pipes -----------------------------------------------------------
# input: I room -> main room (enters main bottom border at (1,30))
vput(1, 31, '^^')

# DATA pipe : main room right border -> display LEFT border
put(28, 9, '>>')

# ADDR pipe : main room top border -> display TOP border
g[4][26] = '^'
g[3][26] = '|'
g[2][26] = '>'
put(27, 2, '----')
g[2][31] = 'v'

# SWAP pipe : main room bottom border -> display BOTTOM border
g[31][25] = 'v'
g[32][25] = '>'
put(26, 32, '-' * 10)
g[32][36] = '^'
for y in range(22, 32):
    g[y][36] = '|'
g[21][36] = '^'

# ---------------- program ---------------------------------------------------------
# phase 1 : stream 256 board cells as colours (0 -> 0, 1 -> 7) into DATA
put(10, 7, '@`257`bv')          # A=257, BP=257, drop south into the loop
put(17, 8, '>m    dv')          # loop top (east): m, nops, d branch, v = exit
put(17, 9, '^s*7Mr<')           # loop body (west): < r M 7 * s ^

# phase 2 : read rx,ry -> ADDR = 16*ry+rx ; robot pixel ; commit
g[10][24] = '<'                 # exit turns west onto row 10
put(12, 10, 'v W1W{W4Mrbr')     # walked WEST: r b r M 4 W { W 1 W _ v

# add-loop : add 1 to A, BP(=rx) times.  rows 11/12, cols 9..12
put(9, 11, 'a  <')              # west travel: a(branch south) nops <
put(9, 12, '>+m^')              # east travel: > + m ^

g[11][1] = '^'                  # exit ran west along row 11, now go north
g[6][1] = '>'                   # then east along row 6
g[6][25] = 's'                  # ADDR  <- 16*ry+rx
g[6][26] = 'v'
vput(26, 7, '`10`')             # literal 10 read walking SOUTH down column 26
g[17][26] = 's'                 # DATA  <- colour 10 at the robot cell
g[28][26] = '0'
g[29][26] = '<'
g[29][25] = 's'                 # SWAP  <- 0  (commit the frame)
# the SWAP pipe is 24 cells long: walk ~41 nops so the value lands before we halt
g[29][1] = '^'
g[12][1] = 'H'

out = '\n'.join(''.join(r).rstrip() for r in g) + '\n'
open('/home/claude/icfpc2026/gpt/wf-pathfinder-setup.man', 'w').write(out)
print(out)
