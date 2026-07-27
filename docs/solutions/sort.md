# sort.man — sort a list ascending

**Problem.** Each round: read a count `n`, then `n` integers; print them in
ascending order, duplicates kept. 2–6 rounds per test case, `1 ≤ n ≤ 16`,
values within ±10000. The next round's input arrives only after the current
output is finished. Scoring: footprint × ticks.

## Idea: selection sort over the pipe queue

Same storage architecture as `reverse.man`: the list lives in a FIFO circuit
(main room → store-out pipe → relay room → store-in pipe → main room), because
a man only has `A`, `B` and the write-only backpack. Instead of rotating to
reach the back, each pass *scans* the queue once and extracts the minimum:

- hold the current minimum in `B`;
- pop a candidate into `A`, compute `A - B`, branch on the sign:
  - negative (candidate smaller): restore the candidate with `+`, `W` it into
    `B`, and send the *old* minimum back to the queue;
  - zero or positive: restore with `+` and send the *candidate* back;
- after `k−1` comparisons the minimum is in `B`; emit it. O(n²) sends total,
  same asymptotics as the reverse rotation but with a real comparison per hop.

Ties go straight (zero arm), which sends the candidate back and keeps the
incumbent — duplicates lose ties, stay queued, and are emitted on later
passes, so none are dropped.

## The count travels in the queue

The scan occupies all three registers (`A` candidate, `B` minimum, `BP` loop
counter), so the remaining count `k` can't live in the man. It lives in the
queue itself, as a header element in front of the values:

```
store = [k, v1 … vk]
```

Each outer pass: pop `k`, push `k−1` (it lands *behind* the values), scan —
which pops all `k` values and pushes back the `k−1` losers behind the new
header — leaving exactly `[k−1, survivors…]` for the next pass. The fill
phase seeds the round by pushing `n` before the values. When the popped
header is 1 there is nothing to compare: a short last-element path emits the
single remaining value directly and returns to the round-start `r`, leaving
the store empty for the next round.

## The grid

```
                         >------v                    store-out pipe
                         ^      |+----+
+-+  +------------------------+ >|>@rv|              relay room
|I|>>|@>rsbv   <              |  |^ s<|
+-+  |     >rsmav             |  +----+
     |            v  MrsNWbW< |     v                general arm  (row 5)
     |                 >+Wsv  |     |                new-min arm  (row 6)
     |              >r-X+sv   |     |                scan body    (row 7)
     |            >maWv>+sv   |<----<                loop head    (row 8)
     |            ^       <<  |                      loop-back    (row 9)
     |          >      >rM1-Xv|                      outer head   (row 10)
     |                       r|
     |                s      s|  +-+
     |                >^      |>>|O|                 output
     | ^                    <<|  +-+
     +------------------------+
```

## Main man, phase by phase

**Round start — `@>rsb` (row 3).** `r` reads `n` (blocking until the round
arrives — the entire round-handling mechanism), `s` pushes it as the header
(`s` copies, so `A` still holds `n`), `b` loads the fill counter.

**Fill — `>rsma` (row 4).** Do-while, n times: `r` a value from input, `s`
it into the store. On exit the man drops down col 16, rides row 10 right,
and enters the outer head.

**Outer head — `>rM1-X` (row 10).** `r` pops the header `k`, `M` saves it,
`1-` computes `A = 1−k`, and `X` branches:

| `A = 1−k` | meaning | route |
|-----------|---------|-------|
| negative (k ≥ 2) | scan needed | turn up: ascend col 28 to the general arm |
| zero (k = 1) | last element | straight: `v` down col 29 — `r` the value, `s` it to output, ride row 14 / col 7 back to round start |
| positive (k = 0) | unreachable | the header is only ever ≥ 1; a `<` at (14,28) still routes it safely home |

**General arm — `<WbWNsrM` read right-to-left (row 5).** Entered with
`A = 1−k`, `B = k`: `W b` load `BP = k` for the scan loop, `W N` recompute
`A = k−1`, `s` pushes it as the next header, `r M` pop the first value as the
initial minimum in `B`. Drop down col 18 into the loop head.

**Scan loop — head `>ma` (row 8), body `>r-X+sv` (row 7).** The head is
test-before (`m` first): with `BP = k` the body runs exactly `k−1` times,
including zero times for k = 1 (which the general arm never sees, but the
same shape is load-bearing in `reverse.man`). The body: `r` candidate, `-`,
then `X` with **all three arms live**:

