# CLASSES — the problem-class casebook

Seven shapes cover everything this repo has met. Identify the class first: it
picks the template, the cost model, and the landmine list, and every one of
those was learned the expensive way on one specific problem.

Score is `max(width, height)² × avgTicks`, lower is better, so every class
entry below says **which term dominates** — that is what you optimize, and
optimizing the other one is how afternoons disappear.

Companions: `PLAYBOOK.md` (the order of operations), `harness/estimate.rkt`
(the cost oracle), `NOTES.md` (the evidence behind every claim here).

---

## 1. PURE FUNCTION — no state at all

**The smell.** One value in, one value out, no memory between inputs, and the
whole program is under ~14 walked cells. Ticks are tiny, so **area is the
entire score** and the optimum is a packing problem, not a compiler problem.

**Template + exemplar.** No template. `synth.rkt` synthesizes the op sequence
from the test cases (Rosette, idiom vocabulary, finite bitwidth) and
`place.rkt` finds the optimal packing exhaustively. `problems/triangular.rkt`,
`solutions/triangular.man` — **8×8 @ 13 ticks = 832, leader tie, and apparently
the true optimum.**

**Cost structure.** Area², absolutely. 13 ticks is a rounding error; one cell
of max-dim is ~24% of the score at this size. Judge multiplier **1.00** — with
ticks this small the hidden set cannot be heavier in any way that shows.

**Landmines.**
- Search beats hand analysis here, twice over: hand analysis missed the 8×8
  layout on two separate attempts and `search8.rkt` rediscovered it
  independently after two fixes (NOTES "Scoreboard").
- Two tricks make 8×8 fit: **crash-ending code** (no `H`, so 12 walked cells
  fit a 2-row interior — errors after the final emission are free) and
  **diagonally interleaved I/O rooms** wired with length-2 hook pipes.
- `harness/estimate.rkt` is **out of model** below ~100 ticks. Do not consult
  it here.

---

## 2. PIPELINE — the state fits in registers

**The smell.** Per input item the machine needs *k* live values, and you can
give each of *k* rooms exactly one persistent value. No random access to
history; each item is consumed, transformed, forwarded. If you catch yourself
about to build a ring "for the stack", check whether the stack is one integer
first.

**Template + exemplar.** `define-pipeline` (`harness/templates.rkt`): an
ordered chain of one-in-one-out rooms, I at the front, O at the back.
`problems/brackets-sol.rkt` — **27×25 @ 617.4 local = 450k; judge 26/26,
1265.27 avgTicks, score 922,381.** History Lesson's decoder is a five-stage
pipeline too (`D1 → D2 → C0 → CD → O`).

