import sys, subprocess, json

def build_subsetsum_man():
    W = 30
    H = 24
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

    # 1. Input Room I at (1, 0)
    draw_room(1, 0, 3, 3)
    g[1][2] = 'I'
    # Input pipe from (2,2) to (2,4)
    g[2][2] = 'v'
    g[3][2] = '|'
    g[4][2] = 'v'

    # 2. Output Room O at (25, 0)
    draw_room(25, 0, 3, 3)
    g[1][26] = 'O'
    # Output pipe from (26,4) to (26,2)
    g[4][26] = '^'
    g[3][26] = '|'
    g[2][26] = '^'

    # 3. Main Room R_main at (1, 4)
    draw_room(1, 4, 27, 11) # y=4 to 14

    # 4. Five Relay Rooms along y=17 (height 4)
    # R_N at (1, 17)
    draw_room(1, 17, 5, 4)
    g[18][2] = '>'; g[18][3] = 'r'; g[18][4] = 'v'
    g[19][2] = '^'; g[19][3] = 'S'; g[19][4] = '<'
    # Pipe N in: (3,14) -> (3,17)
    g[14][3] = 'v'; g[15][3] = '|'; g[16][3] = '|'; g[17][3] = 'v'
    # Pipe N out: (4,20) -> (4,14)
    g[20][4] = 'v'; g[21][4] = '>'; g[22][4] = '^'; g[22][5] = '^' # bend at 21,4?

    # Return string
    return "\n".join("".join(row).rstrip() for row in g)

text = build_subsetsum_man()
with open('subsetsum.man', 'w') as f:
    f.write(text)

print("Wrote subsetsum.man test draft.")