- negative → up to row 6: `>+Wsv` — restore candidate, swap it into `B`,
  send the old minimum back;
- zero → straight: `+s` at (7,24–25);
- positive → down to row 8: `>+s` at (8,23–25);

the zero and positive arms are duplicate `+s` tails that merge on the shared
`v` at (8,26); all three descend into the row-9 lane back to the head.

**Emit — `W` (8,21) then `s` (12,22).** Loop exit swaps the minimum into
`A`, drops down col 22 (executing the output `s` mid-descent), U-turns at
(13,22)–(13,23) and climbs col 23 back into the outer head.

## Nearest-pipe addressing

Attachments: input **left wall (3,5)**, store-out **top wall (2,25)**,
store-in **right wall (8,30)**, output **right wall (13,30)**. Every `r`/`s`
wins its Manhattan comparison strictly (`littleman address`):

| cell (row, col) | op | wants | dist | margin |
|-----------------|----|-------|------|--------|
| round `r` (3,8)   | receive | input     | 3  | 24 |
| round `s` (3,9)   | send    | store-out | 17 | 14 |
| fill `r` (4,12)   | receive | input     | 8  | 14 |
| fill `s` (4,13)   | send    | store-out | 14 | 12 |
| general `r` (5,22)| receive | store-in  | 11 | 8  |
| header `s` (5,23) | send    | store-out | 5  | 10 |
| new-min `s` (6,26)| send    | store-out | 5  | 6  |
| body `r` (7,21)   | receive | store-in  | 10 | 10 |
| body `s` (7,25)   | send    | store-out | 5  | 6  |
| pos-arm `s` (8,25)| send    | store-out | 6  | 4  |
| outer `r` (10,24) | receive | store-in  | 8  | 18 |
| last `r` (11,29)  | receive | store-in  | 4  | 28 |
| emit `s` (12,22)  | send    | output    | 9  | 4  |
| last `s` (12,29)  | send    | output    | 2  | 12 |

Putting store-in and output on the *same* wall (rows 8 vs 13) is what lets
the output room sit beside the main room instead of hanging below it — the
row-11/12 boundary flips the winner between store-out and output.

## Routing tricks

- **Fill-exit crosses the scan block through dead arithmetic.** The
  fill-exit descends col 22 executing `N`, `+`, `+`, `+` on the way — all
  harmless because both hands are dead between rounds. The same four cells
  are load-bearing ops for the general arm, the new-min arm, the zero arm
  and the pos arm.
- **The emit `s` executes mid-descent.** No dedicated emit row: the output
  send sits at (12,22) on the vertical drop from the loop exit.
- **Paths cross at spaces.** The emit descent (col 22), its return climb
  (col 23), the general-arm ascent (col 28) and the col-7 home highway all
  cross the horizontal lanes at plain spaces, direction-neutrally.
- **The relay is a 2×4 loop.** `>@rv` / `^ s<` is the smallest forwarder:
  a 2×3 interior has no spare cell for `@`, and the loop-back would land on
  `@` moving up — `@` doesn't redirect, and the man hits the wall (caught by
  `littleman trace`).

## Constraints this design respects

- **No self-loop pipes** → relay room circuit (capacity 11 + 1 + 9 = 21 ≥ 17
  = header + 16 values, so the fill phase can never deadlock).
- **Pipes ≥ 2 cells** → the output pipe is the minimum `>>`.
- **One backpack per man** → the outer loop keeps no counter at all (the
  queue header replaces it); only the fill and scan loops use `BP`, never
  nested.
- **Small integers only** → values stay ≤ 10⁴ in magnitude; only `k−1` and
  differences of inputs are ever computed.

## Numbers

Footprint 16 × 39 = 624. Heaviest public case ("long case": rounds of
16 + 3 + 12 + 16) finishes its last output at tick 9018 → score ≈ 5.63M.
All 7 public cases pass under round-based feeding (`tests/test_sort.py`).

## Ideas for improvement

- The scan-loop circumference (~22 ticks per comparison) dominates: body
  row 7, lane row 9 and the head span cols 16–27. Each column squeezed out
  of that circuit saves ~2 ticks × Σ(k−1) comparisons.
- The emit detour (down col 22, up col 23) costs ~16 ticks per emitted
  value; an output attachment nearer the loop exit would shave most of it.
- A two-man design (scanner + emitter) could overlap the scan of pass k+1
  with the emit of pass k, but shared store addressing gets hairy.
