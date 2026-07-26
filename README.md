# ICFP Programming Contest 2026 — team `arvindcr4`

Solutions in the Littleman (`.man`) language.

| Problem | Result | Score | Notes |
|---|---|---|---|
| Triangle | 19/19 | **1500** | area² 100 × 15 ticks |
| History Lesson | 1/1 | **21904** | footprint-only (144×148) |

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
side by side above it. That is worth far more than shortening the code: score is
`max(width,height)² × avgTicks`, so the first flat 23×3 version scored 529×11 =
5819, while this 7×10 one scores 100×15 = **1500** — same instructions, 3.9× better.

## History Lesson — emit 2810 fixed bytes

Footprint-only scoring (ticks are ignored), so this is purely a packing problem.
Each byte becomes a 7-cell token `` ` `NNN`s `` laid in a boustrophedon: rows run
left-to-right and right-to-left alternately, with the token reversed on
right-to-left rows since a literal walked backwards reads backwards.

**The trap:** backticks pair *down columns as well as along rows*, and a non-digit
between a vertical pair is a load error. A dense 6-cell token `` `NNN`s `` put
backticks at offsets 0 and 4 going right but 1 and 5 going left, so columns
misaligned and an `s` landed between a vertical pair:

```
Your program failed to load: expected a digit or a space between backticks,
but found 's' at (2, 2)
```

Adding a **leading space** makes the token ` `` `NNN`s `` ` symmetric — backticks at
offsets 1 and 5 in *both* directions — so every column holds backticks in the same
places on every row, and each vertical pair encloses either nothing or spaces.
Costs one cell per byte; makes the program legal.

## Language notes worth keeping

- A pipe **must begin with an arrowhead** whose backward cell is on the source
  room's border. `--->` is not a pipe at all: the program loads clean and then
  every case dies `no-pipe`. Shortest legal pipe is `>>`.
- Score is `max(width,height)² × avgTicks`. The bounding box dominates — square
  beats short.
- Backticks pair on rows **and** columns independently.
- The submission API is behind Cloudflare and rejects scripted clients with
  `403 error code: 1010`; POST from a real browser session.
