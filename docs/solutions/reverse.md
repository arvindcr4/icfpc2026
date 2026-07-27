# reverse.man — reverse a list

**Problem.** Each round: read a count `n`, then `n` integers; print them in
reverse order. 1–3 rounds per test case, `1 ≤ n ≤ 16`, values up to ±10⁶.
The next round's input arrives only after the current output is finished.
Scoring: footprint × ticks.

## Idea: reverse by queue rotation

A little man has three storage slots — main hand `A`, off hand `B`, and the
write-only backpack `BP` — so the list itself must live in pipes, and pipes
are FIFO queues. A FIFO can't pop from the back, but it can *rotate*: if the
queue holds `j` values, move `j-1` of them front-to-back and the front is now
the **last** element. Emit it; the remaining `j-1` values are still in their
original order. Repeat until empty:

```
[a b c]  rotate 2 → [c a b]  emit c
[a b]    rotate 1 → [b a]    emit b
[a]      rotate 0 →          emit a      → output: c b a
```

O(n²) sends, but n ≤ 16 caps it at 120 rotations.

A pipe may not connect a room back to itself, so the queue is a circuit
through a **relay room** whose man forwards forever. The circuit's total
capacity (pipe cells + the relay man's hand) must be ≥ 16 or filling
deadlocks — pipe length is a *semantic* parameter here, not just wiring.

## The grid

```
     +----+
+-+  |>rsv|>---v                 relay room, store-in pipe
|I|  |^@ <|    |
+-+  +----+    |
 v      ^      |                 input pipe, store-out pipe
 v      ^      |
+-------------+|
|>@rMbv   <   ||                 round start + fill loop-back
|     >rsmaW v||                 fill loop
|      >rsv   ||                 rotate cycle (top leg)
|^X-1srdm <bM<|<                 out row (walked right-to-left)
| >N         ^|                  out loop-back lane
+-------------+
     v+-+
     >|O|                        output
      +-+
```

Footprint 16 × 16 = 256. Everything hangs off the main room's walls:
input through the **top wall** (so the `I` room shares the relay band
instead of adding five columns on the left), the store circuit up to the
relay and back down the right edge, output dropping two cells with the `O`
room beside the pipe (3 extra rows, not 5).

## Main man, phase by phase

**Round start — `>@rMbv` (row 7).** `r` reads `n` (blocking until the round
arrives — that is the entire round-handling mechanism), `M` copies it to
`B`, `b` loads it into `BP` as the fill counter. The leading `>` is the
merge target for the round-return path; `@` is a no-op cell, so the return
walks straight through it.

**Fill — `>rsma` (row 8).** Do-while, n times: `r` a value from input, `s`
it into the store, `m`/`a` count down and loop (`a` turns left, up into the
row-7 loop-back). `r`/`s` only touch `A`, so `B` still holds n afterwards;
`W` swaps it back into `A` and the man drops down the col-13 lane onto the
out row's entry `<`.

**Out row — walked right-to-left (row 10).** Read in walk order the row is
`< M b < m d r s 1 - X ^`. On entry `A = k` (n, n−1, …, 1):

| ops    | effect |
|--------|--------|
| `M b`  | `B ← k` (survives rotation), `BP ← k` |
| `< … m d` | the rotate cycle (below) runs exactly k−1 times |
| `r s`  | take the queue's front — the last element — and send it to output |
| `1 -`  | `A = 1 - k` (against the copy in `B`) — deliberately the *negation* of the next counter |
| `X`    | `k > 1`: A < 0, turn left = **down** into the loop-back lane, where `N` fixes `A` to k−1 and the man rides right and up, back to the entry `<`. `k = 1`: A = 0, straight on to `^`, up column 1 onto the round-start `>` |

**Rotate cycle — 8 cells (rows 9–10).** The cycle is the 4×2 rectangle
`>rsv` over `dm <`: bottom leg leftward (`m` decrements, `d` tests), top
leg rightward (`r` from the store, `s` back into it). `d` is the trick — it
turns clockwise (up, into the cycle) while `BP > 0` and falls straight
through (left, out of the cycle) when the count hits zero, so one cell is
both the loop corner and the exit. `m` runs before the first `r`, making
the loop test-before: exactly k−1 rotations, including zero when k = 1.
An 8-tick lap, versus 14 for the older three-row `b>ma` shape — rotation
dominates big rounds, so this is most of the tick win.

After the last round the man parks on the round-start `r` forever; there is
no `H` — the grader ends the program, which is exactly what round-based
grading wants.

## Nearest-pipe targeting is the addressing mode

The main room has two incoming pipes (input, store-in) and two outgoing
(store-out, output); `r`/`s` pick the pipe whose wall attachment is nearest
(Manhattan) to the man's cell. Attachments: input **top wall (6,1)**,
store-out **top wall (6,8)**, store-in **right wall (10,14)**, output
**bottom wall (12,5)**. Every send and receive wins its comparison
**strictly** (the official tie-break rule is unverified):

| cell (row, col) | op | wants | distances (winner first) |
|-----------------|----|-------|--------------------------|
| round `r` (7,3)  | receive | input     | input 3 vs store-in 14 |
| fill `r` (8,7)   | receive | input     | input 8 vs store-in 9  |
| fill `s` (8,8)   | send    | store-out | store-out 2 vs output 7 |
| rotate `r` (9,8) | receive | store-in  | store-in 7 vs input 10 |
| rotate `s` (9,9) | send    | store-out | store-out 4 vs output 7 |
| emit `r` (10,6)  | receive | store-in  | store-in 8 vs input 9  |
| emit `s` (10,5)  | send    | output    | output 2 vs store-out 7 |

Fill `r` and emit `r` sit at margin 1 — a smaller room breaks them first.

This table is no longer hand-maintained: `uv run littleman address
solutions/reverse.man` regenerates it, and `tests/test_analyze.py` asserts
every entry (winner, attachment, margin).

## The store circuit

Main room → store-out (2 cells, straight up) → relay → store-in (14 cells:
along row 1, down column 15) → main room. Capacity = 2 + 14 + 1 (relay
hand) = 17 ≥ 16, with one cell of margin — shortening store-in by one more
cell would make a 16-value fill exactly fit, with zero slack against a
miscounted cell. The relay is the minimal 4×2 forwarder:

```
+----+
|>rsv|
|^@ <|
+----+
```

`@` sits on the *return* leg so the man's first executed op is `r`, not `s`
(an initial `s` would push a spurious 0 into the queue). An 8-cell lap
matches the rotate cycle's 8-tick cadence, so the relay never throttles it.

## Routing tricks

- **The out row is walked right-to-left**, so its loop can put the counter
  test (`d`) at the cycle's bottom-left corner and exit straight into the
  emit sequence — no separate body row, no rejoin column.
- **`1 -` computes the negation on purpose.** `A = 1-k` puts the sign where
  `X`'s arm directions want it (negative = keep looping = turn down); the
  `N` that flips it back to k−1 lives on the loop-back lane, off the
  round-exit path.
- **Arrows are approach-agnostic.** The entry `<` at (10,13) is hit from
  above (fill drop) and from below (loop-back `^`); the cycle corner `<` at
  (10,10) is hit from the right (entry walk) and from above (cycle). The
  round-start `>` is hit from the left (`@` start) and from below (round
  return).

## Constraints this design respects

- **No self-loop pipes** (official environment; enforced by sim.py) — hence
  the relay room.
- **Pipes ≥ 2 cells** (official validator) — the store-out, input, and
  output pipes are all exactly two cells.
- **One backpack per man** — the three nested loops use three different
  counters: the round loop is unconditional, the out loop keeps k in a
  *hand* and branches with `X`, and only the innermost rotate cycle uses
  `BP`. This sidesteps the no-nested-backpack-loops restriction without a
  second worker room.
- **Small integers only** — packing the list into one big number (base
  2·10⁶+1 accumulator) would be ~2× faster and was considered, but needs
  values up to ~10¹⁰⁰; the official runtime's integer width is unverified,
  so rotation is the safe choice.

## Numbers

Footprint 16 × 16 = 256 (was 17 × 32 = 544 before the July rework).
Heaviest public case (rounds of 16 + 9 + 16) completes its output at tick
≈ 3,584 (was ≈ 5,393) — footprint × ticks ≈ 0.92M, 3.2× better than the
original 2.93M. All 8 public cases pass (`tests/test_reverse.py`).

## Ideas for improvement

- The rotate cycle and relay lap are both 8 ticks — the theoretical floor
  for this loop shape; a bigger win needs a different algorithm (e.g. the
  big-number accumulator above, if the official integer width allows it).
- Verify the tie-break rule in the official editor; if it matches sim.py,
  the two margin-1 receives could tolerate an even tighter room.
- The store-in pipe's one cell of capacity margin could be spent as one
  fewer column of lane if a 16-exact circuit proves safe in the official
  runtime.
