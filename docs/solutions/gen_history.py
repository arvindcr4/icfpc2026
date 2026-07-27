"""Generate solutions/history.man — output the ICFP history text.

The problem is footprint-scored: score = max(width, height)^2, no input.
The text (solutions/icfp-history.txt, 2810 chars, all in ASCII 32..122)
is packed 9 chars per base-95 "chunk" literal:

    value = sum((ord(c[j]) - 31) * 95**j for j in range(m))

The -31 offset maps chars to 1..95, so no base-95 digit is ever zero:
the decoder can emit `v % 95 + 31` and stop exactly when `v // 95 == 0`,
with no sentinel digit and no lost high-order spaces. Values stay below
95^9 < 10^18, so full chunks are 18 decimal digits (zero-padded — slots
pack exactly) and fit in int64 read in both directions — the official
loader requires that, and hands are confirmed signed 64-bit.
Least-significant base-95 digit is the first char out, so divmod emits
the text in order.

Layout (92 x 88, score 8464):
  * Producer room, full width, 79 interior rows: a serpentine walk over
    4 chunks per row, ending with a `0` sentinel send and H. Chunks sit
    in fixed 22-cell column slots so that the official loader's backtick
    rule holds (backticks pair per row AND per column independently —
    see analyze.backtick_issues). Rightward rows use `18d`s+pad, leftward
    rows pad+s+`reversed 18d`: every column then holds either only
    backticks (vertically adjacent pairs = legal empty literals), only
    digits/sends, or only spaces — never an op between a vertical pair.
  * Man 1 (unpacker): per chunk, repeated divmod by 95; while the
    quotient is positive it survives each emit via W s W (send the
    remainder from the off hand); on quotient 0 the remainder is the
    chunk's last char — emit it and fetch the next chunk. Chunk 0 ->
    send -1, halt.
  * Man 2 (+31 emitter): B = 31 once, then r X + s forever; X routes
    negative (the -1 sentinel) to H, zero/positive re-merge onto + s.

Run: uv run python solutions/gen_history.py
"""
from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from littleman.analyze import backtick_issues
from littleman.sim import run

HERE = pathlib.Path(__file__).parent
TEXT = (HERE / "icfp-history.txt").read_bytes().decode("ascii")

BASE = 95          # alphabet: ASCII 32..126 stored as c - 31 (1..95)
CHUNK = 9          # chars per literal; 95**9 < 10**18 < 2**63
DIGITS = len(str(BASE**CHUNK - 1))  # 18: zero-padded width of a chunk

SLOT = DIGITS + 4  # 22: literal + send + one pad cell, both directions
PER_ROW = 4        # chunks per producer row (either direction)
W = PER_ROW * SLOT + 4  # 92: wall, turn lane, 4 slots, turn lane, wall
PROD_ROWS = 79     # producer interior rows: ceil(313 chunks / 4)
H = PROD_ROWS + 2 + 7  # producer + decoder strip = 88


def encode(chars: str) -> str:
    v = sum((ord(ch) - 31) * BASE**j for j, ch in enumerate(chars))
    return str(v).zfill(DIGITS)


def chunks(text: str) -> list[str]:
    return [encode(text[i:i + CHUNK]) for i in range(0, len(text), CHUNK)]