**Why it wins.** One pipe per direction makes `r`/`s` targeting *trivially*
correct: no `#:col-order`, no `#:accept?` veto, no MARK protocol, no tanks.
Brackets is **smaller than the whole ring family** (27×25 vs sort's 27×28,
reverse's 27×26) despite doing more arithmetic. Control flow in a second room
is the cheap third register.

**Cost structure.** Ticks are `ops × rails-per-op` — there is no ring term at
all, so the per-item cost is walking between chains inside two small rooms
(brackets: ~55 ticks/char at n=64). Area and ticks are roughly balanced. Judge
multiplier **1.70–2.10** (brackets measured 2.05 — 26 hidden cases against 9
public ones, all near the spec box).

**Landmines.**
- **Pick the arithmetic encoding for the *spec maximum*, not the public tests.**
  Brackets' bijective base 3 is correct through depth 39; the obvious
  2-bits-per-level base 4 fails **at** the spec maximum of 32, because bit 63
  sets, `}` sign-fills, and an emptied stack reads as −1 rather than 0. The
  wrong answer appears exactly where a private test will look. (NOTES
  "Brackets: the stack IS a register".)
- **Design the message around the receiver's branch.** `+t / −t / 0` makes C's
  whole dispatch one `X` and its push arm a tight body.
- **One stub block can buy six columns.** Threading a branch's zero arm onto
  its own chain "because it is the fall-through anyway" made a 17-token lane
  and D compiled to 21×6; an empty stub as a chain cut point gave 15×9. Chain
  length is lane length and lane length is width.
- A value you need **once, at the end** can live in the backpack and be counted
  out — brackets gets a 1-based position with no position counter by *not*
  decrementing BP during the scan and decrementing it during the mandatory
  drain instead.

---

## 3. RING SERVER — the state exceeds the registers

**The smell.** The machine must remember more than two values across
operations, but the state is **bounded and small** (tens of values) and access
is naturally sequential. The ring exists to hold **state**, not to move values.

**Template + exemplar.** `define-ring-server` (`harness/templates.rkt`):
controller C + forwarder F + two melted tanks + 3×3 I/O rooms.

| exemplar | shape | local | judge |
|---|---|---|---|
| `problems/reverse-sol.rkt` | 27×26 @ 2084.3 | 1.52M | 20/20, 3197, **2,330,613** (manual 26×26: 2,147,111) |
| `problems/sort-sol.rkt` | 27×28 @ 3533.7 | 2.77M | 25/25, 5418.48, **4,248,088** |
| `problems/tcp-sol.rkt` | 32×32 @ 4195.2 | 4.30M | 20/20, 7177.5, **7,349,760** (manual 28×31: 7,033,270) |

**The one real decision: MARK vs direct-out, and it is register pressure.**
Outputs normally ride the ring behind a MARK (2²⁰, outside the value domain)
and F diverts them, which keeps C **single-outgoing** and its targeting easy.
Choose `#:out-src 'C` instead — a second C→O pipe, F degenerating to a two-op
bouncer — when a register invariant must survive every emission: tcp's drain
loop holds `waiting` in B and MARK needs B for the marker, so the two are
incompatible. The price is four pipes on C, which is where l1's targeting model
runs out (see the landmines).

**Cost structure.** Ticks dominate the *tuning*, area dominates the *score*.
Per operation: `ticks/cell × walk-fraction × ring-resident + 20 × rails-per-op`
(estimate.rkt). Two measured facts that matter more than they look: **rails
between chains are the tick budget, not the loops** (~150 ticks per input value
walking between chains vs ~10 per loop iteration), and **ring capacity is not a
lever** (tcp caps 6..20 give byte-identical worlds; sort CAP 24→10 is 3.5%, and
bigger tanks cost *ticks* not area). Judge multiplier **1.50–1.75** when a
public case already sits at the spec maximum.

**Landmines.**
- **A SENTINEL in the ring is what buys tight loops.** A body that has to test
  the backpack is disqualified from `#:tight` by construction; terminate on a
  sentinel value instead and the compare goes 38 ticks → 10. Better still, make
  the **sentinel carry the state** the register was holding (tcp's
  `−(waiting+1)`), which frees B for the whole path.
- **Don't store what is provably empty.** tcp's window is 16 seqs but slot 0
  drains the instant it fills, so the ring holds 15 — and *that* is what makes
  a window slide exactly one pop plus one push with no realignment.
- **One late `r ring` op can cost the whole room.** `#:col-order` discriminates
  by column, so the westernmost `r in` must sit east of every `r ring`; a
  33-cell chain whose last `r ring` sat at offset 30 made *no* layout under 41
  wide exist. Keep the emit spine out of any chain that also reads the ring.
- **Four pipes on one room is where l1's targeting runs out.** One split
  fraction serves every group, so a chain holding ops from both sides is
  placeable only if the split falls exactly between them. Fix: make every chain
  **one-sided**, cutting at transfers that are gotos anyway and inserting empty
  blocks purely as cut points. tcp went 6 coarse chains (unlayable) → 12
  one-sided chains → 25×25.
- **`#:near` is not optional for a melt whose partner is far away** — sort's
  unhinted solver picked F's west end and the world blew out 4 columns.
- **Give every room all four degrees of freedom** before concluding a dimension
  is binding. Sort was stuck at 31 columns because O's *row* was pinned by a
  formula; freeing it dropped the world to 30×29 immediately.
- **A tight body cannot be rail-entered** from two arms, and cannot hold a
  backtick literal.

---

## 4. HEAVY-STATE SERVER — the ring *is* the memory

**The smell.** State at the spec maximum is 80–200+ values, cost is
`ops × ring-length` (quadratic in the instance), and the ring's *capacity*, not
its protocol, sets the floorplan. This is a ring server whose tanks are 55% of
the committed cells.

**Template + exemplar.** Still `define-ring-server` in principle, but
`problems/memory-sol.rkt` stays **hand-written** and is wrapped by the registry
— it carries a `#:capacity` argument and a `#:pin?` migration path that nothing
else wants, and a parameter with exactly one user is how a template becomes a
second copy of the thing it replaced.

| exemplar | shape | judge |
|---|---|---|
| `memory-sol.rkt` (MARK, bump tanks) | 34×34 @ 11901.1 = 13.76M | 24/24, 70133.54, **81,074,374** |
| `memory-signdivert-sol.rkt` (sign-as-mark) | 33×33 @ 10904.4 = 11.87M | 24/24, 61105.5, **66,543,935** |
| `memory-bouncer-sol.rkt` (direct C→O) | in flight | — |
| `solutions/memory-manual.man` (hand-drawn) | 33×33 | 24/24, **76,426,791** |
| `problems/gradebook.rkt` | spec max 16×5 = 80 ring values | in flight |

**Cost structure.** Ticks, overwhelmingly — and the **judge multiplier is
5.60–5.90**, the single most important number in this class. Memory's biggest
*public* case touches 41 distinct addresses against a spec maximum of 100, cost
is `ops × ring length`, and the hidden set finds the maximum: local 12123.6 →
judge 70950.33. **Treat local memory-class ticks as a ranking signal only.**

**The asymptotic lever is SHARDING**, not micro-optimization. The per-value
protocol is worth single-digit percentages once (MARK 10 ticks/value →
sign-divert 8 → bouncer ~6, and memory's F genuinely is its rate limiter: the
forwarder v2 upgrade alone was −17.1%); the *seek length* is what is quadratic.

**Landmines.**
- **Capacity is sized at the SPEC maximum and stress-tested there.** Memory's
  100-address case is the one that sizes the ring, needs ~311k ticks, and
  reports FAIL as a pure cap artifact against a 200k verify cap.
- **A bumped tank has NO capacity margin** (exactly `cap` cells) where the melt
  gave 221/218 against a requested 210. Re-run every capacity-sensitive stress
  case after switching former — at a real cap.
- **The former is part of the bake.** Same bump former: 34×34 at its own
  floorplan, 36×36 at the melt's. Never evaluate a former at a floorplan fitted
  to a different one, and pass `#:tank-former` to the builder rather than
  parameterizing `current-tank-former` (memory's builder no longer reads it).
- **First-fit bumping starves the next channel**, and the error names the
  victim (`ring-out`: "no sweep works") rather than the culprit (`ret` filled
  the band). Generate a family and keep the most compact by bounding box.
- **Seek idioms that pay:** lazy storage (only written cells live in the ring),
  the `~` XOR compare making `X` a free three-way dispatch (match / mismatch /
  sentinel), and the backpack holding the opcode so `d` forks READ/WRITE at
  both the match and not-found sites.

---

## 5. BOUNDED SEARCH — DFS with prunes, in a machine with two registers

**The smell.** The answer requires exploring an exponential space, the tick cap
is the binding constraint (subset's page states **15,000,000**, not the usual
5M), and the honest question is not "how do I lay this out" but "does it fit at
all".

**Template + exemplar.** `problems/subset.rkt` — spec, 7 public cases, 9 in-box
stress cases, a 400-case brute-force equivalence battery, registered with
8M/15M caps. **No solution file yet, deliberately**: the measurement gate says
what must be built and the numbers are why it is not the obvious thing.

**Cost structure.** Ticks against the cap, and nothing else matters until it
fits. Two budgets multiply:
- **per-node cost** = `index-steps/node × ticks/rotation × cells-per-index`.
  Measured: 5.7 index-steps per node (1 descent + ~4.7 wrap), ~8 ticks per
  rotation, K cells per index — and **K multiplies the dominant term**.
- **node count** under the prunes: public n=20 case 112k → 25k; median 29k, p90
  128k, max 387k over 300 random in-box cases.

**Landmines.**
- **Prototype first, always.** This is the class where the measurement gate is
  mandatory, and where four alternative architectures were killed with numbers
  before any grid existed (restart-lap DFS ~6× worse; greedy+oracle wrong ratio
  of complexity to gain; bitset DP 125×125 of pure pipe; meet-in-the-middle
  needs sorted halves).
- **Prune soundness is a proof obligation.** Every prune must be a *necessary*
  condition so pruning cannot change the answer, and the battery pins that
  against exhaustive enumeration. Include-first DFS gives lex-smallest for free
  — but **only because all values are positive**; without that, `{0}` vs
  `{0,1}` orders the wrong way.
- **A ring is a bad DFS stack, and the cost is exactly measurable**: forward
  rotation only, so index *i* → *j* costs `(j−i) mod n`. A backtrack whose last
  decision was an include costs **zero**; one over *k* excludes costs `n−k`.
- **Packing is blocked by the off hand.** Keeping the remaining target `r`
  permanently in B makes every prune two ops — but every unpack op (`/ % } &`)
  needs its constant in B, and materializing it destroys `r`. Hence one field
  per ring cell. Look for the arithmetic escape (`/` leaving `A=h, B=rem`, then
  `M`, then `*`) before splitting a room.
- **State the residual risk in the report.** "n≥19, dense random, no solution
  exceeds the cap" is a prediction that tells the next agent what to blame.

---

## 6. FIXED-OUTPUT / FOOTPRINT — ticks are free, data has mass

**The smell.** No input, one test case, and the score is `max-dim²` alone
(`avgTicks` comes back **null**). Every habit inverts: ticks are free to the
cap and the only currency is **cells**.

**Template + exemplar.** No template — a compression toolchain.
`problems/history.rkt` (spec + assertions), `problems/history-gen.rkt`
(compressor + grid emitter), `solutions/history.man`. **Judge PASSED 1/1,
91×90 = 8281.** The denser 87×87 escape build is kept as
`history-esc-stepcap.man` because the judge step-capped it.

**Cost structure.** Area² and nothing else. The density budget is **~2.87
bits/cell** for a backtick literal (19 digits + 2 ticks + one `s` per 63-bit
word), so a **decoder cell is worth ~3 bits** — always price the decoder in
cells against the data it saves. That is why rank-escape beat Huffman:
Huffman's ~2% coding win costs a ~600-cell canonical compare chain against a
~150-cell escape decoder. Measured ladder (content cells): raw base-123 6930,
Huffman 4987+decoder, uniform (β,T) escape + 29-token dict **5087 → shipped**.

**The three literal rules, all judge-calibrated by rejections.**
1. Backticks pair consecutively **per row** within a room, and every cell
   between a pair must be a digit or a space — whether or not any man walks
   there. A stray op between two same-row backticks is a LOAD error.
2. Backticks pair **per column too** (this refuted a standing claim in NOTES).
   Rejection text: *"expected a digit or a space between backticks, but found
   's' at (2, 10)"* — judge coordinates are **(col, row)**.
3. A clean paired span **is** a vertical literal and its value is range-checked
   **in both directions**. Rejection: *"numeric literal exceeds the signed
   64-bit register range — walked top-to-bottom it reads 483…843 (35 digits) at
   (10, 16)"*. Keep paired spans ≤ 18 digits.
   Exemptions from accepted files: odd tick counts per column are fine,
   between-pair and after-last-tick cells are unconstrained, cross-room spans
   are exempt. `sim.rkt`'s `literal-column-warn?` has the polarity **backwards**
   relative to the judge — it warns on clean spans and says nothing about
   op-containing pairs — so carry your own lint (`lint-room-columns!` in
   history-gen is the model).

**The ACTIVITY-CAP model — the step cap is not wall-clock ticks.** Six delay
probes settled it: a 2-man 2.196M-tick program **runs to completion**, while
the 6-man escape decoder **step-caps at 1.95M local ticks** even after
early-halting its data men (~6M man-steps, under the 7.5M a passing probe
exhibits). Every surviving model charges for **pipe-value movement** — the
decoder's 89-value ring travels ~19M value-cells over a run. So:

> **activity ≈ ticks × (men + circulating-fraction × ring-resident)**, and
> **a big circulating ring is not free**: value-count × pipe-length × rotations
> is a budget. Blocked-full residents cost nothing; only values with a free
> cell in front of them move.

`estimate.rkt` implements exactly this with those two calibration points
(≤5M comfortable, ≤10M tight, above that redesign).

**Landmines.**
- **A serpentine data room is a data bus**: westbound rows are the logical row
  *reversed* (literals read in walk direction), the per-row tail word is packed
  to a digit budget so rows fill exactly, and both-direction 64-bit validity
  must be checked per word — reversed-digit overflow does occur.
- **Ring capacity is pipe CELLS, and detours are storage.** A deliberate loop
  in an exit pipe is a legitimate way to buy capacity.
- **Registers, not layout, dictate the architecture.** Three live values with
  two readable registers forces a parking pipe or a pipeline; the single-room
  mixed-radix version died in an unroutable `s`/`r` targeting web after ~10
  layout iterations, and the pipeline's worst room has margins ≥ 4.
- **`X`'s 0-arm goes straight, so `X` is a lousy 2-way brancher** when 0 is a
  live case. Clean 2-way tests: `b` + `m`×T + `d`/`a`, or quotient-vs-0 where 0
  genuinely terminates.
- **P2 (restoring ring rotation after each lookup) was 70–80% of all ticks.**
  Fine here; fatal anywhere ticks are scored.

---

## 7. DISPLAY — infrastructure ready, no problem yet

**The smell.** The problem page shows pictures and states a resolution. Judging
is a **streaming frame compare** — one frame per SWAP — scored by the tick of
the **final matching frame**; exactly one display at the stated resolution is
required and **emitting any output is an error**.

**Template + exemplar.** None yet — no display problem has been published to
us, so there is no id and `submit` refuses. What exists: full LM-75 support in
`sim.rkt` (pipes classified by side: top ADDR, left DATA, bottom SWAP;
right/corner/duplicate = load error; ADDR→DATA→SWAP once per tick in stage 3; a
frame log of every SWAP, delivered via `sim-frame-log` / `sim-displays` /
`sim-error-reason` because `sim-result` is positional), the harness path
(`display-problems` in `harness/problems.rkt` — add a name and a resolution and
`run-suite` switches to streaming frame compare and `final-match-tick`), and
`tests-display.rkt`, 53 checks end to end.

**Cost structure.** Unknown — but note that ticks are the *final matching
frame*, so frames after it are as free as ticks after the final emission, and
`H` may or may not be free (open question 3).

**Every LM-75 semantic we implement is spec-derived and UNCONFIRMED.** Read the
open-questions list before writing one. The probe kit is `probes/d*.man` +
`probes/display-probes.md`, regenerated by `probes/gen-display-probes.rkt`; all
of them are **EDITOR probes** — the observable is the screen widget, not the
output box:

| probe | question | cost if we are wrong |
|---|---|---|
| `d1-data-swap-same-tick` | does the frame include DATA written on the same tick? | a spare tick before every SWAP — 4096 wasted ticks at 64×64 |
| `d2-addr-data-same-tick` | ADDR-before-DATA ordering within a tick | mis-addressed pixels |
| `d3-swap1-cursor` | SWAP 1 cursor/buffer preservation | drawing loops desync |
| `d4-empty-swap` | does an empty SWAP commit a frame? | a stray SWAP desynchronises the whole streaming compare |
| `d5-idle-o-room` | may a display-judged program keep an unused output room? | builders need a no-O mode |
| `d6-post-halt-flush` | does a SWAP in flight survive the last halt? | `H` stops being free; keep a man alive past the last frame |
| `d7-data-out-of-range` | what the judge calls a display error, and whether earlier matching frames still count | the latecrash lesson, on the display side |
| `d8` / `d8b` | do corner / right-side attachments really refuse at level 1? | `display-validation-level` switches to `'pipes` |
| `d9-two-displays` | duplicate counting by distinct partner room | load error |

Round gating (frames gate rounds exactly like output) is modelled by neither
our sim nor anything else — same position as normal problems.

---

## The decision tree

The `OVERVIEW.md` recipe's question sequence, extended with the classes above.

```
0. Is the score footprint-only (avgTicks null / "ticks do not matter")?
   YES -> CLASS 6, FIXED-OUTPUT.  Build a compressor, price the decoder in
          cells at ~3 bits/cell, and check the ACTIVITY CAP before the tick cap.
   NO  -> continue.

1. Is judging a FRAME COMPARE at a stated resolution?
   YES -> CLASS 7, DISPLAY.  Read the open questions first; the semantics are
          spec-derived and unprobed.
   NO  -> continue.

2. Does the answer require SEARCH over an exponential space?
   YES -> CLASS 5, BOUNDED SEARCH.  Prototype in Racket and pass the
          measurement gate BEFORE building anything.  Check the stated tick
          cap — it may not be 5M.
   NO  -> continue.

3. Is there any state to carry between inputs?
   NO, and the program is under ~14 cells -> CLASS 1, PURE FUNCTION.
       synth.rkt + place.rkt; the score is area².
   NO, but it is bigger than that -> CLASS 2 with one room.
   YES -> continue.

4. Does the state fit in REGISTERS — A, B, and one write-only backpack per
   room, counting one persistent value per room you are willing to add?
   YES -> CLASS 2, PIPELINE (`define-pipeline`).  Control flow in a second
          room is the cheap third register.  Reach for this first: it is
          smaller than the ring family and its targeting is trivially correct.
   NO  -> continue.

5. How big is the state at the SPEC MAXIMUM?
   Tens of values, sequential access -> CLASS 3, RING SERVER
       (`define-ring-server`).
   ~80-200+ values, cost quadratic in the ring length -> CLASS 4,
       HEAVY-STATE SERVER.  Expect a ~5.85x judge multiplier, size the tanks at
       the spec max, and look for a sharding-shaped asymptotic lever before
       tuning the per-value protocol.

6. (Ring server only) Must a register invariant survive every emission?
   YES -> `#:out-src 'C`: a direct C->O pipe, F degenerates to a bouncer.
          Price: four pipes on C, so every chain must be one-sided.
   NO  -> the MARK protocol.  C stays single-outgoing and targeting is easy.

7. Run `harness/estimate.rkt` on the SPEC MAXIMUM case before writing the CFG.
   comfortable -> build it.
   tight       -> build it, and make the spec-max stress case the first thing
                  you measure.
   redesign    -> change the algorithm or the state layout now, while nothing
                  has been laid out.
```

## Addendum: room count is a free variable

Nothing limits a solution to the C+F pair. l2's `assemble` takes arbitrary
rooms and channels — the FIXED-OUTPUT exemplar (history) is a five-room
pipeline — and `define-pipeline` is N-room by construction. Only
`define-ring-server` hardcodes two compiled rooms; when it doesn't fit,
declare rooms/channels directly (see problems/memory-signdivert-sol.rkt,
problems/history-gen.rkt).

Reach for 3+ rooms when:
- **a room grows past ~40 blocks** — two half-rooms pack into a smaller
  bounding square than one big one, and area enters the score squared;
- **pipe-op targeting fights** — splitting read groups across ROOMS
  removes the col-order band problem structurally (each room has fewer
  pipes; the tcp four-pipe scar becomes a non-event);
- **timing wants a pipeline** — stage-rooms stream ring cells
  continuously (~1 tick/cell) where one man stop-and-gos (~10);
  sharding (dispatcher + parallel rings) attacks O(ring) seek costs.

Cost per extra room: walls (~2 rows+cols), one channel + latency per
crossing value, and one more man idling when idle (free). Price it —
don't default to two.

## Addendum: STATION FLOORPLANS — use the packer, and score against LATENCY

`floorplan.rkt` is the layout pre-pass for **chain / pipeline worlds**: N rooms
with fixed or menu-chosen sizes, a mostly-linear channel chain (room k talks to
room k+1, every room 1-in-1-out), fixed 3x3 I/O rooms, and — the thing that
makes it tractable — **no tanks**, because a station world holds its state in
registers. It emits ORIGINS for `l2`'s `assemble`; l2 is untouched, gravity
still composes on top (`plan-shift`), the router is still the oracle.

**When to reach for it.** Any world of 5+ rooms whose channels form a chain.
It is worth ~40% of the score there: `sudoku-station` went 41x41 / 8,639,247 ->
31x33 / 4,966,874 with no change to a single CFG, and it beat a careful
hand-drawn floorplan of the same rooms by 5%. Gravity cannot substitute — it
moves one room by one cell, so it can shave a column but it can never re-band a
stack. **The floorplan is a structure, and structures need a search.**

```racket
(define rooms (list (fp-io 'I 'in) (fp-cfg 'D1 d1-menu) ... (fp-io 'O 'out)))
(define links '((in I #f D1 in) (d12 D1 d2 D2 d1) ...))
(guillotine-search rooms #:max-dim 34 #:links links)   ; -> ranked plans
(guillotine-plan rooms BAKED-TREE)                     ; -> the shipped one
(plan-attach-cells plan links)                         ; -> the attach cells
```

Two packers live there. The **snake shelf packer** lays rooms along shelves in
chain order, reversing per shelf — predictable, exact DP per width cap, and on
sudoku-station it bottoms out at 34x34. The **guillotine packer** is the one to
use: recursively cut the rectangle and give each side a CONTIGUOUS run of the
chain, so every cut is crossed by exactly one channel; the Pareto DP over
segments is exact, runs in well under a second on 11 rooms, and it is what
found 31x33. The shelf snake is a strict special case of it.

### Three landmines, each of which cost an hour

1. **Do not hand l2 unconstrained walls at this room count.** `assemble` keeps
   `attach-tries` assignments per (room, kind) group and CROSS-PRODUCTS the
   groups; an 11-room chain has ~20 groups, so `#:attach-tries 2` is 2^20 picks
   and the process grows to 25 GB. At `#:attach-tries 1` it terminates but the
   single centre-ranked pick per room usually has no coherent completion, and
   assemble dies in its own error path with `first: contract violation ...
   given '()`, naming neither room nor channel. **Let the packer name the exact
   cells** (`plan-attach-cells` -> `attach-at ... #:fixed`); the search never
   runs. Safe on a chain because with one channel per kind the sim's
   nearest-segment targeting rule is satisfied by any legal cell — a broadcast
   or a merge room does NOT get this and must go back through l2's solver.
2. **Two cells of clearance, and CORNERS COUNT.** A pipe needs two free cells
   (l2 rejects a length-1 path and a bend needs a cell to bend at). One free
   row between stacked rooms is not enough; a 2-row corridor between two full
   rooms carries a vertical hop but NOT a sideways hook, because the climb back
   up is a bend whose backward cell is the next room's wall and `bend-ok?`
   refuses it. The way out is not wider corridors, it is **flush rooms with
   ragged widths**: the overhang beside a narrower room is a pocket, and the
   CORNER cell facing it is a judge-legal attach point costing zero separating
   rows or columns. Reserve ~2 cells of margin around the whole packing, too —
   a room flush against coordinate 0 has no outward cells at all.
3. **Rank by max-dim^2 x SINGLE-ROUND LATENCY, not by local average emit.**
   The judge withholds round N+1 until round N answers, so it measures latency
   while a local run measures throughput, and a pipelined machine separates the
   two. On sudoku-station `judge avgTicks = 48.5 x latency` fits both
   previously graded builds to within 0.3% and predicted the third to within
   0.04%. Latency is one sim run on a one-round input. Ranking by local avg
   picks the wrong floorplan: the 32x33 world with the better local average is
   worse on the judge than the 31x33 world with the shorter pipes.
