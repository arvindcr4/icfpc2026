import subprocess
import json

def build_subsetsum_man():
    W = 35
    H = 27
    g = [[' '] * W for _ in range(H)]

    def draw_room(x0, y0, w, h):
        for x in range(x0, x0 + w):
            g[y0][x] = '-'
            g[y0 + h - 1][x] = '-'
        for y in range(y0, y0 + h):
            g[y][x0] = '|'
            g[y][x0 + w - 1] = '|'
        g[y0][x0] = '+'
        g[y0][x0 + w - 1] = '+'
        g[y0 + h - 1][x0] = '+'
        g[y0 + h - 1][x0 + w - 1] = '+'

    # 1. Input Room I at (1,0)
    draw_room(1, 0, 3, 3)
    g[1][2] = 'I'
    g[3][2] = 'v'; g[4][2] = 'v'

    # 2. Output Room O at (30,0)
    draw_room(30, 0, 3, 3)
    g[1][31] = 'O'
    g[4][31] = '^'; g[3][31] = '^'

    # 3. Main Room R_main at (1,5), size 32x12
    draw_room(1, 5, 32, 12)

    # 4. Five Relay Rooms along y=19 (height 4)
    # Relay 1 (R_N) at (1,19)
    draw_room(1, 19, 5, 4)
    g[20][2] = '>'; g[20][3] = 'r'; g[20][4] = 'v'
    g[21][2] = '^'; g[21][3] = 'S'; g[21][4] = '<'
    g[17][3] = 'v'; g[18][3] = 'v'
    g[23][3] = 'v'; g[24][3] = '>'; g[24][6] = '^'; g[17][6] = '^'
    for x in range(4, 6): g[24][x] = '-'
    for y in range(18, 24): g[y][6] = '|'

    # Relay 2 (R_T) at (7,19)
    draw_room(7, 19, 5, 4)
    g[20][8] = '>'; g[20][9] = 'r'; g[20][10] = 'v'
    g[21][8] = '^'; g[21][9] = 'S'; g[21][10] = '<'
    g[17][9] = 'v'; g[18][9] = 'v'
    g[23][9] = 'v'; g[24][9] = '>'; g[24][12] = '^'; g[17][12] = '^'
    for x in range(10, 12): g[24][x] = '-'
    for y in range(18, 24): g[y][12] = '|'

    # Relay 3 (R_M) at (13,19)
    draw_room(13, 19, 5, 4)
    g[20][14] = '>'; g[20][15] = 'r'; g[20][16] = 'v'
    g[21][14] = '^'; g[21][15] = 'S'; g[21][16] = '<'
    g[17][15] = 'v'; g[18][15] = 'v'
    g[23][15] = 'v'; g[24][15] = '>'; g[24][18] = '^'; g[17][18] = '^'
    for x in range(16, 18): g[24][x] = '-'
    for y in range(18, 24): g[y][18] = '|'

    # Relay 4 (R_V) at (19,19)
    draw_room(19, 19, 5, 4)
    g[20][20] = '>'; g[20][21] = 'r'; g[20][22] = 'v'
    g[21][20] = '^'; g[21][21] = 'S'; g[21][22] = '<'
    g[17][21] = 'v'; g[18][21] = 'v'
    g[23][21] = 'v'; g[24][21] = '>'; g[24][24] = '^'; g[17][24] = '^'
    for x in range(22, 24): g[24][x] = '-'
    for y in range(18, 24): g[y][24] = '|'

    # Relay 5 (R_C) at (25,19)
    draw_room(25, 19, 5, 4)
    g[20][26] = '>'; g[20][27] = 'r'; g[20][28] = 'v'
    g[21][26] = '^'; g[21][27] = 'S'; g[21][28] = '<'
    g[17][27] = 'v'; g[18][27] = 'v'
    g[23][27] = 'v'; g[24][27] = '>'; g[24][30] = '^'; g[17][30] = '^'
    for x in range(28, 30): g[24][x] = '-'
    for y in range(18, 24): g[y][30] = '|'

    # Let's put instructions in R_main
    # Spawn man at (2,6)
    g[6][2] = '@'
    # Row 6: read n, save to N, compute M=(1<<n)-1, save M
    # (2,6) @, (3,6) r, (4,6) M, (5,6) s (to N at x=3)
    # Then compute (1<<n)-1: b 1 M + m d ...
    # Let's place row 6 instructions
    code_r6 = "@rMsb1"
    for i, c in enumerate(code_r6):
        g[6][2 + i] = c

    text = "\n".join("".join(row).rstrip() for row in g)
    return text

text = build_subsetsum_man()
with open('subsetsum.man', 'w') as f:
    f.write(text)

res = subprocess.run(["python3", "sim.py", "subsetsum.man", "--in", "4 10 20 30 40 100", "--trace", "20"], capture_output=True, text=True)
print("Sim trace stderr:\n", res.stderr.strip())