def build() -> str:
    grid = [[" "] * W for _ in range(H)]

    def put(r: int, c: int, s: str) -> None:
        for i, ch in enumerate(s):
            assert grid[r][c + i] == " ", (r, c + i, grid[r][c + i], ch)
            grid[r][c + i] = ch

    def room(top: int, left: int, bottom: int, right: int) -> None:
        put(top, left, "+" + "-" * (right - left - 1) + "+")
        put(bottom, left, "+" + "-" * (right - left - 1) + "+")
        for r in range(top + 1, bottom):
            put(r, left, "|")
            put(r, right, "|")

    # ---------------------------------------------------------- producer
    room(0, 0, PROD_ROWS + 1, W - 1)
    data = chunks(TEXT)
    assert all(len(d) == DIGITS for d in data)
    row, grid[1][1] = 1, "@"
    for i in range(0, len(data), PER_ROW):
        batch = data[i:i + PER_ROW]
        last = i + PER_ROW >= len(data)
        if row % 2:  # rightward row: `18d`s+pad per slot, walked in order
            for j, d in enumerate(batch):
                put(row, 2 + j * SLOT, f"`{d}`s")
            if last:
                put(row, 2 + len(batch) * SLOT, "0sH")  # terminator + halt
            else:
                put(row, W - 2, "v")
                put(row + 1, W - 2, "<")
        else:        # leftward row: pad+s+`reversed 18d`, rightmost first
            assert not last, "terminator must land on a rightward row"
            for j, d in enumerate(batch):
                put(row, 2 + (PER_ROW - 1 - j) * SLOT + 1, f"s`{d[::-1]}`")
            put(row, 1, "v")
            put(row + 1, 1, ">")
        row += 1
    assert row <= PROD_ROWS + 1, row

    # ------------------------------------------- man 1: chunk -> base-95
    m1_top, m1_left = PROD_ROWS + 2, 2  # rows 81..86, cols 2..18
    room(m1_top, m1_left, m1_top + 5, m1_left + 16)

    def put1(r: int, c: int, s: str) -> None:  # man-1 interior coords
        put(m1_top + r, m1_left + c, s)

    put1(1, 1, "@>rX`1`NsH")   # outer loop: fetch chunk / halt on 0
    put1(2, 2, "^")            # return path back to the outer r
    put1(2, 15, "<")
    put1(3, 4, ">W`95`W/XWs^")  # divmod; q==0: emit last char, go up
    put1(4, 4, "^")
    put1(4, 9, "WsW<")         # q>0: emit rem from off hand, keep q

    # producer bottom wall -> man 1 left wall
    put(m1_top, 1, "v")
    put(m1_top + 1, 1, ">")

    # -------------------------------------------- man 2: value + 31 -> O
    # m2_left keeps the room's backticks (`31`) on producer digit columns;
    # a decoder backtick under a producer backtick column could form an
    # unintended vertical pair across the rooms' walls.
    m2_top, m2_left = PROD_ROWS + 2, 27  # rows 81..87, cols 27..37
    room(m2_top, m2_left, m2_top + 6, m2_left + 10)

    def put2(r: int, c: int, s: str) -> None:  # man-2 interior coords
        put(m2_top + r, m2_left + c, s)

    put2(1, 1, "@`31`M v")     # off hand = 31, once
    put2(2, 1, ">")
    put2(2, 8, "v")
    put2(3, 8, "r")
    put2(4, 7, "vXH")          # X: negative sentinel -> H (right)
    put2(5, 1, "^")
    put2(5, 5, "s+<<")         # zero/positive re-merge onto + s

    # man 1 right wall -> man 2 left wall
    put(m1_top + 4, m1_left + 17,
        ">" + "-" * (m2_left - m1_left - 19) + ">")

    # ------------------------------------------------------- output room
    o_top, o_left = m2_top + 4, m2_left + 13  # rows 85..87, cols 34..36
    room(o_top, o_left, o_top + 2, o_left + 2)
    put(o_top + 1, o_left + 1, "O")
    put(m2_top + 5, m2_left + 11, ">>")  # man 2 right wall -> O left wall

    return "\n".join("".join(r).rstrip() for r in grid) + "\n"


def main() -> None:
    text = build()
    lines = text.splitlines()
    width, height = max(map(len, lines)), len(lines)
    out = HERE / "history.man"
    out.write_text(text)

    if issues := backtick_issues(text):
        for issue in issues[:10]:
            print("official loader:", issue)
        sys.exit(1)

    res = run(text, max_ticks=300_000)
    got = "".join(map(chr, res.output))
    ok = got == TEXT and res.halted
    print(f"{out.name}: {width}x{height}, score {max(width, height)**2}, "
          f"ticks {res.ticks}, halted {res.halted}, output "
          f"{'OK' if got == TEXT else 'MISMATCH'}")
    if res.error:
        print("error:", res.error)
    if not ok:
        for i, (a, b) in enumerate(zip(got, TEXT, strict=False)):
            if a != b:
                print(f"first diff at {i}: got {a!r} want {b!r}")
                break
        print(f"lengths: got {len(got)} want {len(TEXT)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
