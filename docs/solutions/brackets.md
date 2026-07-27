# brackets.man — balanced-bracket checker

**Problem.** One length-prefixed string: a count `n`, then `n` ASCII codes,
each one of `( ) [ ] { }` (40, 41, 91, 93, 123, 125). Output a single
integer: `0` if the string is balanced, otherwise the 1-based position of
the first offending closer (wrong type, or nothing open), or `n + 1` if the
string ends with openers still unclosed. `0 ≤ n ≤ 64`, nesting depth ≤ 32.
Scoring: footprint × ticks.

## Idea: a LIFO stack in one hand, base-4 digits

The matching algorithm needs a stack; pipes are FIFO, so the queue circuit
from `reverse.man`/`sort.man` doesn't fit. Instead the whole stack is **one
integer** in a dedicated man's off hand: each level is a base-4 digit, with
openers encoded 1 (`(`), 2 (`[`), 3 (`{`). Codes start at 1 so that digit 0
never occurs — `stack == 0` means empty, and a pop on an empty stack
harmlessly returns 0, which no opener uses.

- **push v**: `n = n*4 + v`
- **pop**: `/` is a one-op divmod — quotient (the popped stack) lands in the
  main hand, remainder (the top digit) in the off hand.

Depth ≤ 32 × 2 bits = 64 bits exactly: the worst case (32 nested `{`) is
`4³² − 1 = 2⁶⁴ − 1`, which overflows *signed* int64. Fine in our sim
(Python ints); the official runtime's width is unverified, but the depth
constraint matching the encoding so exactly suggests this is intended.

## Three rooms, three jobs

```
stack room      holds the stack in B; cmd >0 = push (value follows), 0 = pop
main room       reads input, classifies, drives the stack, decides the verdict
counter room    holds the 1-based position in B; owns the only pipe to O
```

The **counter room** exists because no register in the main room can hold
the position: `BP` is write-only and busy with the input countdown, `B`
must hold the bracket code during classification, and `A` is clobbered by
every literal. It doubles as the reporter because the output room accepts
only one pipe — whoever owns it must print everything. Its protocol:
`0` = increment, `1` = print position and halt, `2` = print 0 and halt.

**Stack room** (`@>rb4dW/Ws v` / `>*Wr+Wv` / `^ <`): reads a command,
`b`+`d` branch on it. Pop (cmd 0) falls through `W/Ws` — swap the stack
into `A`, divmod by the 4 loaded before the branch, swap, send the top
back down. Push (cmd > 0) turns into `*Wr+W` — multiply the stack by 4,
receive the pushed value, add, swap the new stack back into `B`.

## Main room walk

```
|@rb>d     0s   rX                 v |     header + countdown + end-check
|   m>rWv        >               v   |     bracket read; leftover arm
|              >v                0   |
|       >`040`-X 1s1sv           s   |     openers: push 1 / 2 / 3
|       >`091`-X 1s2sv           1   |
|       >`123`-X 1s3sv           s   |
|              >v      >> 0s1sH  H   |     mismatch: inc, report position
|       >`041`-X 0srW1-X v         2 |     closers: pop, compare top
|       >`093`-X 0srW2-X v         s |     balanced: cmd 2 → prints 0
|       >`125`-X 0srW3-X v         H |
|       v      <<      >^            |
|                    0 >^0           |     per-bracket increment (both exits)
|   ^                s   s           |
|                    <   <           |     return through m to the countdown
```

**Header.** `r b` load `n` into the backpack; `d` turns down into the loop
while `BP > 0` and falls straight to the end-check at zero. Each loop
iteration reads one code (`r`), `W`s it into `B`, and walks the classifier
ladder.

**Classifier ladder.** Six rows of `` >`lit`-X ``: load the candidate code,
subtract `B`, and `X` — zero means "this row's bracket", nonzero falls
through serpentine `>v` / `<<` connectors to the next row. Order is
irrelevant (each code matches exactly one row); only the wall-distance of
each row's pipe ops matters (see below).

**Openers** send `1` (push cmd) then their encoding to the stack pipe.
**Closers** send `0` (pop), block on `r` for the top, and compare it with
their expected encoding (`W c - X`): zero = match, continue; nonzero —
either sign, including the empty-stack 0 — merges into `>> 0s1sH`, which
increments the counter one last time and asks it to print. Both surviving
exits (push, matched pop) walk a `0 s` increment on their way to the shared
return lane, which climbs through `m` (countdown) back to the header `d`.

The increment placement is the position-correctness trick: brackets
1…i−1 each incremented on their way back, and the error path adds the
i-th increment itself, so the counter prints exactly the offending
position. The same shape gives `n + 1` for leftovers at no extra cost.

**End-check.** When the countdown hits zero: `0 s` pops the stack once,
`r X` inspects the top. Zero → stack was empty → send `2` (counter prints
0). Positive → openers left → send `0` then `1` (counter prints `n + 1`).

## Verification notes

- `littleman address` is mandatory after any layout change here: the pop
  `0s` cells and the counter pipe compete, and four sends win by **margin
  1** (this exact bug shipped in an earlier draft — the `]`/`}` pop
  commands went to the output pipe and printed spurious zeros).
- `littleman trace` reports two possible wall hits, both dynamically dead:
  the ladder's no-match fall-off (inputs are guaranteed bracket codes) and
  the negative arm of the end-check `X` (a stack top is never negative).
- The stack and counter men never halt (they block on `r` forever after
  the verdict); tests assert output within a tick budget, matching the
  other never-halting solutions.

Footprint 34 × 60 = 2040. Covered by `tests/test_brackets.py` (all nine
public cases plus a max-depth stress case and a small differential fuzz).
