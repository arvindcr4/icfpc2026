# ICFP 2026 fleet contract — solve the Littleman problem sets

Contest ends **Mon 27 Jul 12:00 UTC**. Work in `/home/claude/icfpc2026`.

**You cannot submit.** The judge is behind Cloudflare and rejects scripted clients
(`403 error code: 1010`). Write your `.man` file, prove it with the simulator, print your
DONE line. The coordinator submits and relays the judge's verdict back to you.

## Your loop

```bash
cd /home/claude/icfpc2026
curl -s https://icfpcontest2026.com/api/v1/public/problems/<slug> | python3 -m json.tool > spec.json
#   -> description, io, scoring, publicTestData   (GET is fine; only POST is blocked)
python3 sim.py yourprog.man --in "4"            # run against one case
python3 sim.py yourprog.man --in "0" --trace 60 # per-tick A/B/BP trace to stderr
```

`sim.py` is a local reimplementation, **validated against our two accepted solutions**
(Triangle 19/19 and History Lesson 1/1). It is not the judge — if they disagree, the judge
wins — but it catches load errors, wall crashes and wrong output cheaply. **Test every public
case in `publicTestData` before declaring done.**

## The language

Grid of ASCII. Rooms are rectangles of `+` `-` `|`. A little man `@` spawns inside a room
**facing right**, executes the cell under him each tick, then steps one cell. Hitting a room
border is a fatal `wall` error. Registers: `A` main hand, `B` off hand, `BP` backpack — all
signed 64-bit, all starting 0. `BP` is **write-only**: you can branch on it, never read it.

| | |
|---|---|
| `0`–`9` | `A` = digit |
| `` `123` `` | literal; loads on the **closing** backtick. Walked backwards it reads backwards. Spaces inside are ignored |
| `M` / `W` | `B = A` / swap `A,B` |
| `+ - * / % N` | `A = A op B`; `/` floors and puts the **remainder in B**; `N` negates |
| `& \| ~ { }` | and, or, xor, `A<<B`, `A>>B` (arithmetic) |
| `> < ^ v` | set direction |
| `X` | turn by sign(A): right if >0, left if <0, straight if 0. `A` unchanged |
| `b m d a ] x` | `BP=A`; `BP-=1`; turn right/left if `BP>0`; `BP>>=1`; `x` turns right if low bit set else left |
| `q` | `BP` = number of values in the nearest incoming pipe |
| `s S` | send `A` to nearest / every outgoing pipe (blocks if full) |
| `r R U` | receive into `A` from nearest / any incoming pipe; `U` also turns away from that side |
| `Y` | split into two men moving perpendicular; both inherit `A,B,BP` |
| `H` `.` space | halt; nop; nop |

I/O rooms are 3×3 holding a single `I` or `O`, each with exactly one pipe.
Input arrives one value per tick into the input pipe's source cell.

## Pipes — read this twice, it cost us a whole submission

A pipe **must start with an arrowhead whose backward cell is on the source room's border**,
and **ends at the first arrowhead whose forward cell is on another room's border**.

- `>>` — shortest legal pipe (2 cells, arrowheads at both ends).
- `--->` — **NOT A PIPE.** It starts with a body glyph. The program loads clean and then every
  test dies `no-pipe`.
- Body glyphs must match direction (`-` horizontal, `|` vertical); every bend is an arrowhead
  pointing the new way; the terminal arrowhead doubles as the final bend.

`s`/`r`/`q` use the **nearest** pipe by Manhattan distance from the instruction to the pipe
segment touching your room, ties broken in reading order. `R`/`U` take from any ready pipe.

## Backticks pair down COLUMNS as well as along rows

Within a column they pair top-to-bottom, 1st-2nd, 3rd-4th. **A non-digit between a vertical
pair is a load error** — this killed a program that was otherwise perfect:

```
expected a digit or a space between backticks, but found 's' at (2, 2)
```

If you lay literals in a grid, either keep backtick columns identical on every row (pad tokens
so they are symmetric, e.g. `` ` `NNN`s `` ` has backticks at offsets 1 and 5 **both** walked
left-to-right and right-to-left), or keep only spaces/digits between vertical pairs.
`sim.py` enforces this rule, so trust it.

## Scoring — layout matters more than instruction count

`score = max(width, height)² × avgTicks`, **lower is better**, and every case must pass.
Problems marked `footprint` ignore ticks entirely.

The bounding box dominates. Our Triangle went **5819 → 1500** with the *same ten instructions*,
purely by folding a flat 23×3 line into a 7×10 snake with the I/O rooms side by side:

```
+-+ +-+
|I| |O|
+-+ +-+
 v   ^
 v   ^
+-----+
|@rM*v|
|v1W+<|
|>W}sH|
+-----+
```

Get it **correct first**, then square it up. A correct big program beats a beautiful broken one.

## Useful patterns

- **No third register.** With only `A` and `B` readable, a loop that needs a constant *and* an
  accumulator *and* a temp needs external storage — use a pipe to a helper room as memory,
  or restructure the arithmetic. Triangle avoids a division entirely by computing
  `(n²+n) >> 1`, parking the `1` in `B` with two `W` swaps.
- **Pipes are FIFO queues** and hold one value per cell — a long pipe is a delay line and a
  bounded buffer. A ring of two rooms joined by pipes both ways is a rotatable store.
- **`BP` is a loop counter**: `b` to set, `m` to decrement, `d`/`a` to branch while positive.
- **Encode a stack in one integer** when the alphabet is small: push = `A*k + item`,
  pop = `%k` then `/k`. 64 bits holds 31 items at k=4.

## House rules

1. Write **only your own file**. Never `git`. Never touch another agent's `.man`.
2. Test every public case with `sim.py` before you claim success.
3. **Report failure honestly.** "I could not make Sort work, here is how far I got and what
   blocked me" is worth more than a program that does not run. Do not invent a passing result.
4. Print exactly: `DONE <file> — result: <passes|fails|partial> — <cases passed>/<total>, <what you did>`

## Assignments

| Agent | Problem | slug | File |
|---|---|---|---|
| agy1 | Brackets | `brackets` | `brackets.man` |
| agy2 | Reverse a List | `reverse-a-list` | `reverse.man` |
| agy3 | Sort | `sort-numbers` | `sort.man` |
| agy4 | Memory | `memory` | `memory.man` |
| agy5 | Packet Reassembly | `tcp` | `tcp.man` |
| agy6 | Sudoku Auditor | `sudoku-validity` | `sudoku.man` |
| agy7 | Matrix Multiply | `matmul` | `matmul.man` |
| agy8 | Subset Sum | `subset-sum` | `subsetsum.man` |
