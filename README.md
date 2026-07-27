# ICFP Programming Contest 2026 — team `arvindcr4`

Solutions in the Littleman (`.man`) language. Scoring is
`max(width, height)² × avgTicks`, lower is better, and every case must pass;
problems marked *footprint* ignore ticks entirely.

| Problem | Result | Score | Notes |
|---|---|---|---|
| Triangle | 19/19 | **1,500** | area² 100 × 15 ticks |
| History Lesson | 1/1 | **8,464** | footprint-only |
| Reverse a List | 20/20 | **369,229** | 16×16 × 1,442 ticks |
| Sort | 25/25 | **6,059,238** | 39×39 × 3,984 ticks |
| Brackets | 26/26 | **8,646,785** | 60×60 × 2,402 ticks |
| Packet Reassembly | 20/20 | 180,443,404 | |
| Sudoku Auditor | 20/20 | 575,105,767 | |
| Memory | 24/24 | 628,849,485 | |
| Plotter | 20/20 | 3,600,583,724 | display |
| Snake | 17/17 | 124,903,487,938 | display |
| Matrix Multiply | 20/20 | 267,001,259,039 | |
| Gradebook | 20/20 | 473,609,502,261 | |
| Subset Sum | 20/20 | 522,818,050,142 | |
| little-little-man | 14/28 | — | public only; scores 0 points |
| little-little-little-man | 10/21 | — | |
| pathfinder | 0/18 | — | setup frame correct, no BFS |

13 of 16 problems fully solved.

## Triangle — `T(n) = n(n+1)/2`

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

Walk order is `r M * + W 1 W }` then `s H` — computing `(n² + n) >> 1`, so no
division is needed. The two `W` swaps exist only to park `1` in the off hand for
the shift, because `}` shifts A by B and loading a literal always lands in A.

The instruction path snakes across three interior rows and the I/O rooms sit
side by side above it. That is worth far more than shortening the code: the
first flat 23×3 version scored 529×11 = 5819, while this 7×10 one scores
100×15 = **1500** — same instructions, 3.9× better.

## Reverse a List — rotate a FIFO

A little man has three storage slots — `A`, `B`, and the write-only `BP` — so
the list itself has to live in pipes. A FIFO cannot pop from the back, but it
can *rotate*: sending each value round the ring brings the last element to the
front, and repeating with a shrinking count emits the list backwards.

Folded to 16×16 it scores 256 × 1,442 = **369,229**. Derivation in
[`docs/solutions/reverse.md`](docs/solutions/reverse.md).

## Sort, Brackets, History Lesson

Same principle each time — pick the algorithm the pipe topology expresses
naturally, then fold the layout until the bounding box stops dominating:

- **Sort** — insertion via queue rotation, 39×39 × 3,984 = **6,059,238**
  ([`docs/solutions/sort.md`](docs/solutions/sort.md))
- **Brackets** — depth counter in a single accumulator, no stack needed,
  60×60 × 2,402 = **8,646,785**
  ([`docs/solutions/brackets.md`](docs/solutions/brackets.md))
- **History Lesson** — 2,810 fixed bytes under footprint-only scoring, so purely
  a packing problem ([`docs/solutions/history.md`](docs/solutions/history.md),
  generator [`gen_history.py`](docs/solutions/gen_history.py))

### The backtick trap

Backticks pair *down columns as well as along rows*, and a non-digit between a
vertical pair is a load error. A dense 6-cell token `` `NNN`s `` puts backticks
at offsets 0 and 4 going right but 1 and 5 going left, so columns misalign and
an `s` lands between a vertical pair:

```
Your program failed to load: expected a digit or a space between backticks,
but found 's' at (2, 2)
```

Adding a **leading space** makes the token symmetric — backticks at offsets 1
and 5 in *both* directions — so every column holds backticks in the same places
on every row. Costs one cell per byte; makes the program legal.

## The three that got away

**little-little-man** (14/28) passes every public case and no private one, so it
scores zero — the contest requires at least one private pass to be eligible for
points. The submitted program is a memorised lookup table, not an interpreter:
36,497 `s` instructions decoding byte-for-byte into the 14 public frames,
selected by 11 comparisons hashing `(W, H)` plus a raw grid byte. It is at a
permanent ceiling by construction.

**little-little-little-man** (10/21) fails the same way — all public pass, all
private fail. The leading untested hypothesis: the room is assumed to fill the
display box, so an *inset* room breaks any wall-vs-operator test that keys on
"is this cell on the grid boundary".

**pathfinder** (0/18) needs a BFS with an up/right/down/left tie-break and one
committed frame per move. [`gpt/pathfinder-agent.man`](gpt/pathfinder-agent.man)
gets the setup round right — its frame is byte-identical on all 7 public cases —
and proves the board-in-a-pipe store plus the DATA/SWAP display plumbing, but
has no search. [`simd_display.py`](simd_display.py) extends the simulator to
drain display pipes and render committed frames, which is what made display
problems verifiable at all.

## Language notes worth keeping

- A pipe **must begin with an arrowhead** whose backward cell is on the source
  room's border. `--->` is not a pipe at all: the program loads clean and then
  every case dies `no-pipe`.
- Display rooms use `=` and `:` for borders, not `-` and `|`.
- Program size is capped — a 28 MB grid was rejected `413 payload_too_large`.
- Submissions are graded on your **best** result per problem, so experimenting
  is free: a worse submission can never lower a banked score.

`CONTRACT.md` carries the full language reference and the working notes.
