import subprocess
import json

def build_man():
    # Construct subsetsum.man
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

    # Rooms
    draw_room(1, 0, 3, 3); g[1][2] = 'I'; g[3][2] = 'v'; g[4][2] = 'v'
    draw_room(30, 0, 3, 3); g[1][31] = 'O'; g[4][31] = '^'; g[3][31] = '^'
    draw_room(1, 5, 32, 12)

    # Relay Rooms
    draw_room(1, 19, 5, 4); g[20][2] = '>'; g[20][3] = 'r'; g[20][4] = 'v'; g[21][2] = '^'; g[21][3] = 'S'; g[21][4] = '<'; g[17][3] = 'v'; g[18][3] = 'v'; g[23][3] = 'v'; g[24][3] = '>'; g[24][6] = '^'; g[17][6] = '^'
    for x in range(4, 6): g[24][x] = '-'
    for y in range(18, 24): g[y][6] = '|'

    draw_room(7, 19, 5, 4); g[20][8] = '>'; g[20][9] = 'r'; g[20][10] = 'v'; g[21][8] = '^'; g[21][9] = 'S'; g[21][10] = '<'; g[17][9] = 'v'; g[18][9] = 'v'; g[23][9] = 'v'; g[24][9] = '>'; g[24][12] = '^'; g[17][12] = '^'
    for x in range(10, 12): g[24][x] = '-'
    for y in range(18, 24): g[y][12] = '|'

    draw_room(13, 19, 5, 4); g[20][14] = '>'; g[20][15] = 'r'; g[20][16] = 'v'; g[21][14] = '^'; g[21][15] = 'S'; g[21][16] = '<'; g[17][15] = 'v'; g[18][15] = 'v'; g[23][15] = 'v'; g[24][15] = '>'; g[24][18] = '^'; g[17][18] = '^'
    for x in range(16, 18): g[24][x] = '-'
    for y in range(18, 24): g[y][18] = '|'

    draw_room(19, 19, 5, 4); g[20][20] = '>'; g[20][21] = 'r'; g[20][22] = 'v'; g[21][20] = '^'; g[21][21] = 'S'; g[21][22] = '<'; g[17][21] = 'v'; g[18][21] = 'v'; g[23][21] = 'v'; g[24][21] = '>'; g[24][24] = '^'; g[17][24] = '^'
    for x in range(22, 24): g[24][x] = '-'
    for y in range(18, 24): g[y][24] = '|'

    draw_room(25, 19, 5, 4); g[20][26] = '>'; g[20][27] = 'r'; g[20][28] = 'v'; g[21][26] = '^'; g[21][27] = 'S'; g[21][28] = '<'; g[17][27] = 'v'; g[18][27] = 'v'; g[23][27] = 'v'; g[24][27] = '>'; g[24][30] = '^'; g[17][30] = '^'
    for x in range(28, 30): g[24][x] = '-'
    for y in range(18, 24): g[y][30] = '|'

    # Instructions in R_main:
    # Phase 1: Read n, save N, compute M=(1<<n)-1, save M
    code_r6 = "@rMsb1>M+mdM1W-s"
    for i, c in enumerate(code_r6): g[6][2 + i] = c
    g[7][8] = '^'; g[7][9] = '<'; g[7][10] = '<'; g[7][11] = '<'; g[7][12] = '<'

    # Read n values -> send to V:
    code_r6_vals = "rsb>rsmd"
    for i, c in enumerate(code_r6_vals): g[6][18 + i] = c
    g[7][21] = '^'; g[7][22] = '<'; g[7][23] = '<'; g[7][24] = '<'; g[7][25] = '<'

    # Read t -> send to T:
    code_r6_t = "rs"
    for i, c in enumerate(code_r6_t): g[6][26 + i] = c

    # Turn down at (28,6) to Row 8
    g[6][28] = 'v'
    for y in range(7, 9): g[y][28] = 'v'

    # Row 8: Outer Mask Loop Header (moving WEST)
    g[8][28] = '<'
    code_r8 = "rXM1W-sM1+"
    for i, c in enumerate(reversed(code_r8)): g[8][27 - i] = c

    text = "\n".join("".join(row).rstrip() for row in g)
    return text

text = build_man()
with open('subsetsum.man', 'w') as f:
    f.write(text)

with open('subsetsum_spec.json') as f:
    spec = json.load(f)

passes = 0
total = len(spec['publicTestData'])

for case in spec['publicTestData']:
    name = case['name']
    inp_str = " ".join(case['rounds'][0]['in'])
    exp_out_str = " ".join(case['rounds'][0]['out'])
    
    cmd = ["python3", "sim.py", "subsetsum.man", "--in", inp_str]
    res = subprocess.run(cmd, capture_output=True, text=True)
    out = res.stdout.strip()
    err = res.stderr.strip()
    
    status = "PASS" if out == exp_out_str else "FAIL"
    if status == "PASS": passes += 1
    print(f"[{status}] {name:<30} -> Got: '{out}' | Expected: '{exp_out_str}'")

print(f"\nSummary: {passes}/{total} passed")

