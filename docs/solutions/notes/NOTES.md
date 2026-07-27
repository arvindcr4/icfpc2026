# Judge facts (confirmed against the authoritative interpreter)

- **Score ticks = tick of the final correct emission.** Not run end: a
  program that emits then blocks forever to the step cap scores its
  emission tick (probe a1); a late `H` costs nothing (a2). Post-halt
  flush ticks count when emission happens during them (a3).
- Therefore `H` is never needed for scoring; ending by blocking (`r` on
  exhausted input) is free. Errors are only fatal if they occur before
  the final emission (latecrash: wall error one stage after emission
  passes). For multi-round problems an error still kills later rounds —
  servers should block, not crash.
- Tick order within a tick: pipes shift, output emits / input feeds,
  men execute, men move. A wall error fires when the man *executes* the
  wall cell, one stage after the emission window of that tick.
- Pipe grammar: start arrowhead with its backward cell on the source
  border; body glyphs match the run axis; bends are arrowheads pointing
  the new direction; terminal is the first arrowhead whose forward cell
  is a foreign room border. Corners are valid attachment cells on both
  ends (latecrash, c1). Min length 2. Adjacent parallel pipes are legal
  (b1) — the parser is walk-based, not adjacency-based.
- Two rooms 1 cell apart cannot be piped (any candidate start cell is
  already terminal => length 1). Rooms need >= 2 cells of clearance
  along the pipe's approach axis.
- identity 4 ticks, record.man 14 (1134), latecrash 13 (1053) — sim
  reproduces all exactly.

# Reusable idioms (post-memory)

- **tight loops** (l1 `#:tight`): hot head/body loop pairs compile to a
  2-row circuit — body inverted westward under the head's lane, cw drop
  in, `^` hop back onto the join. No rail transfers. Body must be ops +
  (goto head) and be the branch's cw arm.
- **register-invariant forwarder**: keep the compare constant in B
  permanently; per-value cycle `r - N X` + tight body `W - s + M`
  (recover v, restore B). ~12 ticks/value vs 27 naive. Negative arm
  provably unreachable when values < the marker.
- **empty-line compaction** (l1+l2): all-empty rows/cols delete safely —
  motion is straight-line through empties. Shrinks area AND ticks.
- **AABB floorplanning**: rooms rigid, serpent tanks flexible-w/h;
  stack tanks in one column, keep routing corridors (a room flush
  against the canvas edge can topologically trap a pipe).
- **targeting by geometry**: same-wall channels discriminate by
  column (or row) only; mixed-read blocks split across lanes; dot
  padding positions pipe-op cells.
- **melted tanks** (l2 `chan-spec` capacity = a bare NUMBER): instead of
  declaring a free rectangle for a serpentine, l2 grows a boustrophedon
  snake of exactly `cap` cells through whatever space is actually free,
  clamped to the ROOM BOUNDING BOX (cells inside it are free real estate
  — empty rows/cols compact away — while one row above the topmost room
  costs a row; relax the shorter side first, it is free under max-dim^2),
  then glues the tail to the destination wall with the normal router.
  Callers drop their region/fold-width bookkeeping entirely, and the
  tank re-melts around the rooms on every gravity step: memory 44x42 ->
  41x41 (32.4M -> 25.0M), reverse 42x27 -> 31x28 (5.6M -> 2.0M).
- **hook pipes let I/O rooms sit flush**: a room 1 cell from another
  cannot be piped to it *on that axis*, but it can sit FLUSH against it
  and hand over sideways: leave the side wall (first arrowhead pointing
  away from it), bend, and terminate into the neighbour's wall — `>v`
  then `v`, three cells. Memory's I now sits directly on C's north wall
  instead of costing five rows of approach. Two consequences worth
  remembering: (1) the terminal cell is always the neighbour's only free
  approach cell, so the r-op targeting segment is fixed by the DST wall
  cell, not by where the source room drifts to under gravity; (2) the
  same trick on an outgoing pipe saves two columns — an east-wall exit
  spends one column on the start arrowhead and one on the bend, while a
  SE-corner exit drops straight down and spends none.
- **relax, don't tune**: every floorplan constant that the tanks are
  sensitive to should be a gravity movable, not a hand-fitted number.
  Memory's band height is an `'int` movable ('band); l2's `relax-boxes`
  does the same progressively for the melt box. Hand-tuning finds one
  feasible point, relaxation finds the frontier — here the two tanks
  trade band-height against F's column exactly, and BAND x FX >= ~265 is
  the whole floorplan in one inequality (40x40 is its optimum).
- **plateau gravity** (l2 `gravity-optimize` `#:sideways` `#:tolerance`):
  score is max-dim^2, so growing the SHORT side is free and strict
  lexicographic descent cannot cross score-neutral ridges. When no
  neighbour is strictly better, step to the best SIDEWAYS one (same
  max-dim, tick-sum within tolerance, deltas never visited), on a budget
  that resets on strict improvement; return best-ever, not last-accepted.
  Honest result so far: it walks (15 sideways steps on reverse, 4 on
  memory) but has not yet beaten greedy on either — both problems'
  basins turned out to be convex under these movables.
- **arrowheads are two-sided**: a bend's FORWARD cell on a room border
  ends the pipe there (premature terminal), and its BACKWARD cell on a
  border makes it a candidate START for the sim. So a snake hugging a
  wall must turn one cell short of it *if the wall is in front*, and the
  tank's first cell must leave in the direction that puts the source wall
  exactly behind it (a perpendicular first glyph is no start at all, and
  the whole tank parses as stray glyphs). Blank room interiors are not
  in `occ` but must be blocked too, or a tank melts into the room it
  serves. The backward-cell half of this used to be fatal ("pipe cell
  used twice"); it is NOT — see the next entry.

- **candidate arbitration: TIGHT FOLDBACKS ARE LEGAL** (judge-confirmed
  by the lead's example), **and the judge works at TWO LEVELS** — see the
  "level 1 / level 2" note that follows this list, which is the 2026-07-26
  correction from probes f3/f5. The arbitration rule itself is unchanged,
  implemented in `sim.rkt` `find-pipes` and mirrored in
  `tools/layout/engine.rkt`:
  1. every arrowhead with a room border BEHIND it is a CANDIDATE start;
     walk each candidate independently. Failed walks (length 1, dead end,
     backward arrow) are discarded, never fatal — this is the old
     optimal.man lesson, unchanged.
  2. a candidate is INTERIOR if its start cell appears as a non-first
     cell of some OTHER candidate's successful walk, i.e. it is a
     mid-pipe rival rather than a true head. TRUE STARTS are arbitrated
     first, INTERIOR candidates afterwards; within each group, reading
     order (row-major).
  3. arbitration keeps a `claimed` set. A candidate whose own start cell
     is already claimed is not a candidate at all; a walk that would
     traverse any already-claimed cell is DISCARDED exactly like a failed
     walk. Success claims all its cells.
  4. "pipe cell used twice" is now UNREACHABLE (step 3 makes overlap
     impossible) — it survives only as an internal assertion. The real
     arbiter of a broken grid is the unchanged STRAY-GLYPH rule: every
     pipe glyph outside a room must end up claimed by exactly one pipe.
  The lead's grid — one pipe leaving a room's south wall and folding back
  alongside itself into O, cells orthogonally adjacent to other cells of
  the SAME pipe — now parses as one 6-cell pipe (`v>^>vv`) and delivers
  values. `probes/f1-foldback.man` / `f2-foldback-send.man`,
  `tests-foldback.rkt`. It also un-broke `solutions/sort-manual.man`,
  which our own parser had been rejecting outright and which now parses
  and passes 7/7 sort-tests.

- **THE JUDGE WORKS AT TWO LEVELS — f3/f5, 2026-07-26, question CLOSED.**
  Two probes were submitted and both came back definitive:
  - `probes/f3-order-ambiguity.man` (id `b9e47ab2-0695-4efa-8048-ff538826112e`)
    -> loadError **"the output room has more than one incoming pipe —
    connect exactly one at (5, 2)"**.
  - `probes/f5-overlap-normal.man` (id `9ae0ac89-c436-4838-8f17-74d75d28496b`),
    the SAME geometry with a normal room in place of O -> loads clean
    (0/19, as expected with no output room).

  f3 answered a question we did not ask. Neither hypothesis below it was
  right: under true-start priority f3 emits `7`, under reading-order-first
  the head cells report as STRAYS — the judge did neither, it counted TWO
  incoming pipes. So the judge saw the arbitrated-away rival. The model
  that fits f3, f5 AND every graded file we own:

  - **LEVEL 1 — VALIDATION is STRUCTURAL, over every successful candidate
    walk, BEFORE arbitration.** The I/O room rules (direction *and* count)
    are checked against the raw walks that touch an I/O room's walls, so a
    rival walk that never becomes a pipe can still fail the load. This is
    the same lesson as the "I/O rooms: the judge checks the WALLS" section
    below, now extended from direction to count — one rule, two symptoms.
  - **LEVEL 2 — SEMANTICS uses the ARBITRATED pipe set** (rule 1-4 above,
    unchanged). Rivals must NOT become pipes of their own.

  **"Keep every successful walk as a pipe" is REFUTED, and the refutation is
  the important part.** Shipped grids are full of rival walks — the premise
  that they are not is simply false: `solutions/reverse-manual.man` has one
  (the return serpentine's `^` at (9,19), an 11-cell suffix of the true
  21-cell C->F pipe, C's top wall behind it) and `solutions/memory-manual.man`
  has FOUR (145/197/188/176 cells, all suffixes of the 211-cell return tank,
  706 shared cells). Parse them as pipes and each room's `s` splits between a
  pipe and its own suffix while the far end's `r` keeps reading the original —
  measured: reverse-manual (judge **20/20**) and memory-manual (judge
  **24/24**) both emit **nothing at all**, deadlocked. The judge ran both
  correctly, so the judge does not do it. Arbitration stays.
- **the I/O COUNT rule, calibrated** (`check-io-room-pipes!`, second half):
  over the candidate walks, an I/O room may be touched by walks from **at
  most one partner room**. Three qualifications, each forced by a
  grader-ACCEPTED file, not by taste:
  - **AT MOST one, never EXACTLY one.** A pipeless I/O room is legal
    (reference.md fine print) and `triangular.man` (19/19) attaches O's only
    incoming pipe at a CORNER, so "exactly one non-corner incoming" rejects a
    file the judge took. We only raise on "more than one".
  - **CORNER attachments do not count**, exactly as in the direction rule.
    `memory-manual.man` (24/24) has a 145-cell walk starting at O's
    bottom-left CORNER — an outgoing pipe from the OUTPUT room — and a second
    outgoing walk at I's south-west corner beside I's real 188-cell one.
  - **count PARTNER ROOMS, not walks.** f3's two incoming walks come from two
    DIFFERENT rooms and were rejected; f1's two incoming walks into O both
    start on the SAME room's wall (the 6-cell pipe and its 2-cell suffix) and
    f1 is judge-confirmed to LOAD. Counting raw walks would reject f1.
    **This is the one thing still unprobed here**: if f1's "judge-confirmed"
    is not to be trusted, the rule could be the stricter raw-walk count. A
    probe that settles it is f1 itself, or any grid with two same-source
    walks into O.
- **order-dependence: STILL UNSETTLED, and f3 can no longer settle it.**
  Reading-order-first-wins and true-start-priority give the SAME answer on
  every grid we own, provably — in all of them the true head precedes its
  rivals in reading order. Verified as well as proved: every `.man` in the
  repo x four input sets plus all three suites, byte-identical under both.
  They differ only when a mid-pipe bend sits EARLIER in reading order than
  the head of the pipe it belongs to, which is exactly f3 — and f3 now dies
  at LEVEL 1 under both readings, so its judge message discriminates neither.
  **We keep TRUE-START PRIORITY** (it maximizes coverage, and the stray-glyph
  rule is a coverage invariant). Nothing observable rests on the choice
  today; a new discriminating probe would need a wall-backed bend preceding
  its own head **between two NORMAL rooms** (so level 1 stays silent), where
  the two readings differ in which pipe delivers.
- **this unlocks denser tank folds — opportunity, NOT yet taken, and now
  with an I/O CAVEAT**: a serpentine may U-turn against a wall *between two
  NORMAL rooms*. Since f3 the same fold is FATAL when the pipe's destination
  (or source) is an I/O room and the U-turn's backward wall belongs to a
  third room: the rival walk terminates where the real pipe does, so the I/O
  room gets a second partner room and the load fails at level 1. Fold freely
  in tank corridors; keep wall-backed bends out of any pipe touching I or O.
  The layout tool now reports exactly this (`io-room-issues` counts candidate
  walks), and l2's `bend-ok?` still uses the old blanket ban, so no shipped
  build is affected. The measurement below is unchanged for normal rooms: Measured on the layout tool's autorouter, same 2-row
  corridor and bounds: old strict predicate 11 cells max, new 15 (+36%);
  never worse (`expand` runs both predicates and keeps the longer, so
  the relaxation is monotone). The l2 MELT has NOT been redesigned to
  exploit this — `melt-chan!` / `pipe-route` still gate every turn on
  `bend-ok?` (l2.rkt:469, `(not (border? (p- p nd)))`), the old blanket
  ban, so a snake still turns one cell short of a wall. Worth revisiting:
  capacity-210 tanks are what set memory's floorplan, and relaxing
  `bend-ok?` to the reading-order condition changes a melt's shape
  constraint from "3 free rows" to "2 free rows" along any wall.

  shape — stop computing the answer, hand the search the CONSTRAINT.
  - **shape menus** (l2 `build-shape-menu`): L1's `#:max-width` means a CFG
    has a FAMILY of rooms, not one. Sweep the budget, keep the Pareto front
    over (w, h, static ticks), and let the floorplan search index it with an
    ordinary `'int` movable. Aspect and placement are then chosen JOINTLY,
    which they must be: the binding constraint couples them. Ordering the
    menu by ascending width matters — a +-1 index step is then a real aspect
    change, whereas +-1 on the raw budget usually recompiles to the SAME room
    and gravity sees a plateau instead of a gradient. Ticks need a per-shape
    number, so `cfg-layout` gained a static `ticks` estimate (profile-weighted
    lane cells + rail cells, tight circuits counted twice for the round trip);
    it is a shape-comparison number, not a simulation, and that is all the
    Pareto filter needs. Fronts: memory C 36 widths -> 27 distinct -> 8,
    memory F 34 -> 5 -> 4, reverse C 32 -> 23 -> 8. `#:keep` force-retains a
    dominated shape so a shipped solution stays reachable by index.
  - **it does real work**: memory's search moved C from 26x17 to **22x18**
    (the narrowest on the front) and F from 16x5 to **14x6** — 23.35M ->
    20.06M; reverse moved C from 21x14 to **22x14**, one column WIDER because
    width was not binding and 22x14 is the faster shape (est 1249 vs 1273).
    Two of three rooms-with-menus ended up non-default, so compile-then-place
    really was leaving money on the table.
  - **combo lower bound** (`shape-combos`): total occupied cells bound max-dim
    from below (`ceil(sqrt(cells))`, and no smaller than the widest room), so
    a shape combination can be discarded before any routing. Honest yield:
    37.5% of reverse's 32 combos die against a bound of 27, but 0% of
    memory's 36 do — memory's rooms are small next to two 210-cell tanks, so
    the cell count barely moves and the bound is slack. Useful as a filter
    only when the ROOMS dominate the area.
  - **multi-magnitude gravity** (`#:magnitudes`, default 1/2/4/8): unit moves
    cannot cross a valley — a room must travel ten columns before the tank on
    its far side re-melts short enough to pay, and every step between is
    worse. Geometric magnitudes span it in two moves. This is what finally
    beat both hand-tuned floorplans; memory's winning deltas include an
    8-column F move and a 9-column I move that unit steps never reached.
  - **attachment auto-solving** (l2 `attach` / `attach-at`): a channel end
    declares a ROOM plus the l1 channel symbol its pipe ops use (and,
    optionally, which walls are acceptable). L2 searches that room's
    perimeter, choosing all channels of one kind JOINTLY — the sim's rule is
    a nearest-neighbour classification over the whole segment set, so no
    single cell is legal or illegal on its own — and verifies with the SIM'S
    OWN rule (`targeting-ok?`, nearest segment by manhattan, ties by segment
    reading order; segment = LAST pipe cell for incoming, FIRST for
    outgoing). Then it routes, and re-checks the rule against the cells
    ACTUALLY LAID, not the ones planned. Callers' `check-targeting!` is gone
    from both sol files: the predicate became the search's oracle instead of
    a post-hoc assertion.
  - **hooks emerge; nothing draws them**: a room flush against its neighbour
    has NO outward cell on the shared side (the outward cell is the
    neighbour's border, so `free-seg?` rejects it), so the only attachments
    on offer are side exits and the router's own bend is the hook. Reverse's
    I now hooks off its SE corner exactly like memory's, without a line of
    hook-specific code anywhere.
  - **reverse lost its six forwarder dots**: they only ever existed because
    `out` attached to F's EAST WALL, making the split against west-wall `ret`
    one-dimensional. With the solver free to pick F's SOUTH-EAST CORNER the
    split is 2-D (the corner wins on row as well as column) and the padding
    is unnecessary — `idioms.rkt` now offers `ff-blocks/corner`. Six fewer
    cells the man walks per emitted value, worth ~250 ticks/test on its own.
  - **candidate filter = NOTES' own 2-cell clearance rule**: a wall cell is
    only attachable if the cell TWO steps out is free. For a source the start
    arrowhead's direction is fixed, so it cannot turn until then; for a
    destination the terminal is reached either straight from that cell or by
    a bend whose BACKWARD cell is that cell (arrowheads are two-sided), so a
    border there kills both. Without this the solver happily picks an I room
    corner whose only normal points into the room it is trying to reach.
  - **landmines, all found the hard way**:
    (1) `compile-cfg`'s memo key excluded `#:accept?` — a veto that varies
    silently returned a stale layout. It cannot go in the key (callers build
    it fresh every call), so there is now a `#:accept-key` the caller sets to
    a hashable summary. (2) Plain pipes ignored `attach-halo`; only melts
    respected it. Once L2 picks the cells, two attachments land close enough
    that a 2-cell hook eats the only free approach of a tank routed later,
    and the tank reports "no sweep works" — a very indirect way to learn that
    two wall cells were adjacent. (3) Two segments of one room must be >= 2
    apart for the same reason: side by side they share the single cell in
    front of the wall. (4) If a channel's two segments COINCIDE the pipe is
    length 1, which is illegal — and `pipe-route`'s state is (pos, dir), so
    it "solves" it by looping 35 cells all the way back onto its own start
    cell and dying in `commit-pipe!`. Reject coincident segments up front.
    (5) Ranking candidates by distance to the partner room is right for a
    plain pipe and WRONG for a melted tank, whose quality is where its snake
    has room to grow; hence `#:near`, a preference anchor that is a hint, not
    an answer.
  - **backtick literals are validated STATICALLY AT LOAD, per ROW**
    (judge-confirmed): the backticks on a row pair up consecutively and every
    cell between a pair must be a digit or a space, whether or not any man
    walks there. A stray op between two same-row backticks is a LOAD error
    the simulator will happily run. Vertically aligned literals across rows
    are fine, but a COLUMN whose backticks pair over an all-digit/space span
    can read as an unintended vertical literal. l2's `check-literals!` runs
    inside every `assemble`, so a violating layout is infeasible to the
    search rather than a surprise at submission. Hand-built rooms were safe
    by construction; shelf-packed rooms that share a row between chains are
    the risk.
  - **results**: memory 40x32 @ 14591 (23.35M) -> 37x37 @ 14654 (20.06M);
    reverse 27x28 @ 2344 (1.84M) -> 27x26 @ 2089 (1.52M). Both plain builds
    reproduce their saved file byte for byte (optima baked into
    `BASE-DELTAS`), memory still passes the 100-address stress case with
    210/210 ring capacities, and `#:pin?` in memory-sol shows the migration
    path: pin every attachment to the cell the caller used to compute, keep
    the declaration, and the verification still runs.

# Scoreboard

- triangular: **832 (8x8 @ 13), leader tie — optimal.** Sophia found it
  by hand; search8.rkt independently rediscovered the identical layout
  after two fixes. The tricks: crash-ending code (no H) so 12 walked
  cells fit a 2-row interior, and DIAGONALLY INTERLEAVED I/O rooms
  (overlapping rows, different columns) wired with length-2 hook pipes:
  a terminal-bend `>^` off I's corner into main, and `v` `<` corner-
  terminating into O's top-right corner. 832 appears to be the true
  optimum: emission < 13 needs a walk that provably can't fit under
  10-dim, and the 0-special-case fork (X branch subsidizing the average)
  needs 3 interior rows, pushing past 8-dim for a worse total.

# Parser lesson (judge-confirmed via optimal.man)

- An arrowhead adjacent to some room's border is only a CANDIDATE pipe
  start; if the walk from it is invalid (e.g. length 1), the judge
  discards that interpretation rather than failing the load. The same
  glyph can be a valid interior cell of a different pipe.
- The lead's foldback grid extends this: a candidate whose walk SUCCEEDS
  is also discarded when it collides with a pipe already parsed, so a
  pipe may fold back against itself. Full rule under "candidate
  arbitration" in Reusable idioms; regression `tests-foldback.rkt`.
- **But discarded is not invisible.** A successful walk that arbitration
  throws away still counts for I/O ROOM VALIDATION (probe f3): the judge
  checks I and O structurally, over every successful candidate walk, before
  it decides which walks are pipes. Two levels, one parser.

# L1 v2: code melting (room interiors)

- **flows, not strips** (l1 `compile-cfg`): a chain is one routed path whose
  ops sit on its front and whose tail IS its transfer rail. The router is a
  Dijkstra over `(pos, heading, token-index)`: stepping forward may leave the
  cell BLANK (a no-op the man walks over, crossable straight by any other
  flow), place the next token (needs a virgin cell), bend (an arrow — costs a
  cell as well as a tick), stamp a whole tight loop, or FOLLOW an existing
  arrow, which is how a late rail merges onto an earlier one. Lane and rail
  became the same object.
- **rigid seeds are heading-relative**: a `#:tight` circuit is a macro token
  occupying 2 x (L+1) cells laid relative to the current heading — body on the
  cw side, `arrow(-d)` under the branch, `arrow(-cw)` hopping back onto the
  join. It works at any of the four headings, so a bend upstream re-aims a
  whole loop. Same for X/d arms: they leave cw/ccw of the heading AT the
  branch cell, so heading tracking gets branch geometry for free.
- **the greedy sequential placer is the weak link, not the router.** Each flow
  commits cells, so flow k+1 inherits a fragmented board; the failure mode is
  always an ENCLOSED region or a WALLED-IN JOIN, never a bad path. Three fixes
  tried, in increasing order of usefulness: soft halos round a join (useless —
  a foreign flow crossing the reservation makes it unturnable anyway), gutters
  (a protected straight run — better, but its far end is unturnable so the
  corridor is decorative), materialised STEMS (a bus of arrows pointing back
  into the join, so any rail reaching ANY cell of it merges and rides in —
  this is the one that works). Even so the melt only lands ~1 attempt in 5.
  The real fix is rip-up-and-reroute, i.e. conflict-directed backjumping over
  the *ordering*, not restarts.
- **so the shipped engine is the SHELF PACKER**: lanes are still straight, but
  several chains share a row growing in from both ends, tight chains share
  two-row shelves, and rails route in the gap rows as in v1. Deterministic, no
  search failures, and it does most of the work: memory C 22x24 -> 26x17,
  reverse C 27x13 -> 22x14. The melt survives behind `#:melt`.
- **dot padding was load-bearing TWICE**: it positioned r-cells for targeting,
  and — because a dot is a character — it also walled regions off from the
  router. Deleting memory's 30 dots removed 30 cells AND 30 obstacles. But
  keep it where the split is genuinely 2-D: reverse's forwarder attaches `out`
  to F's EAST WALL and still needs six, while memory's attaches to the SE
  CORNER and needs none.
- **`#:col-order` + `#:accept?`**: same-wall channels discriminate by column,
  so L1 takes a west-to-east channel order and either enforces it as a hard
  band per op (`#:strict-bands?`, needed by memory's controller — no
  unconstrained packing satisfies its split) or uses it only to pick which end
  of a shelf a chain packs from. Anything genuinely 2-D goes through
  `#:accept?`, a caller veto over candidate layouts: the caller's targeting
  rule IS the oracle, so give it the veto instead of hoping the smallest room
  happens to be legal. Callers then derive their wall cells from the layout
  (`ring` over the easternmost ring read, `in` over the westernmost input
  read) rather than pinning them.
- **`#:max-width` is a real budget and rooms are L2 movables**: the room is
  routed inside a W x H box and only the width is a budget, so the other
  dimension is minimized under it. Both sol files expose the budgets as
  `deltas` keys (`cw`, `fw`, plus memory's `inmax`), which is exactly
  `gravity-optimize`'s movable format — the floorplan search now sweeps ROOM
  ASPECT alongside room positions. That matters because the two levels are
  coupled: a shorter C does not automatically pay, since memory's tanks need
  `BAND x FX + strip` area and shrinking C shrinks the strip beside it.
- **results**: reverse 31x28 @ 2112 -> 27x28 @ 2344, score 2.03M -> 1.84M
  (kept). Memory's C room shrank 22x24 -> 26x17 and all 7 tests plus the
  100-address stress still pass, but the world did not improve (40x32 @ 14695,
  23.51M vs the 38x40 @ 14649, 23.44M baseline) — the height C gave back went
  straight into band slack the tanks could not use, so memory's v1 solution
  was KEPT. Memoize `compile-cfg`: gravity calls it hundreds of times.

# Y (split): sim-y.rkt, probe kit, fork-search verdict

- **`sim-y.rkt` is sim.rkt + `Y`**, cloned so the live sim.rkt is never
  touched. Regression-clean: memory.man x7 mem-tests, reverse.man x8
  rev-tests and 14 standing programs (identity/record/latecrash/optimal/
  tri/memory-gravity) give byte-identical outputs, status, ticks AND emit
  ticks under both sims. Extras it provides: `y-collision-mode`,
  `y-stats`, `y-max-men`, `y-trace`.
- **Semantics chosen** (see the file header for the full rationale):
  births happen at stage 3 the moment the splitter executes `Y`; the right
  copy takes the splitter's slot, the left copy is appended; newborns
  neither execute nor move on their birth tick; birth-cell occupancy is
  resolved after *all* men have executed, so "two splits, one cell" is one
  uniform rule; dead men are REMOVED (halted men are not); the run ends
  when every remaining man is halted, which is vacuously true once they
  have all died; flush semantics unchanged.
- **The one contradiction with reference.md is not resolved by split.md.**
  reference.md: a man who *touches* another makes both STOP. split.md: men
  who *collide* both DIE. Our default (`'split-md`) splits the difference —
  two movers onto one cell, a swap-through, and a birth onto an occupied
  cell all KILL; a man moving onto a *stationary* man (halted, blocked or
  newborn) makes both STOP. `probes/y3-onto-stationary.man` is the probe
  that decides it: `(1)` means stop, `(1 5)` means die. Until it is run,
  treat this as a guess.
- **`sim.rkt` is NOT a superset of `sim-y.rkt` even on Y-free programs**:
  it makes two men arriving on one cell stop rather than die, and it never
  notices a swap-through at all. Every solution we ship is single-man, so
  nothing observable changes today — but a multi-man solution would.
- **Parity law (derived, useful):** for a man, `phi = (row+col+tick) mod 2`
  is invariant under movement AND across a split (the birth cell is one
  step away and one tick later). Two men can only ever be adjacent — hence
  only ever swap — if their `phi` differ, and the *only* thing that flips
  `phi` is being blocked for a tick. `y4-swap.man` engineers its swap by
  making one man lose a race for the output pipe's source cell.
- **Fork-search subset-sum: NO at n=16**, for three independent reasons.
  (1) *Registers.* `BP` has no read instruction, so a man carries at most
  two readable quantities; every way of getting a number in lands it in
  `A`. Sum + choice-mask + addend is three. Packing sum and mask into one
  64-bit word does not help, because the per-fork addend still has to
  reach `B` through `A`. (2) *Serial input.* Men never leave their room, so
  all 2^n descendants share one set of pipes, and a pipe read consumes the
  value — each of the 2^n men needing a per-level value reintroduces
  Theta(n*2^n) serialized reads. A value can only be *broadcast* by being
  loaded before a split, i.e. at most two values total (or a whole list
  packed into one 64-bit word, which needs n*b <= 64 — fine for toy
  inputs, useless for real ones). `q` is the only non-consuming read and
  it only yields a pipe's occupancy count, into the write-only `BP`.
  (3) *Area.* Colliding men die, so 2^n live men need 2^n distinct cells:
  max-dim >= 2^(n/2) = 256 at n=16 even with a perfect square quadtree
  spread, and the winner cannot convert his position back into a mask
  without a per-leaf literal block, which forces one row per leaf and
  max-dim >= 65536. Score is max-dim^2, so that is 4.3e9 x ticks.
- **The mechanism itself works** and is worth keeping for small fanout:
  `probes/y6-forksum.man` (generated by `probes/gen-forksum.py`) forks
  once per element and selects the matching leaf, `[3,5,7]` target 10 ->
  `2 3 7` at tick 59 in 56x38; verified up to n=5. Sum lives in `B`
  (`` `v` `` `+` `M`), compare is `` `T` `` `N` `+` then `X` as a free
  three-way branch. Known gap: when several subsets match, they ALL emit
  and interleave — arbitration would need a pipe-as-mutex, which is not
  built.
- **Local sim throughput** (`probes/gen-forkbench.py N RUN`): cost is
  dominated by *parsing*, which is O(area) with a cons-keyed hash — about
  1.3 us and 140 bytes per grid cell. 2^13 men / 8.4k ticks = 6.1 s and
  553 MB; 2^14 men / 16.6k ticks = 12.6 s and 1.07 GB. Simulation proper
  runs about 1.3M man-ticks/s. Extrapolated, an n=16 fork grid is ~31M
  cells -> ~4 GB and ~50 s just to load, so the local sim can validate
  fork programs up to about n=14 and not beyond.

# Sort: insertion sort in the ring (29x30 @ 3728 = 3.35M)

- **Reverse's twin at the world level, its opposite inside the room.**
  Same topology (C + the shared forwarder + two melted CAP-16 tanks +
  I/O rooms), same MARK protocol, same never-halting server that blocks
  on exhausted input. But selection sort costs ~n^2 ring passes and
  INSERTION sort costs ~n^2/2, and insertion's pivot lives in B for a
  whole pass — the forwarder's register-invariant trick one level up.
  All 7 public tests pass ('timeout with correct output); 6 rounds of
  n=16 emit at 23.4k ticks, 0.5% of the 5M cap.
- **A SENTINEL in the ring is what buys tight loops.** Ring layout
  `[v1..vc, S, K]`, S = 15000 (above every value, below MARK so the
  forwarder relays it like any other value) and K = c. Both hot loops —
  scan and copy — terminate by comparing against S instead of counting
  BP down, and that is exactly the condition for `#:tight`: a tight body
  must be plain ops ending in `(goto head)`, so a body that has to test
  the backpack is disqualified by construction. Measured: the BP-counted
  first draft paid ~38 ticks per compare (three chains, three rails per
  iteration), the sentinel version pays ~10. K is a SMALL integer, so
  `b` loads it straight into BP for the emit loop (no literal decode),
  which leaves BP free during a pass to hold r, the input still to read.
  Whole-program effect: 5072 -> 3728 average ticks.
- **Scan and copy are the same circuit with a different pivot**: head
  `r W -` (A = pivot - w, B = w), body `+ W s` (recover w, restore the
  pivot in B, send w). Pivot = x scans, pivot = S copies. `+` undoes
  what `-` clobbered and `W` puts the invariant back — the same dance as
  the forwarder's `W - s + M`, two ops shorter. Worth back-porting: an
  `ff` body of `+ W s` is L=4 instead of L=6, 10 ticks/value instead of
  14 (left out of idioms.rkt only because that file was another agent's
  this week).
- **RAILS BETWEEN CHAINS ARE THE TICK BUDGET, not the loops.** In a
  25x16 controller ~150 ticks per input value go on walking between
  chains and only ~10 per iteration inside them. Neither `#:weights` nor
  `#:max-height` touches this: the shelf packer places chains by height
  then width, so profile weights only price rails it has already
  committed to, and only `#:max-width` is a real budget (max-height is
  accepted and ignored). The one lever is the chain PARTITION — which
  transfers are fall-throughs — and l1 constrains that hard: every
  branch's straight arm must be its chain's fall-through, a tight head
  must have a successor, a tight body must be the cw arm, and the entry
  must head a chain. **A mid-chain `goto` whose target is not the next
  block is silently dropped from the flow** (chain-flow only emits the
  tail transfer for the LAST block) — the rail edge still exists, so it
  compiles and then walks into the wrong code. Never write one.
- **One late `r ring` op can cost the whole room.** `#:col-order`
  discriminates by column, so the westernmost `r in` must sit east of
  every `r ring`. A 33-cell chain whose last `r ring` sat at offset 30
  pushed the split to 31 and no layout under 41 wide existed; splitting
  that chain at a transfer that was a `goto` anyway gave 26. Rule of
  thumb: keep the emit spine (the long literals) out of any chain that
  also reads the ring.
- **Profile with a scratch COPY of sim.rkt** — add a per-cell
  visit/blocked counter to stage 3 — and run it with `#:max-ticks` set
  to the emit tick. Otherwise the post-completion blocking (a correct
  server blocks forever) swamps the histogram 50:1 and every cell looks
  like a stall. That is what showed the man was busy, not starved: 356
  of 4148 ticks blocked, and 2400 of them outside the tight loops.
- **What was NOT the bottleneck**, each measured rather than assumed:
  the forwarder (2%), the ring capacity (CAP 24 -> 10 is 3.5%, and
  bigger tanks cost TICKS not area — they melt into space that was free,
  but lengthen the round trip), and C's aspect (cw -4..+12 spans 5%).
- Adversarial shapes worth keeping for any ring sort: ascending input is
  the worst case for the scan (every value appends, so every pass scans
  the whole run), descending is the worst case for the copy, and
  all-equal takes the duplicate arm on every compare. All three land
  within 25% of random input here.

# grading.md, recorded

- Default step cap is **5 million**; a few problems differ and say so on
  the problem page.
- **Rounds gate input on completed output**: round N+1's input is not
  released until all of round N's output has been received. A server
  that never reads ahead is unaffected in OUTPUT, but a local
  continuous-feed sim slightly UNDERESTIMATES judge ticks on multi-round
  tests, since it hands over the next round's `n` earlier than the judge
  will. Rounds that expect no output unlock the next round immediately.
- Private cases "exercise the same behavior as the public cases - no
  hidden tricks"; they exist only to make hardcoding hard. Passing at
  least one private case is what makes a team eligible for points.
- Only the BEST submission per problem counts and submitting can never
  lower a score, so there is no reason to sit on a working solution
  while chasing a better one.

# Consolidation pass: sim merge, forwarder v2, an L1 hard error, re-gravity

- **`Y` is merged into sim.rkt**; sim-y.rkt is now a one-line re-export, so
  there is a single simulator again. The merge was *justified*, not assumed:
  `diff sim.rkt sim-y.rkt` reproduced the saved 5-hunk patch BYTE FOR BYTE,
  which is the proof that sim.rkt had not drifted since the clone and that a
  copy could therefore only introduce the Y hunks. Regression against a saved
  PRE-MERGE copy of sim.rkt: all three shipped solutions x their full suites
  (22 tests) plus 14 standing programs, comparing outputs / status / ticks /
  EMIT TICK — **0 mismatches**. Keep the pre-merge copy; once you overwrite
  sim.rkt, a regression that compares the file against itself proves nothing.

- **reference.md's "touches another little man (both stop)" is DEAD.**
  `probes/y3-onto-stationary.man` walks a man onto a *stationary* (halted /
  blocked) man — the case most favourable to "stop" — and the judge returned
  `1 5`, the DIE outcome. So the kill rule is not merely for two movers: it
  is EVERY man-man contact. `y-collision-mode` now defaults to `'strict-die`;
  `'split-md` (the pre-probe guess: two movers die, arriving on a stationary
  man stops) and `'legacy-stop` survive only for comparison, and the dead
  sentence is annotated in reference.md itself. Under the new default every
  Y probe still reproduces: y1/y2 `(1 2)`, y3 `(1 5)`, y4-swap `(3 5 7)`,
  y5 `(21 21 8 8)`, y6-forksum `(2 3 7)` @ tick 59. Nothing we ship changes
  — every solution is single-man — but the parity law and the fork-search
  area bound now rest on a measured rule instead of a guess.

- **the sim validates backtick literals AT LOAD too.** `run-program` calls
  `check-static-literals!` before parsing: per ROW the backticks pair
  consecutively and every cell between a pair must be a digit or a space,
  else a load error worded like the judge's ("expected a digit or a space
  between backticks"); an odd count on a row is an error too. COLUMN
  alignment is explicitly NOT an error — shipped reverse.man stacks literals
  in the same columns with ops between them and the judge accepts it — but a
  column pair whose span is entirely digits/spaces WARNS
  (`literal-column-warn?`, on by default). Note the deliberate asymmetry with
  l2: `check-literals!` *raises* on that column case. Over-strict in l2 is
  cheap (the search simply never considers such a layout); over-strict in the
  sim would misreport a legal program as broken.

- **forwarder v2: head `r W -`, tight body `+ W s` — 10 ticks/value, was 14.**
  Back-ported from sort's scan/copy circuit with the pivot specialised to
  MARK. The old body `W - s + M` fixed its registers up AFTER the send (`+`
  to rebuild MARK, `M` to reseat it); the new head parks v in B with a `W`
  BEFORE the subtract, so `+` alone rebuilds MARK and one more `W` puts it
  back — two fixup ops collapse into one, and it happens before the send
  instead of after. The MARK arm needs no fixup at all: it is taken exactly
  when v = MARK and the head left B = v. Sign convention, `x` arms, chain and
  tight structure are unchanged, so it is a drop-in swap.
  - Measured on the ROOM, not just on paper: at F's minimum footprint the
    tight circuit goes from 7+7 cells to 5+5, i.e. 14 -> 10 ticks per value,
    with the footprint UNCHANGED at 14x6. The `` `1048576` `` literal is F's
    width floor, so a shorter body buys TICKS, not area — the hoped-for "new
    shape fronts" did not materialise (the F menu is still 4 shapes, same
    dimensions, lower estimates: 14x6 est 1318 -> 1078).
  - End-to-end the payoff is exactly as lopsided as the old profiling said:
    **memory -17.1%** (14653.6 -> 12149.0 average) because F really is
    memory's rate limiter, but only **-0.24% on reverse** and ~-1.4% on sort,
    where NOTES had already measured the forwarder at ~2% of the budget. A
    29% cheaper inner loop is worth almost nothing where it is not the
    bottleneck; memory is the one place it was.
  - **memory kept a PRIVATE COPY of the forwarder** and so silently missed
    the upgrade until it was deduplicated onto `ff-blocks/corner`. Two
    identical five-block definitions in two files is a bug waiting for
    exactly this. There is one definition now, and memory's F is an alias.

- **L1: a mid-chain `goto` to a non-successor is now a COMPILE ERROR.** This
  was the standing landmine — `chain-flow` emits a transfer only for the LAST
  block of a chain, so a mid-chain `(goto L)` whose L is not the very next
  block vanished from the flow while `rail-edges` still built its rail; the
  program compiled and then walked into the following block's ops. The check
  lives in `rail-edges`, which already owns the fall-through map and the
  analogous x/d checks, so BOTH engines (shelf packer and `#:melt`) reject
  it, and the message names the block, its goto target, its actual successor
  and the fix. No false positive on either legal shape (goto its own
  fall-through; goto from a chain tail) and none of the three sol files
  trips it.

- **sort migrated to L2 v2, and the migration initially LOST.** The diff was
  mechanical (menus for `cw`/`fw`, `attach-at` for every channel end, both
  `check-targeting!` calls deleted, `ff-blocks/corner` for F), and the result
  was 33x30 = 3.86M against a 3.36M baseline. Two separate causes, both
  worth remembering:
  - **`#:near` is not optional for a melt whose partner is far away.** With F
    parked west of C's east corridor, the unhinted solver ranked F's south
    wall candidates by distance to C and picked the WEST end; the ring-out
    snake then had to grow east of everything to reach it and the world blew
    out to 40+ columns. Aiming ring-out at F's south-EAST end (and ret at C's
    ring-read columns) put the snake back in the corridor east of C, which is
    the only place it is free anyway: 33 -> 31 wide. Reverse gets away
    without hints only because its F sits over the corridor already.
  - **a room needs all four degrees of freedom, and I gave O two.** Every
    sweep I ran moved O's COLUMN and left its row at the formula's value;
    every feasible floorplan then put O east of the ring-out corridor and
    nothing got below 31 columns. Freeing O's ROW — one more axis, no new
    machinery — let it tuck into the band BESIDE the corridor rather than
    past it, and the world dropped to 30x29 immediately. The failure looked
    like "this floorplan cannot be narrower"; it was "my search could not
    express narrower". Screen on all of a movable's axes before concluding a
    dimension is binding.

- **re-gravity results (shape menus as movables, `#:magnitudes '(1 2 4 8)`,
  forwarder v2). All three improved; all three plain builds reproduce their
  saved .man byte for byte, and every final grid passes both literal checks.**

  | problem | before | after | score |
  |---|---|---|---|
  | memory  | 37x37 @ 14653.6 = 20.06M | 37x37 @ 12149.0 | **16.63M** (-17.1%) |
  | reverse | 27x26 @ 2089.3 = 1.523M  | 27x26 @ 2084.3  | **1.519M** (-0.24%) |
  | sort    | 29x30 @ 3727.6 = 3.355M  | 30x29 @ 3540.7  | **3.187M** (-5.0%) |

  Memory and reverse were already at their optima: gravity re-explored from
  the baked deltas with the rebuilt menus and returned the base point in both
  cases, so their entire gain is the forwarder. Sort's gain is the forwarder
  plus the two search fixes above. Memory still passes the 100-address stress
  (write 0..99 distinct, read all back) with ring capacities 221/218 against
  a requested 210.

- **housekeeping**: l2's `dump-occ!` debug dumps fired unconditionally on
  three error paths that the `#:attach-tries` loop CATCHES and retries, so a
  perfectly successful `build-reverse-grid` printed 58 lines of occupancy map
  to stderr. Gated behind `#:verbose`. Also, the three sol files now export a
  `*-channel-manifest` (name, src/dst room, min length, l1 op symbols) so
  tools/layout can read the channel table from the solutions instead of
  keeping a hand-transcribed copy.
- **tandem turns are legal** (sim-verified, probes/f4-tandem-turn.man):
  two parallel adjacent pipes may bend together — inner bend arrowhead
  directly beside the outer pipe's straight cell, corner terminals and
  all. Never blocked by the parser (no shared cells, no rival starts);
  recorded so nobody "fixes" it away. With self-foldback (candidate
  arbitration entry) this means pipe bundles pack at 1-cell pitch
  through turns, not just straights.

- **compound (cluster / contraction) moves in `gravity-optimize`.** Greedy
  one-movable-at-a-time gravity cannot express a move whose whole VALUE is
  joint. Memory is the worked case: shifting F and O together by (2 . -2)
  builds a 35x35 world, but F-alone and O-alone both stay at max-dim 37 with
  1-2% worse ticks — above any sane sideways tolerance — so every staging move
  is rejected and the search provably parks. `gravity-optimize` now also
  proposes:
  - `#:clusters` — 'pairs (default): every PAIR of 'pos movables plus the
    all-'pos group, translated by one delta over the EIGHT compass directions
    x `#:cluster-magnitudes` (default '(1 2 4)). Diagonals matter here in a way
    they do not for single moves: the offsets that pay ARE diagonal, and
    staging a diagonal through two axis steps re-enters the rejected
    intermediate. A list of key-lists names groups explicitly; 'none disables.
  - `#:positions` — `deltas -> (hash key -> (r . c))`: with it the search also
    proposes a true CONTRACTION, every movable stepping toward the centroid of
    the packing, in three flavours (both axes / rows only / columns only).
  They are generated LAZILY — only once no single move strictly improves,
  which is exactly the parked state they exist for — so a still-descending
  search costs precisely what it did and existing callers are unchanged.

  **Gate (this is the evidence, not a unit test):** memory's baked deltas with
  the F/O (2 . -2) shift SUBTRACTED, same movables, same budget:
  singles-only parked at (37, 12496) for its whole run; with cluster moves the
  compound neighbour fired on ROUND 0 (37 -> 35) and kept descending, ending
  at 35x35 / 7-7 PASS / avg 12123.6 / **14.85M vs the shipped 15.33M**. The
  gain is now baked into memory-sol's BASE-DELTAS. Two cells of max-dim is
  5.3% of memory's score each; no router change was involved at any point.

- **three L2 mechanism bugs, all found by the fluid-packing investigation and
  all cheap:**
  - **melt glue ignored attach halos.** `melt-chan!`'s `finish` routed the
    tank's tail with `pipe-route` but without `#:chan`, so a tank's own glue
    could take the only free approach cell of ANOTHER channel's wall; the
    second melt then died with "no sweep works", which names the victim rather
    than the culprit. Now passed `#:chan name` — but SOFTLY, falling back to
    the unconstrained route, because the halo is a heuristic reservation and
    previously-feasible builds legitimately cross halo cells the other channel
    never needs.
  - **attachment ranking anchored at room CENTRES.** `end-anchor` returned the
    partner room's box centre, and the ranking is "distance from this
    candidate wall cell to the anchor" — so pressed-together rooms rank each
    other's FAR corners best (I's south-west corner wins because C's centre is
    south-west of it) and `#:attach-tries` then permutes the wrong group. The
    symptom is "cannot route channel in" with the feasible cell two columns
    away. The right anchor is the point of the partner's box NEAREST this room
    (our centre clamped into their box).
    **It went in as a FALLBACK, and the two rejected forms are the interesting
    part.** Making it the PRIMARY ranking stops memory's 210-cell `ret` tank
    melting at all ("cannot melt tank ret: no sweep works") — the shipped
    35x35 world is balanced on the centre-anchored ordering. Demoting it to a
    TIE-BREAK (ties in centre distance are the common case: a whole wall is
    usually equidistant from a box centre, and they used to be broken by raw
    scan order) still cost reverse 0.02% — 1,519,783 vs 1,519,418 — because
    the tie-break is exactly where reverse's grid was decided. Since the bug's
    symptom is INFEASIBILITY rather than a slightly worse world, `assemble`
    now re-resolves with the near anchor only after every centre-ranked
    assignment has FAILED. Builds that succeed today never reach it and are
    bit-for-bit unchanged. General lesson, third time it has bitten this
    project: a ranking heuristic that shipped solutions were tuned against is
    load-bearing, and "obviously better" changes to it must be additive.
  - **overlapping room boxes were silent.** `add-room!` writes into `occ`, a
    hash, so a second room simply overwrote the first: the world assembled,
    `check-literals!` passed, and the failure surfaced in the SIM PARSER as a
    "stray pipe glyph" somewhere else entirely (the merged wall stops being a
    closed border rectangle). `add-room!` now rejects box overlap by name.
    FLUSH boxes — adjacent walls, no shared cell — stay legal; that is what
    every hook floorplan uses.

- **sort's floorplan, not its search, was the last 13%.** The v2 migration had
  already landed (menus, attach-at, corner forwarder); what remained was three
  DECLARATIONS. (1) ring-out was pinned to C's `'(e)` wall by inherited dogma —
  C has exactly one outgoing channel, so targeting is satisfied wherever the
  segment lands, and the restriction bought a dead 2-3 column gutter; allowing
  `'(n e)` lets the snake grow into the band the world is already paying for.
  (2) F was seeded at the band's north-west corner, which is on top of the only
  corridor `ret` has; seeding it EAST of the input hook gives ret the west
  gutter and ring-out the middle, and the two melts stop competing. (3) O was
  seeded under F rather than beside it, so the ring-out tank had to go PAST it
  instead of AROUND it. Result: 30x29 @ 3540.7 = 3.19M -> **27x28 @ 3533.7 =
  2,770,432 (-13.1%)**, beating the hand-verified 27x28 demo (2.83M) as well,
  and the plain build reproduces `solutions/sort.man` again. (The last 784 of
  that came from a cluster-move gravity pass over the new floorplan — `O
  (1 . -1)`, `cshape -1` — which is what the compound moves are for once the
  declarations stop being the binding constraint.)
  The band could not close from 29 to 28 rows until I moved eight columns east:
  at `band -4` I's box and F's box COLLIDE, which is precisely the overlap the
  third bug fix above now reports by name instead of assembling a world the
  sim's parser later rejects. The fix paid for itself inside one afternoon.

# Brackets: the stack IS a register, and a two-room pipeline (27x25 @ 617.4 = 450k)

- **Topology: `I -> D -> C -> O`, one incoming and one outgoing pipe per
  room.** No ring, no forwarder, no MARK, no tanks — and therefore no
  `#:col-order`, no `#:accept?` veto, no `#:near` hints: with a single
  pipe per direction, `s`/`r` targeting is trivially correct and `attach-at`
  only has to find walls the router can reach. It is the first solution here
  that is a PIPELINE rather than a server-with-memory, and it is much smaller
  than the ring family (sort 30x29, reverse 27x26) despite doing more
  arithmetic. Reach for this shape whenever the state fits in registers:
  the ring exists to hold state, not to move values.
- **Why two rooms, precisely.** Per character the machine needs the STACK,
  a COUNTDOWN, and the character (plus scratch for every binary op). `r`
  always lands in A and every arithmetic op clobbers B, so at most one value
  survives a character, and BP cannot be read back. Three into two does not
  go. Splitting across two men gives each exactly one persistent value:
  D keeps the countdown in BP and uses A/B as pure scratch to classify;
  C keeps the stack in B and never touches BP during the scan. Control flow
  in a second room is the cheap third register.
- **BIJECTIVE BASE 3 for a bracket stack — and base 4 is a TRAP.** S = 0 is
  empty, push t in {1,2,3} is `S := 3S + t`, and because there is no zero
  digit a nonempty stack is never 0, so the empty test is a bare `X`.
  - push, with the code in A and S in B, is `+ + + M`: three adds and NO
    constant, because B already holds S. Four cells, tight-loop body.
  - pop-and-typecheck is ONE divide: `+` gives S - t, then `/ 3` leaves the
    popped stack in A and (S - t) mod 3 in B, which is 0 exactly when the
    top was t. `/` putting the remainder in B is what makes this one op.
  - **the trap**: 2-bits-per-level (push 4S+t, top S&3, pop S>>2) fills all
    64 bits at the spec's maximum depth 32, so a depth-32 stack whose
    OUTERMOST bracket is `[` or `{` has bit 63 set and is NEGATIVE. `}` is
    an arithmetic shift, so each pop sign-fills, the value drifts by -2^62,
    -2^60, ... and an emptied stack reads as **-1, not 0** — a balanced
    string reported as unclosed. `&3` genuinely is wrap-safe (the drift is
    always a multiple of 4); the EMPTY test is not, and that is the test
    that decides the answer. Base 3 tops out at (3^33-3)/2 = 2.8e15 at depth
    32 and needs no wraparound argument at all. Measured on the shipped
    grid: correct through depth **39**, wrong from 40 — 7 levels of margin
    over the spec, where base 4 would have failed AT the spec maximum.
- **A 1-based POSITION with no position counter.** Nothing can count up in
  the backpack (`b` writes it from A, `m` only decrements), and the answer
  is the index p of the first offending character. So don't track p: load
  BP = n once for the round, never decrement it during the scan, and on a
  failure DRAIN the rest of the round — which the room has to do anyway, or
  the producer blocks — decrementing BP once per drained code. After n - p
  drops **BP = p exactly**. Then `+ m` while BP > 0 (a two-cell tight body)
  counts it into A. Seeding that same loop with A = 1 instead of A = 0 and
  running it on an undecremented BP = n yields n+1, so the "unclosed
  openers" answer reuses the identical circuit. Generally: a value you only
  need ONCE, at the end, can live in the backpack; converting it costs its
  own magnitude in ticks, so keep the magnitude small (<= 64 here).
- **Classification with two divides and no literals.** With e = c - 1,
  `t = e >> 5` names the family and `e mod 4 == 0` means closer; `/` keeps
  both halves, so `e / 4` yields u = e/4 beside the closer test and `u / 8`
  then yields t. The -1 is load-bearing and unique among small offsets:
  openers and closers only separate mod 4 after it, and c+3 (the other
  candidate mod 4) breaks on `{` because 96/32 = 3 collides. Consequence
  worth noting: the whole program contains **no backtick literal at all**
  (every constant is a single digit 0,1,3,4,8), so both literal checkers are
  vacuous and D's width is set by its chains, not by a constant.
- **Codes chosen so the consumer needs no compare**: D sends +t for an
  opener, -t for a closer, 0 for end-of-round, so C's entire dispatch is one
  `X` (zero / cw / ccw) and the push arm is its tight body. Designing the
  MESSAGE around the receiver's branch instruction is worth more than any
  optimization inside either room.
- **l1 shape landmine, repeatable**: threading a branch's zero arm onto its
  own chain because "it is the fall-through anyway" made one 17-token lane
  and D compiled to 21x6; splitting it with an EMPTY stub block (the stub is
  the fall-through, and gotos the real arm) gave 15x9. One stub cell bought
  six columns. Chain length is lane length, and lane length is width.
- **Never-halting servers cost `tests x max-ticks`, always.** The sim runs
  to the cap even though scoring stops at the emit tick, so a gravity `check`
  with `#:max-ticks 60000` on a 4k-tick program spends 93% of its time
  simulating a blocked man. Capping just above the worst observed emit
  (9000 here) made the gravity sweep ~7x faster; a build is 3-28ms and a
  9-test score 63ms, so the CAP, not the router, was the search's bottleneck.

# I/O rooms: the judge checks the WALLS, not the pipe list (2026-07-26)

Found by submitting `solutions/reverse-manual.man` (hand-drawn in the layout
tool, 26x26, strictly better-dimensioned than the built `reverse.man` 27x26).
The judge refused it at LOAD:

    Your program failed to load: a pipe flows out of the output room —
    the output room's pipe must flow into it at (21, 7)

- **Judge coordinates are (col, row).** (21, 7) is the O room's top-left
  corner at row 7, col 21; the cell it is really complaining about is the `<`
  at row 8, col 20, hard against O's west wall. Every other diagnostic we
  have from the judge is worth re-reading with x-then-y in mind.
- **The offending cell belonged to a pipe between two OTHER rooms.** It is
  the up-then-left bend of the C->F return serpentine, mid-pipe, correctly
  claimed by our parser and by the tool. So the rule is NOT "no pipe is
  sourced at O" as our parse sees it — the judge tests O's walls directly,
  and any arrow leaning away from an output-room wall counts as outflow no
  matter whose pipe it belongs to.
- **The predicate, calibrated against every grader-ACCEPTED file we own**
  (implemented as `check-io-room-pipes!` in sim.rkt, called at the end of
  `find-pipes`, and mirrored leniently as `io-room-issues` in
  `tools/layout/engine.rkt` so the layout tool flags it live):

      for each NON-CORNER wall cell w of an I/O room, let o = the cell just
      outside w.  If o is an arrowhead and
        * o points AWAY from the room and a legal pipe walk starts at o
          (>= 2 cells, terminating at a foreign room's border)
              -> OUTPUT room: "a pipe flows out of the output room"
        * o points INTO the room (i.e. at w)
              -> INPUT room:  "a pipe flows into the input room"

- **"Must point INTO the room" is WRONG** — the naive reading of the message.
  Pipes running flush PARALLEL along an O wall are legal and shipped:
  `reverse.man` (12,25)-(12,26), `memory.man` (14,32), `triangular.man` (4,3)
  all do it and all were accepted 20/20, 24/24, 19/19. Only *away* is fatal.
- **Both qualifications are forced by accepted programs, neither is taste:**
  * NON-CORNER — `memory-manual.man` (24/24, our best Memory) has a `<` at
    (13,29) against O's bottom-left CORNER whose outward walk is a good
    145-cell pipe. A cornerless rule rejects a program the judge took.
  * WALK VALIDITY — `triangular.man` (19/19, leader tie) has a `^` at (4,4)
    against O's top wall, non-corner, pointing away; its walk is 1 cell (it
    is the terminal arrowhead of the I->A hook), so it is not a pipe. This is
    the optimal.man candidate lesson again, now on the I/O side.
- **~~A second reading fits the same evidence~~ — REFUTED by f3, 2026-07-26.**
  We suspected the judge might simply use plain READING-ORDER pipe
  arbitration, under which reverse-manual's `<` at (8,20) beats the true head
  at (9,11), parses as a pipe sourced at O, and trips an ordinary direction
  check. `probes/f3-order-ambiguity.man` kills that: under reading-order
  arbitration f3's head cells would have been STRAYS, and the judge instead
  answered "more than one incoming pipe". **So this rule stands alone, and it
  is not about arbitration at all** — the judge validates I/O rooms
  STRUCTURALLY, one level below the pipe list, against every successful
  candidate walk. See "THE JUDGE WORKS AT TWO LEVELS" in Reusable idioms.
- **The same structural check also enforces a COUNT** (added to
  `check-io-room-pipes!` / `io-room-issues` 2026-07-26): over the candidate
  walks, at most one PARTNER ROOM may touch an I/O room, corner attachments
  exempt. f3 is the calibration; `probes/f5-overlap-normal.man` shows the
  count is I/O-only (the identical geometry between normal rooms loads).
  Our sim now reproduces both judge verdicts verbatim, including the
  pre-fix reverse-manual geometry -> "a pipe flows out of the output room —
  the output room's pipe must flow into it at (21, 7)" (regression in
  `tests-foldback.rkt`, which reconstructs it from the ISSUE.txt diff).
- **Input side: implemented, but vacuous — asymmetry unprobed.** No file we
  own has any pipe pointing into an input room, so the mirror ("a pipe flows
  into the input room") is regression-free but also unconfirmed; the strict
  mirror the wording suggests (adjacent cells must point AWAY from I) is
  definitely wrong — `memory.man`, `sort.man` and `memory-manual.man` all run
  parallel pipes along an input wall and were accepted. Also unprobed: the
  reference says the input room has EXACTLY ONE outgoing pipe, yet
  memory-manual has two away-pointing arrowheads at I's south wall (one at a
  corner, one non-corner whose walk is a 188-cell pipe) and the judge took
  it — so "second pipe" is evidently counted the same wall-based way, or not
  at all. Resolved 2026-07-26: memory-manual's extra I-outgoing walk starts at
  a CORNER, and corners are exempt from the count, so the file has exactly one
  counted outgoing walk. **PROBE SUGGESTION** (still open): a grid whose only
  oddity is an arrow pointing into I's non-corner wall, plus one with two
  genuine NON-CORNER outgoing I pipes to two different rooms — the input-side
  mirror of f3.

## Reverse: 26x26 hand layout is the new best (2,147,111)

- The fix ISSUE.txt prescribed is two characters wide: shift the serpentine's
  up-to-left turn one column left (`>v^-----< |O|` / `>v^------^ +-+`), which
  also shortens the return channel by 2 cells. All 8 rev-tests still pass;
  local avg emit 2074.25 (was 2084.25 on reverse.man).
- Judge: **20/20, 26x26, avgTicks 3176.2, score 2,147,111** vs reverse.man's
  20/20, 27x26, 3197, 2,330,613 — **7.9% better, and it is now the submitted
  best for Reverse** (id 3b2defc1-8607-441e-a7ca-e113ef73b276).
- `solutions/reverse.man` STAYS as the build-reproducible artifact
  (`build-reverse-grid` still reproduces it byte-identically, verified);
  `reverse-manual.man` is hand-made and reproduces from nothing. Keep both.
- **Geometry insight for the automated floorplan**: the whole 7.9% is one
  column. The hand layout beats l2 by tucking the 3x3 I and O rooms into the
  SAME horizontal band between the two big rooms (row 7-9), so neither I/O
  room adds to the width, and by letting the return serpentine thread the gap
  between them. l2's placement never considers "I/O rooms share a band";
  making max-dim (not area) the objective and allowing I/O rooms to be packed
  into an existing corridor is the target that would let gravity find this.
- Local ticks underestimate the judge by a stable **x1.53** on both Reverse
  programs (2084.25 -> 3197, 2074.25 -> 3176.2) and on Sort (3533.71 ->
  5418.48). The *ratio between two programs on one problem* survives intact
  (local 0.9952 vs judge 0.9935 for manual/built reverse), so local scoring
  ranks correctly even where it mis-levels.

## Resubmission round, 2026-07-26

| file | cases | dims | judge avgTicks | judge score | note |
|---|---|---|---|---|---|
| reverse-manual.man | 20/20 | 26x26 | 3176.20 | 2,147,111 | **new Reverse best** |
| memory.man | 24/24 | 35x35 | 70950.33 | 86,914,158 | unchanged from its earlier submission; memory-manual (33x33, 76,426,791) still the Memory best |
| sort.man | 25/25 | 27x28 | 5418.48 | 4,248,088 | tiny improvement on the previous 5421.68 / 4,250,597 |

- Memory is the one place local ticks are *not* off by 1.53x but by **5.85x**
  (local avg emit 12123.57 over our 7 public tests -> judge 70950.33 over 24
  cases). Memory is single-round, so this is not the withheld-input effect:
  the judge's case set is simply much heavier than the published one. Treat
  local Memory tick counts as a ranking signal only, never as a score
  estimate — the same caution now applies wherever casesTotal >> our suite.

## tcp (Packet Reassembly): the ring server that does NOT use the MARK protocol

`problems/tcp.rkt` (spec + all 6 public cases + load assertion + stress
material), `problems/tcp-sol.rkt`, `solutions/tcp.man` — **31x32 @ 4271.8
local = 4.37M**, 6/6 public, 8/8 stress, 400 fuzz cases against the spec, 0
failures. Not submitted (no tcp problem id yet).

- **A direct C->O pipe beats the forwarder when a register invariant is at
  stake.** Every previous solution routes output through the ring behind a
  MARK because that keeps the controller single-outgoing. Here the drain loop
  must hold `waiting` in B across every emission, and the MARK protocol needs B
  for the marker (`M` / MARK-lit / `W`) — the two are incompatible. Giving C a
  SECOND outgoing pipe straight to O makes an emit one op (`s out`) that
  touches neither hand. F degenerates to a bare BOUNCER (`r tank` / `s ret`,
  a 5x2 room) which exists only because a pipe may not return to its source
  room. Side benefit: the scored final emission does not have to travel a lap
  of the ring first. Cost: C has FOUR pipes, and that cost is real (below).
- **Don't store what is provably empty.** The window is 16 seqs, but slot 0
  (seq = `waiting`) is empty by definition — the instant it fills it drains —
  so the ring holds only the 15 SUCCESSOR slots. That is what makes a window
  slide exactly one pop plus one push, so the drain path needs no realignment
  at all and an in-order stream costs ~35 ticks a packet. The 16-slot version
  needs the freshly-emptied cells to land where the alignment marker is, which
  they cannot (pushes go behind it), and the fix is a 15-cell fixup rotation
  per packet. Look for the always-empty cell before building the buffer.
- **A TIGHT BODY CANNOT BE RAIL-ENTERED**, so a two-way loop test whose "keep
  going" class spans two `X` arms is impossible: `(x rdone rc rc)` fails with
  "rc is not rail-entered". Ring cells here are EMPTY(0) / value(+) /
  sentinel — the realign wants {EMPTY, value} -> body, and X splits them. The
  fix generalises: make the SENTINEL CARRY THE STATE the register was holding
  (here it is `-(waiting+1)`), which frees B for the whole path; the test
  becomes `(r ring) + b` with a `d` branch (`y+1 > 0` for every ordinary cell,
  `<= 0` only for the sentinel), a genuine two-way branch whose cw arm is the
  tight body, and `rdone` reads `waiting` back out of the sentinel with `N M`.
  A sentinel that is only a marker is a wasted 64-bit word.
- **`b` + `]`*k + `d` is a free magnitude test.** `d >= 16` is `b ] ] ] ]`
  then a `d` branch — no literal, no compare constant, and A still holds d.
  Any "is |x| >= 2^k" question can be asked this way when both hands are busy.
- **BACKTICK LITERALS ARE DIRECTION-UNSAFE IN L1.** l1 lays a chain along
  whatever heading the router picks and shelf chains genuinely run westward
  (they pack in from both ends of a row), and nothing reverses a literal run:
  a westward `` `15` `` loads 51. Single digits are direction-free, so build
  small constants arithmetically (`3 M 5 *` for 15). The shipped MARK-lit
  rooms are safe only because their chains happen to run east — that is luck,
  not a guarantee, and it is worth an l1 fix (reverse the digit run when the
  chain's heading is west, or refuse to place a literal on a westward lane).
- **Four pipes on one room is where l1's targeting model runs out.** l1 can
  only discriminate by COLUMN BANDS, and `splits-for` uses ONE split fraction
  for every group, so two groups mean one physical split column: west =
  {`r ring`, `s ring`}, east = {`r in`, `s out`}. Consequences, all learned
  the hard way:
  - a chain holding ops from both sides is placeable only if the split falls
    exactly between them (`fits?` requires `col+woff <= wlimit` and
    `col+eoff >= elimit`), so with several such chains NO split works and
    `compile-cfg` fails at every width. The error is only ever "no feasible
    layout"; `#:verbose 'trace` and its "shelf X (w=.. woff=.. eoff=..) does
    not fit" lines are the only diagnosis.
  - the fix is to make every chain ONE-SIDED, cutting at transfers that are
    gotos anyway and introducing EMPTY BLOCKS purely as chain cut points
    (`ok0`-style). Chain partition is a compile-time knob, not just a width
    knob.
  - and to make each block's own ops monotone in column. `r1e` pushes val and
    THEN pops the stale EMPTY: push-then-pop and pop-then-push leave a queue
    identical (they touch opposite ends), and only one of the two orders is
    layable. Look for order-independent op pairs when a block straddles a band.
  - net effect on shape: 6 coarse chains -> 43x9 (unlayable world), 12
    one-sided chains -> 25x25. More chains buys width and costs height and
    rails; C's box wants to be SQUARE because the world is C plus a band on
    one axis and an I/O strip on the other.
- **Attach the pipes where the OPS actually are.** The bands put ring ops
  upper-west and I/O ops lower-east, i.e. the room's targeting geometry is
  DIAGONAL even though the constraint that produced it was a column split. The
  floorplan that follows — ring band above C's north-west, I and O in a strip
  east of C's lower rows — is worth 34x31 -> 31x32 over putting both strips
  below. Splitting the two strips across the two axes is the general move when
  the controller is roughly square.
- **Where the remaining ticks are**: ~377 ticks per deposit packet = 15 ring
  cells (rotate d-1 tight at ~10, realign 15-d tight at ~12) plus ~8 rail
  transfers between the now-numerous chains. The ring's CAPACITY is NOT a
  lever: cap 6 through 20 give byte-identical worlds and identical ticks here,
  because the man is always slower than the pipe shift and the tanks melt into
  space that was free anyway. Gravity (multi-magnitude + `#:clusters 'pairs`,
  movables cshape/band/two attach anchors/three origins) found exactly one
  improvement, `I (0 . -1)`; the basin is flat because the band is at its floor
  (F's box is 4 rows) and every narrower C on the menu is taller by as much.
- **Fuzz the VALID streams separately.** A uniformly random permutation of
  0..n-1 trips the `-1` rule within a few packets almost every time, so a
  "200-case fuzz" can exercise nothing but the loss path. `tcp-random-valid-
  stream` picks each arrival from the seqs inside the current window, which is
  the generator that actually tests the buffering. Both are in tcp.rkt.

# L4: the problem harness (harness/), and what it could NOT absorb

The recurring cost was never the CFG — it was ~120 lines of floorplan
boilerplate per problem, copy-pasted and then diverged. `harness/templates.rkt`
owns it: `define-ring-server` and `define-pipeline` take a declaration and
derive the deltas merge-and-bake, both shape menus, the band floorplan, the I
seeding, the `in-col`/`ring-col` derivation and its west-of assertion, the
room list, the channels, the tools/layout manifest and the gravity movables.

- **Migration gate: byte-identity, and it holds.** reverse and sort onto
  `define-ring-server`, brackets onto `define-pipeline`, all three producing
  grids IDENTICAL to what the hand-written files produced (diffed against
  dumps taken before the migration, not just against the saved `.man`). That
  equality is the whole proof that the template derives what the hand-written
  file did rather than something merely similar. All four problems still
  verify green at their published numbers: memory 35x35 @ 12123.6, reverse
  27x26 @ 2084.25, sort 27x28 @ 3533.71, brackets 27x25 @ 617.44.

- **`solutions/reverse.man` and `sort.man` carry a TRAILING NEWLINE the
  builders do not emit; `brackets.man` does not.** So the naive
  `(equal? grid (file->string f))` reports DIFFERS on two of four shipped
  solutions and always has — it is a file-hygiene artifact, not geometry.
  Half an hour went into confirming that before touching anything, which is
  the right order but worth not repeating: the honest predicate compares
  modulo one final newline, and `driver verify` implements exactly that and
  says which case it hit. Anything else is a real difference.

- **What the template deliberately does NOT synthesize**, because this is
  where the three ring servers genuinely disagree and each has a scar above:
  the `#:accept?` vetoes (c-ok?/f-ok?, memory's IN-MAX bound), the `#:near`
  tank separation hints (load-bearing for sort, absent for reverse), the F and
  O seeds, the band formula, and the channel ORDER (memory melts `ret` first
  because it can only sweep the band; reverse and sort melt `ring-out` first
  because its only corridor is the gap east of C). A template that guessed
  here would be re-deriving a hand-tuned floorplan from nothing.

- **MEMORY IS NOT MIGRATED, and the reasons are structural rather than
  cosmetic.** `build-memory-grid` carries two parameters no other builder has:
  `#:capacity` (the tank size is a caller argument, not a constant) and
  `#:pin?`, which threads `#:fixed` cells derived from the layout — including
  a computed `f-ret-row` — through every attachment as the documented
  pre-L2-v2 migration path. Expressing either in the template means adding a
  parameter with exactly one user, which is how a template becomes a second
  copy of the thing it replaced. Memory stays hand-written and is wrapped by
  the registry instead; it loses nothing (it is `verify`/`stress`/`score`/
  `submit`-able like the rest) and its movables list is spelled out in
  `harness/problems.rkt` rather than derived. If a third problem ever wants a
  capacity argument, revisit.

- **Fragments are a library, not a framework.** `harness/fragments.rkt` has
  the counted loop, the read-n-then-loop, the sentinel scan and drain, the
  MARK emit (ring and direct), the counter-in-the-ring rotate and the
  countdown-to-A, each returning block lists with its register contract in the
  comment. Two things learned writing them down: a `d` head IS tightenable
  (the rule constrains the BODY — plain ops ending in `goto head` — not the
  head), and a fragment's suggested `chains` is only a suggestion, because the
  chain PARTITION is the room's real tick budget and only the caller knows
  which transfers are worth making fall-throughs.

- **Two stress generators were wrong, and the failures looked identical to
  solution bugs.** (1) brackets: nesting 63 deep violates the spec's
  `depth <= 32`, and the shipped base-3 stack is correct only through depth 39
  — so the generator manufactured a red against an input the judge will never
  send. (2) memory: the 100-address case needs ~311k ticks against a 200k
  verify cap, and a capped never-halting server returns a correct PREFIX,
  which reads exactly like a wrong answer. Hence `stress-ticks` as a separate,
  larger per-problem cap, and a driver that says "ran to the N-tick cap"
  instead of leaving you to find it. **A stress case outside the spec box is
  worse than no stress case.**

- **The operational lessons are compiled into the driver, not documented at
  it.** Tick caps are measured rather than guessed (`optimize` runs the suite
  once and caps just above the worst observed emit); `verify` and `stress`
  take a LIST of problems so a full sweep is one process and pays the ~70s
  menu sweep once per problem instead of once per invocation; `submit` is a
  DRY RUN by default that prints the exact `jq -Rs | curl` it would send, and
  refuses outright when no problem id is registered (brackets and tcp have
  none — SUBMIT.txt records ids for Triangle, Memory, Reverse and Sort only,
  and a guessed problemId spends a submission against the wrong test set).

- **`parse-command-line` stops flag parsing at the first positional**, so
  `optimize brackets --rounds 1` silently ran the default 12 rounds. Found by
  reading the round counter in the output, not by any error. The driver
  hand-rolls its argument scan so flags work anywhere on the line.

# L3 "littlelang": register allocation as shortest-path search (l3/)

`l3/compile.rkt` compiles a small language with named variables and
structured control down to L1's `(values blocks chains tight)`. Nothing below
L3 changed. `l3/DESIGN.md` is the language and the pipeline; `l3/RESULTS.md`
is the measured comparison; `l3/demo-brackets.rkt` and `l3/demo-reverse.rkt`
are the two validations.

- **The result that matters: the generated forwarder is `ff-blocks/corner`,
  block for block** — `fprologue (lit M)`, `loop (r tank) W -`,
  `mark (r tank)(s out)`, tight body `+ W (s ret)`, `dead H`; 5 blocks, 18
  ops, 3 chains, 1 tight, same as the hand file. So is reverse's `rhead`:
  `(r in) M 1 W - (s ring) + b`, including the `+` that recovers `n` from the
  leftover `1` in B. Neither was special-cased. Both are shortest paths.

- **Allocation here is not colouring, it is SHORTEST PATH over abstract
  register states.** There is no mov-anywhere in this ISA and a binop can only
  read its second operand from B, so "put x in r" is not an instruction — it
  is a synthesis problem. Represent every value as a LINEAR TERM
  `k + sum c_i*atom_i` (exactly the closure of `+ - N` and `*`-by-constant;
  `/ % & | ~ { }` mint a fresh opaque atom), let the room's state be the pair
  of terms in A and B, and make code generation a sequence of STATE GOALS
  ("A must hold t, B must still hold u, and this `r` must happen once, in
  order") discharged by a bounded Dijkstra over `{M W N + - * digit-loads}`.
  One mechanism, no idiom table, and it reproduces `M k W /`, `W -`, `+ W`,
  `+ + +` (base-3 push, no constant 3 anywhere) and `W + M 3 W /`.

- **Let the side-effecting READ into the search space.** With `(r in)` as an
  obligation the search must discharge, the goal "A = c-1" from an empty state
  costs 4 ops (`1 M (r in) -`: stage the constant into B BEFORE the read)
  instead of the obvious 5 (`(r in) M 1 W -`). That is the hand solution's
  sequence, and it is only reachable if scheduling the read is part of the
  search rather than fixed before it.

- **Two branch refinements are worth more than they look.**
  (1) `X` takes the straight arm exactly when A = 0, so on that arm A is a
  known constant AND the tested term is a live EQUATION: solve `T = 0` for an
  atom with a unit coefficient and substitute it away. That is how the MARK
  arm learns for free that the value it just read IS the marker and B still
  holds the compare constant — without it, that arm needs a fixup the hand
  code does not have.
  (2) Preserving the B-resident across a leaf `send` is a PREFERENCE taken
  when it costs at most one extra op. Greedy per-statement it is cheaper to do
  `W (s ret)` and fix up after; with the preference the search finds
  `+ W (s ret)`, which is the shipped body and one op shorter overall.

- **Jump threading must run BEFORE tight classification.** Structured
  lowering mints a join block after every branch, so a loop body reaches its
  head through an empty `(goto head)` and does not literally end in
  `(goto head)` — the `#:tight` precondition fails and the hot loop silently
  compiles cold. Threading the empty joins out is what makes brackets' push
  loop tight.

- **LANDMINE, cost me an hour: l1 does not check `#:entry`.** If the entry
  label names no block, `compile-cfg` places no `@` and returns a room with no
  little man in it; the sim then reports `status = done` with empty output,
  which reads exactly like a logic bug. Jump threading had deleted the empty
  prologue block that the caller had named. l3 now carries the caller's entry
  NAME onto whatever block became the entry. Worth an assertion in l1.

- **The chain PARTITION is the tick budget, confirmed from both directions.**
  l3 emits reverse C with 12 blocks / 50 ops / 2 tight — identical counts to
  the hand version — but FIVE chains where the hand has six (`passc` and the
  rotate head end up in one lane), and that alone is **-11.8% ticks**
  (1837.9 vs 2084.2 avg, 8/8 pass). In the other direction brackets C is +4
  blocks and 4 rows taller and pays +4.3%. Same knob, both signs, chosen by a
  greedy heuristic on both sides. It belongs in the L2 search as a movable,
  next to room aspect.

- **Chain-length budget must count a tight circuit as `2 x (L+1)`, not as one
  block.** Counting ops only, reverse's emit chain merged a 5-cell rigid
  circuit with a 14-token literal spine into one 19-wide lane and no room
  under 28 columns existed; costing the circuit properly puts the budget over
  the edge and a stub appears exactly where the hand file has `emitgo`. Same
  mechanism as brackets' `dcz` — one stub cell buys six columns — now
  automatic.

- **Channel bands have to constrain the CHAIN, not the block.** With a
  `#:col-order`, two banded channels in one lane make the column split
  unsatisfiable at ANY width ("one late `r ring` op costs the whole room").
  l3 takes `#:band-channels '((r ring in))` and refuses to merge such chains;
  the refusal materialises as reverse's `fillgo`.

- **`materialize-const` prefers digits, then digit arithmetic, then a
  literal — and warns when the literal is not a palindrome.** l1 seeds
  non-entry chains at any of four headings, so a westward chain reads
  `` `1048576` `` as 6758401. Shipped reverse gets away with it; a generated
  CFG has no such luck. l3's demo uses **MARK = 1111111**, palindromic and
  direction-safe, satisfying the same two conditions (above every value,
  equal to none). If you ever hand-place a wide literal, check the heading.

- **The infeasibility diagnostic reproduces brackets' own header.** Write the
  one-room version — stack in B, classify the character in the same room —
  and the compiler says: `want A = c-1, B = 4; have A = c, B = s.1`, "a value
  that must survive is in neither hand and the backpack cannot be read back",
  then proposes the ring spill, the ROOM SPLIT (naming brackets-sol as the
  worked example) or the backpack-and-count-out. Auto-splitting is v2;
  diagnosing beats silently failing, and the diagnostic arrives before any
  layout work has been done.

- **Validation, honest numbers** (full public suites, judge-exact sim, each
  world given its OWN shape menus and its own `gravity-optimize` run):

  | problem | shipped | littlelang | ticks | score |
  |---|---|---|---|---|
  | brackets | 27x25 @ 617.4 = 450k | 25x29 @ 644.2 = 542k | **+4.3%** | +20.4% |
  | reverse | 27x26 @ 2084.2 = 1.52M | 30x30 @ **1837.9** = 1.65M | **-11.8%** | +8.9% |

  Both 9/9 and 8/8. All the remaining gap is AREA, and the reason is worth
  recording on its own: **the shipped files' baked deltas are not merely
  suboptimal against generated rooms, they are INFEASIBLE** — l2 rejects them
  with overlapping boxes, because the band formula and the room seeds were
  hand-derived for the hand-written rooms' dimensions. Gravity re-finds a
  floorplan (reverse 42 -> 30 in two rounds) but cannot re-derive the
  floorplan's STRUCTURE. Same lesson as "sort's floorplan, not its search, was
  the last 13%".

# The 'bump tank former, and what EXHAUSTIVE sweeps say about the floorplans (2026-07-26)

Candidate work: `autoroute.rkt` + l2's `bump-chan!` are in the tree, but every
default is unchanged — `current-tank-former` is `'melt`, and all five builds
still reproduce `solutions/*.man` byte for byte. Deltas below are candidates,
not bakes.

- **`autoroute.rkt` is now the ONE autorouter, shared by the layout tool and
  l2.** The tool's `route-pipe` was the only place that knew how to grow a pipe
  by EDGE BUMPS (replace edge `u->w` with `u, u+q, w+q, w`: +2 cells, endpoints
  unmoved, still one self-avoiding walk). It is now a module both callers use —
  `autoroute-bfs` (BFS over `(cell, entry-dir, START)`; the start cell rides in
  the state because the rival-start hazard depends on reading order),
  `autoroute-expand` (runs the relaxed AND strict predicates, keeps the longer
  path, so the relaxation is monotone) and `make-bump-ok?`. Everything
  world-shaped is a closure the caller passes in. `tools/layout/test-roundtrip`
  is 53/53 before and after.
- **The melt and the bump are opposite orders, and that is the whole
  difference.** The melt grows a boustrophedon snake from the source and then
  glues its tail to the destination: a strip sweep is monotone, so pockets
  behind rooms are unreachable, and `bend-ok?`'s blanket ban makes it turn one
  cell short of every wall (3 free rows to fold). The bump former routes a
  SHORTEST legal pipe to the destination first and then fattens it in place, so
  there is no glue to fail on, the tank is exactly `cap` cells, and it folds
  back against its own body — legal since the candidate-arbitration entry.
- **The relaxation is NOT blanket, and the f3 two-level model is exactly why.**
  A wall-backed arrowhead X spawns a rival walk that follows the rest of our
  pipe to our terminal, i.e. a walk from the room behind X into our destination.
  So `bump-chan!` forbids a wall-backed arrowhead when (a) the pipe terminates
  in an I/O room — that rival would be a SECOND partner room touching I/O,
  which is f3's loadError — or (b) the wall behind it belongs to an I/O room
  (the "pipe flows out of the output room" rule and its input mirror), and
  otherwise allows it only when it does not precede its own head in reading
  order, which keeps the grid correct under BOTH arbitration orders (that
  question is still open). The sim is the oracle: every candidate below was
  parsed and run by it, so a violation would have surfaced as a load error.
- **memory 34x34 — the fluid proposal's target, reached.** `'bump` on both
  210-cell tanks plus gravity: **34x34, 7/7 public PASS, avg 11901.1 = 13.76M
  against the shipped 35x35 @ 12123.6 = 14.85M, -7.4%**. Deltas on top of
  BASE-DELTAS: `F (1 . -1)`, `I (-1 . 14)`, `O (-4 . 0)`. The 100-address
  stress passes (emit 310844 vs the melt's 311270), and so does the literal
  lint. At the CURRENT floorplan the same former is a LOSS (36x36) — memory's
  floorplan was tuned around the melt's shape, so the former only pays when the
  rooms are allowed to move with it. Do not evaluate a former at a floorplan
  fitted to a different one.
- **Everywhere else the bump former is a rounding error, as the floor analysis
  predicted**: reverse 27x26 @ 2082.3 (was 2084.3, -0.1%), sort 27x28 @ 3525.7
  with `ret` bumped and `ring-out` melted (-0.23%), tcp identical ticks (8 fewer
  pipe cells), brackets unaffected (no capacity channels). Memory is the one
  problem where tanks are 55% of the committed cells.
- **LANDMINE: first-fit bumping starves the next channel.** The greedy scan is
  order-sensitive, and the first legal form of memory's `ret` fills the band so
  that `ring-out` cannot form at all ("no sweep works" — the melt's own error,
  reported against the victim rather than the culprit). The fix is the melt's
  own lesson: generate a FAMILY (each free start cell x strict/relaxed seeding
  x both sideways preferences) and keep the most compact by bounding box. Same
  ranking rule, same reason.
- **LANDMINE: a bumped tank has NO capacity margin.** The melt gave memory
  221/218 cells against a requested 210 (tank + glue); the bump gives exactly
  210, because it stops at min-len. Every capacity-sensitive stress case has to
  be re-run for a bumped build — and at a REAL cap: memory's 100-address case
  emits at ~311k, above `harness/problems.rkt`'s 200000 verify cap, so a
  stress run at that cap reports FAIL for melt and bump alike. That is a cap
  artifact, not a capacity failure.
- **EXHAUSTIVE combo sweeps: two problems are already at their optimum, and
  that is worth knowing.** `lab.rkt combos` enumerates the whole menu product,
  identifies a combo by the multiset of ROOM BOXES read back off the grid, and
  runs a bounded gravity inside each on `(max-dim, non-space cells)` — no
  simulation, because the area term is what a shape swap moves.
  - **sort: 15 combos, no combo beats the shipped one** (27x28 @ 3533.7 =
    2.77M). **brackets: 6 combos, same verdict** (27x25 @ 617.4 = 450k; the
    runner-up 26x27 @ 621.9 = 453k is worse). Both were re-confirmed with the
    I/O insertion pass below. The hill-climb over shape indices was not missing
    anything on these two.
  - **The rescue scan is what makes it exhaustive.** Most combos do not build
    at the baked placement — a taller C simply collides with the band — so each
    menu point gets a scan of band relaxations and small I/O nudges before it is
    called infeasible. Reverse reached 6 combos without it and **30** with it.
    An "exhaustive" sweep over the combos that happen to fit one floorplan is
    not exhaustive at all.
  - **The lower bound must prune on STRICTLY greater floors.** Score is
    max-dim^2 x ticks, so a combo whose floor only TIES the best max-dim can
    still win on ticks — a `>=` prune skipped brackets' own shipped combo and
    reported a worse world as the winner.
- **I/O POCKET INSERTION: implemented, exhaustive, and it does NOT pay on these
  floorplans.** Hold the man rooms and shapes fixed, sweep each 3x3 I/O room
  over a +-8 window (289 positions) with a full re-melt/re-route at every point
  — a pocket only exists relative to tanks that have re-formed around the room —
  two coordinate passes plus a joint refinement over the best 6 of each. sort:
  73-79 feasible positions per room, no improvement (md 28 either way).
  brackets: 115-192 feasible, no improvement (md 27). The human 33x33 memory and
  26x26 reverse layouts really do tuck I/O into a band, but on the BUILT
  floorplans that band position is already what the seeds and gravity produce;
  what the hand layouts have and the builder does not is a different tank
  SHAPE, which is the former's job, not the placement's. Negative result,
  recorded so it is not re-run on a hunch.
- **reverse CAN be built at 26x26, and it is a LOSS — which is what the hand
  layout is really worth.** The combo sweep reaches max-dim 26 from C's
  narrowest Pareto shape (21x14, `cshape` index 0) with `F (0 . -1)`: 26x26,
  8/8 PASS, avg **2329.5 = 1.575M against the shipped 27x26 @ 2084.3 =
  1.519M**. The area term drops 7.3% and the tick term rises 11.8%, because
  index 0 is the SLOW end of C's front (est 1273 vs 1249). So
  `reverse-manual.man`'s 26x26 is not "the builder cannot find 26" — it is that
  the hand layout gets 26 while keeping a FAST C, by tucking I and O into the
  band between the big rooms. The I/O insertion pass says the builder cannot
  reach that from this floorplan: at the shipped point I has only **7 feasible
  positions** in a 19x19 window (it is flush against C by construction) and O
  has 171, and none of the 342 improves on md 27. What is missing is a
  floorplan STRUCTURE where the I/O rooms are inside the band, not a better
  search over the structure we have — same conclusion the fluid proposal
  reached from the other end.

# History Lesson: footprint-only compression pipeline (83x84 = 7056, sim-exact)

`problems/history.rkt` (2810-byte spec + assertions vs icfp-history.txt and
the published byte list), `problems/history-gen.rkt` (compressor + emitter),
`solutions/history.man` (plain build reproduces it byte for byte).  NOT
submitted.  Emit tick 2,333,509 of the 5M cap; no input, single case, so
local ticks should be judge-exact (the 1.53x factor on reverse/sort came
from withheld input, which cannot apply here).

- **Footprint scoring inverts every habit: ticks are FREE (to the cap) and
  data has a MASS.**  A backtick literal stores ~2.87 bits/cell (19 digits +
  2 ticks + one `s` per 63-bit word); that is the whole density budget.  The
  aim of "beat 60x60" was never reachable: gzip -9 on this text is 12.6k
  bits = ~4400 data cells alone.  Measured ladder (content cells before
  rooms/walls): raw base-123 6930; order-0 Huffman 4987 (+~600 decoder,
  rejected); 3-level mixed-radix escape + dict 5354 (rejected, see below);
  uniform (beta,T) escape + 29-token dict 5087 -> shipped.
- **The winning encoding is rank-escape, not Huffman.**  Symbols (chars +
  packed dictionary tokens + EOT) are frequency-ranked; rank < T costs one
  base-(beta+1) digit, else two ((23,20) optimal here; ~5.0 bits/symbol vs
  Huffman's 4.87).  Huffman's ~2% coding win costs a ~600-cell canonical
  compare chain; the escape decoder is ~150 cells.  At 2.87 bits/cell,
  decoder CELLS are worth ~3 bits each — always price the decoder in cells
  against the data it saves.
- **Tokens are free on the decoder side if the ring maps rank -> PACKED
  VALUE.**  Ring entries are 64-bit words: a char is a 1-char packed string,
  a token is <=9 chars base 123.  One divmod-123 unpack-emit loop decodes
  both; there is no token branch anywhere.  EOT = the rank that lands the
  skip-j lookup on the ring's 0 sentinel -> X 0-arm -> H.
- **Registers, not layout, dictate the architecture.**  Extract-digit +
  escape-test + index needs three live values; two readable registers force
  either a parking pipe ("cubby") or a PIPELINE.  The pipeline won, hard:
  D1 -> D2 -> C0 (word->digit splitter; needs a UNIFORM digit base, which
  is why mixed radix lost) -> CD (rank->ring lookup->unpack) -> O.  Every
  room has <=2 in/<=2 out pipes; C0/D2/D1 have 1/1 and need no targeting
  care at all.  The mixed-radix single-room version died in an unroutable
  s/r-targeting web after ~10 layout iterations; the pipeline's worst room
  has six op-cells to place against four segments, margins >= 4.
- **A serpentine data room is a data bus**: rows of `word`s cells walked
  boustrophedon; westbound rows are just the logical row REVERSED (literals
  read in walk direction), the per-row tail word is packed to a DIGIT
  BUDGET so rows fill exactly, and both-direction 64-bit validity is
  checked per word (reversed-digit overflow does occur in practice).
- **Chained serpentine rooms turn dead strip area into data.**  D-content
  does not fit one rectangle beside the decoder strip without waste; D2
  forwards D1's n1 words (one `count` literal + r/s/m/d circuit) and then
  walks its own rows, so the strip's leftover width holds the stream tail.
  Same trick cascades the ring image: C0 forwards the first K words unsplit
  before it starts splitting, so CD can load its ring from the same stream.
- **X's 0-arm goes STRAIGHT, so X is a lousy 2-way brancher** when 0 is a
  live case (compare-to-limit hits it on the boundary).  Clean 2-way tests
  here: `b` + `m`*T + `d`/`a` (backpack countdown, T<=21 or the chain
  outgrows the room), and quotient-vs-0 via X where 0 genuinely terminates.
  `a` (ccw) vs `d` (cw) chooses which side the branch leaves — that choice
  saved a whole crossing row in CD.
- **Ring capacity is pipe CELLS, and detours are storage.**  The rank table
  circulates in a foldback snake (adjacent runs at 1-row pitch — legal per
  the candidate-arbitration rules) sized >= K+2; when the snake area
  narrowed to 14 cols the missing capacity was bought by routing F1's exit
  pipe on a deliberate loop south of F1.  A pipe's length is a tank knob.
- **P2 (restoring ring rotation after each lookup) is 70-80% of all ticks**
  (~2.3M of the cap; fine here, fatal anywhere ticks are scored).  Encoder-
  side relative addressing would kill P2 but destroys the rank-frequency
  correlation the short codes need — rejected after measuring.
- ~~Residual judge risks, all believed low: the sim's vertical-literal
  column WARNINGS fire on stacked serpentine words (judge validates
  literals per ROW...)~~ — **REFUTED by submission the same day**: the
  judge validates COLUMNS too.  See the correction section at the end of
  this file and probes/literal-probes.md.

# The LM-75 display: sim.rkt, the harness, and what is still open (2026-07-26)

Display support landed across sim.rkt, tools/layout, harness/ and a probe
kit, ahead of the display-judged problems.  Nothing is submitted: no display
problem has been published to us, so there is no id and `submit` refuses.

## What the spec says, and where it stops

reference.md's "The LM-75 Display" is the primary source; textbook.md adds
the tutorial framing and grading.md adds the assignment rules.  Implemented
exactly:

- A display is a rectangle with `+` corners, `=` horizontal walls and `:`
  vertical walls, interior at most 64x64 (66x66 with walls).
- Pipes attach BY SIDE: **top = ADDR, left = DATA, bottom = SWAP**.  A pipe
  on the RIGHT, on a CORNER, or a second pipe on one side is a LOAD ERROR.
- Per tick the display processes ADDR, then DATA, then SWAP, taking **at
  most one value from the arrival end of each** ("can read a value from all
  3 of its pipes in the same tick").
- ADDR `row*width+col` moves the cursor; negative or out of bounds is a
  program error.  DATA 0..15 paints NEXT at the cursor and advances (next
  col, else next row at col 0, else wrap to 0,0); out of range is an error.
  SWAP 0 copies NEXT->CURRENT, clears NEXT, homes the cursor; SWAP 1 copies
  and preserves both; anything else is an error.  Buffers start black,
  cursor at (0,0).
- grading.md: display problems are judged by a **streaming frame compare**
  (one frame per SWAP), scored by the tick of the **final matching frame**,
  require **exactly one display at the stated resolution**, and make
  emitting any output an error.

## The design calls, and the reasoning behind each

- **STAGE 3.**  reference.md's tick order lists "Execution: every little man
  executes the instruction under him. Displays consume and process input."
  in one breath, so displays consume in stage 3 — after the stage-1 shift
  and stage-2 I/O.  Within stage 3 we run men first, displays after, and
  **that sub-order is unobservable**, which is why fixing it arbitrarily is
  safe: the only ops that could see a display pipe are `r`/`R`/`U`/`q`, and
  all four resolve over pipes whose DST is the acting man's own room — a
  pipe into a display has the display as its dst, so no man can read or
  count one.  `s` writes cell 0 while the display reads cell n-1 (n >= 2),
  and the shift between them is next tick's stage 1.
- **Displays are rooms to the PIPE GRAMMAR and to nothing else.**  They live
  in the same `rooms` list, so `border-room` makes their walls foreign-room
  borders: a legal pipe terminal AND legal backing for a candidate start,
  with no change to `find-pipes`.  They are excluded from man placement, and
  their kind ('display) keeps them out of `out-pipe?` / `in-pipe?` /
  `sorted-pipes`.
- **[Dd1] A pipe flowing OUT of a display is a load error.**  The spec never
  says what one would mean and nothing can drive it; the I/O rooms get
  exactly this treatment.
- **[Dd2] A display error aborts the rest of that tick's display
  processing** ("errors end your whole program on the spot"), so a bad ADDR
  is not followed by that tick's DATA and SWAP.
- **[Dd3] A man inside a display is a LOAD ERROR.**  Spec silent.  A display
  is a device, not a room: no instruction semantics, a pixel grid for an
  interior.  Failing loudly beats inventing behaviour — the alternatives
  (ignore him / let him bad-op) both let a typo run.
- **[Dd4] The post-halt flush covers displays.**  reference.md's flush rule
  names the output pipe; a display-judged program has none, and a SWAP in
  flight when the last man halts plainly ought to land, so the drain loop
  also runs while any pipe into a display holds a value.  **Probe d6 exists
  to settle this** — if it is wrong, `H` stops being free on display
  problems and every solution must keep a man alive past its last frame.
- **Side/corner/duplicate rules are validated at LEVEL 1** (every successful
  candidate walk, rivals included), the way probe f3 showed the judge
  validates I/O rooms, and duplicates are counted by DISTINCT PARTNER ROOM
  for the same reason probe f1 forced there.  Corner and right-side
  attachments are flat errors — reference.md names them with no
  qualification and, unlike the I/O corner rule, no grader-accepted program
  forces an exemption.  UNPROBED: `display-validation-level` switches to
  `'pipes` if the judge turns out to be laxer.

## The delivery channel (why `sim-result` did not change)

`sim-result` is positional and destructured all over the tree, so display
results arrive the `y-stats` way — parameters holding boxes that
`run-program` fills:

- `(sim-frame-log)` — list of `(cons tick frame)`, one per SWAP; a frame is a
  vector of rows of colour ints, snapshotted from CURRENT just after the
  copy.  `frame->rows` / `rows->frame` / `frames-match?` convert and compare
  either spelling.  `(sim-frame-limit)` (default 4096) stops the log growing
  without stopping the count.
- `(sim-displays)` — per-display geometry, attached roles, final cursor and
  buffers; set at LOAD and again at run end, so a run that dies mid-way
  still leaves the geometry for the layout tool.
- `(sim-error-reason)` — `'man`, `'display-addr`, `'display-data`,
  `'display-swap` or `'display-output`.
- `(display-judged?)` / `(display-resolution)` — the ASSIGNMENT's rules,
  off by default: exactly one display of the stated size at load, and
  emitting output becomes a program error.

Zero existing callers changed.  **Regression: 222 runs (every .man in the
tree x 6 input sets) through the pre-display sim and the new one produced
identical outputs / ticks / emit / status / dims — 0 mismatches.**  harness
verify 5/5 green, tests-foldback / tests-ringsmoke / tool-roundtrip green.
(Memory's dims moved 36x36 -> 35x35 between two verify runs; that was a
stale-bytecode rebuild of another agent's builder, not the sim — the saved
memory.man is 35 wide and the repro check is byte-identical either way.)

## Harness shape

A display problem is an ordinary registry row plus an entry in
`display-problems` (harness/problems.rkt) giving its resolution.  Separate
table rather than a sixth struct field on purpose: the struct is positional
and constructed in every row, so growing it is exactly the edit that
collides with another agent adding a row.  A name in that table makes
`run-suite` compare frame sequences instead of output lists, score by
`final-match-tick`, and run the sim with `display-judged?` on.  The table is
empty until a display problem exists.

## Open questions, in the order they will cost us

1. **Does the frame include the DATA written on the same tick?** (probe d1)
   If not, every drawing loop needs a spare tick before each SWAP — 4096
   wasted ticks on a 64x64 problem.
2. **Does an empty SWAP commit a frame?** (probe d4)  We say yes, which
   means a stray SWAP desynchronises the whole streaming compare.
3. **Does a SWAP in flight survive the last halt?** (probe d6, [Dd4])
4. **May a display-judged program contain an unused output room?** (probe
   d5)  Our builders emit one by default; if not, they need a no-O mode.
   Only answerable on a real display problem.
5. **What does the judge call a display error, and does a frame that
   matched before it still count** the way a correct emission before a wall
   error does (the latecrash lesson)?  (probe d7)
6. **Do corner / right-side attachments really refuse at level 1?** (d8/d8b)
7. **Round gating.**  grading.md says frames gate rounds exactly like
   output.  Our sim models withheld input for NEITHER — it feeds the input
   pipe whenever the source cell is free — so a display problem is no worse
   off than a normal one here, but neither is modelled.

Probe kit: `probes/d*.man` + `probes/display-probes.md` (predictions per
interpretation, y-probes style), regenerated by
`racket probes/gen-display-probes.rkt`.  All ten are EDITOR probes: the
observable is the screen widget, not the output box.

Battery: `tests-display.rkt`, 53 checks — pixels, cursor advance and wrap,
ADDR addressing, both SWAP modes, all six error paths, the three-pipes-one-
tick case with the ADDR-before-DATA ordering made observable, every load
rule, the assignment hooks, the frame-log shape, the post-halt flush, and
the harness's streaming compare end to end.  Its bench assembles grids from
three driver programs and derives the arrival tick arithmetically (a value
sent from interior offset k arrives on tick k+2 through a 2-cell pipe),
which is what lets a test assert "these three arrive together" instead of
hoping.  One trap worth remembering: every driver must end in `H`, because
a man who walks into his own wall raises a program error and an error ends
the WHOLE run — an unpadded driver silently kills the test before the other
drivers' values have arrived, and the failure looks like a display bug.

# Maintenance pass: the memory bake "mystery", an l1 #:entry error, literal headings, per-case stress caps, tcp on the template (2026-07-26)

## The "34 vs 36" memory discrepancy: there was no discrepancy

The report was that building memory with the OFFSET deltas `F (1 . -1)`,
`I (-1 . 14)`, `O (-4 . 0)` merged onto BASE-DELTAS gives the 34x34 world,
while REPLACING BASE-DELTAS with the numeric sums and adding
`#:tank-former 'bump` to the assemble call gives 36x36 — which reads like a
second consumer of BASE-DELTAS or an asymmetry in the merge.  **Neither
exists, and it is worth writing down why, because the shape of the confusion
recurs every time a former or a delta set gets baked.**

- **The merge is provably equal to replacement.**  `build-memory-grid` folds
  `#:deltas` onto BASE-DELTAS key by key — pairs add componentwise, ints add —
  so "pass offset d onto base b" and "replace the base with b+d and pass
  nothing" are the same hash.  Verified as well as argued: both routes build
  34x34, and the offsets route reproduces the saved grid byte for byte.
- **`grep -rn BASE-DELTAS` finds one consumer per sol file** and no shared one.
  The menu-index clamping suspicion is innocent too: `menu-ref` does clamp, but
  memory's `cshape`/`fshape` are 0 in every configuration in the report.
- **`#:tank-former` and `current-tank-former` are the same switch.**  l2's
  keyword DEFAULTS to the parameter and `assemble` is the only reader in the
  tree (l2.rkt:525), so parameterizing around the builder and passing the
  keyword inside it are interchangeable.  Measured over
  `'bump`/`'bump-only` x `#:attach-tries` 1/2/3: all 34x34.
- **So where does 36x36 come from?  From the FLOORPLAN, not the merge.**
  `'bump` at the plain melt BASE-DELTAS — the gravity offsets NOT applied —
  builds exactly 36x36.  That is the number NOTES already records one section
  up ("At the CURRENT floorplan the same former is a LOSS (36x36)"), and it is
  what any edit that fails to move the deltas produces: a typo'd key, a dropped
  `'band -1`, a replacement hash summed against a stale value.
- **And one of the reported sums WAS stale.**  The quoted `I (-2 . 5)` is off
  by one column: the live base is `I (-1 . -10)`, so the sum is `(-2 . 4)`.
  `(-1 . -9)` appears in memory-sol's own comment as the value the cluster-move
  run REPLACED — summing against the comment instead of the code is the whole
  error.  Both `(-2 . 4)` and `(-2 . 5)` build 34x34, but only `(-2 . 4)`
  reproduces the saved grid, so a wrong sum fails the REPRO check and not the
  dimensions.  That is exactly what the repro check is for; dimensions are not
  a fingerprint.

**GENERAL RULE, now enforced in memory-sol: THE FORMER IS PART OF THE BAKE.**
A former is not a global default you flip while measuring — it is a property of
the shipped world, in the same class as the deltas, and evaluating it at a
floorplan fitted to a different former measures nothing.  `build-memory-grid`
now takes `#:tank-former`, defaulting to memory's own `'bump`, instead of
reading `current-tank-former`; l2's `'melt` default therefore keeps meaning
"every OTHER build is byte-identical under it", which is the only reason that
default is safe.  **Consequence for any measurement rig: `parameterize`-ing
`current-tank-former` no longer changes memory's build — pass `#:tank-former`
to the builder.**

## memory consolidated: solutions/memory.man IS the 34x34 world

`memory-bump.man` is now `solutions/memory.man`, a plain `(build-memory-grid)`
reproduces it byte for byte, and BASE-DELTAS holds the summed optimum
(`band -1`, `I (-2 . 4)`, `O (-5 . -1)`, `F (-5 . -3)`).  **34x34 @ 11901.1 =
13.76M against the melt's 35x35 @ 12123.6 = 14.85M, -7.4%**; 7/7 public, the
100-address stress passes at emit 310844 (the melt's was 311270), literal lint
clean.  The old melt world is KEPT as `solutions/memory-melt.man` — it is the
file the judge graded 24/24 at 35x35 / 86,914,158 — and rebuilds from

    (build-memory-grid #:tank-former 'melt
                       #:deltas (hash 'F '(-1 . 1) 'I '(1 . -14) 'O '(4 . 0)))

## l1 now REFUSES an unresolved #:entry

The standing landmine from the L3 section ("l1 does not check `#:entry`", an
hour) is closed.  If the entry label heads no chain, the shelf packer's
`entry?` is false everywhere, no `@` is written, and the sim reports
`status = done` with EMPTY OUTPUT — indistinguishable from a logic bug in the
CFG.  The melt engine already raised here; the SHIPPED engine did not.  The
check now lives in `make-ctx`, so both engines get it, and the message
separates "the block does not exist" from "it exists but is not first in its
chain" and lists the chain heads — because the way you actually reach this is a
pass (jump threading, dead-block elimination) deleting or merging the block the
caller named, and the fix is to carry the entry NAME onto whatever block became
the entry.

## Backtick literals: the rule is now structural, and a TIGHT BODY can never hold one

`nobend` already stopped an arrow landing between two backticks.  Nothing
checked the HEADING, and there are TWO distinct failures there, not one:

- a WESTWARD run reverses the digits (`15` loads as 51 — the tcp entry);
- a VERTICAL run puts the two backticks in one COLUMN, so each of their rows
  carries an ODD number of backticks and the judge rejects the program at LOAD.
  This one kills palindromes and single digits too, so "use a palindrome" was
  never the whole rule.

What the engines actually do — the part that had never been written down:

- the SHELF PACKER (the shipped engine) writes every lane west-to-east from
  `col0` and stamps a tight HEAD eastward, so plain chains and tight heads are
  safe there BY CONSTRUCTION, not by luck as the tcp entry guessed;
- but a tight BODY is written back along the lane (`(- L 1 i)`) in BOTH
  engines, so the man walks it in the opposite direction and **no placement
  makes a literal in a tight body correct**.  `chain-flow` now rejects it
  outright, and rejects an odd backtick count on either lane of the circuit (a
  literal straddling head and body is split across two rows);
- the MELT engine may seed a chain at any of four headings, so `route-flow` now
  refuses to place a literal cell unless the heading is EAST, and refuses to
  stamp a tight circuit whose head carries a literal unless its seed is east.

Every shipped build is byte-identical across this change, which is the point:
the constraint only removes candidates the shelf packer never generated.  The
convention is documented in l1's header.  (`harness/templates.rkt`'s landmine
(1) is now half stale — "nothing checks this" is no longer true, though its
advice still is.)

## Stress caps are PER CASE, and a stress FAIL now says WHY

- **One cap per problem is wrong in both directions.**  memory's four cases
  emit at 311k, 24k, 7.3k and 2.2k.  Set the cap at the cheap ones and the
  100-address case reports FAIL as a pure cap artifact; set it at the expensive
  one and the three cheap cases each simulate a blocked man for the remaining
  1.5M ticks — which is where a stress sweep's wall time goes, since a correct
  server never halts.  `harness/problems.rkt` grew `stress-case-ticks`, a side
  table (like `display-problems`, and for the same anti-collision reason:
  `problem` is positional and constructed in every row) mapping a problem to
  per-case caps by the exact string its generator produces, plus a LOAD-TIME
  assertion that every named case exists — rename a case and the file says so
  instead of silently reverting that case to the default.
- **"failed and timed out" is not the same as "hit the cap".**  The old message
  fired on any timeout failure, but a never-halting server ALWAYS ends at
  'timeout, including when its output is simply wrong.  The driver now tests
  whether the output is a strict PREFIX of the expected one: only a
  correct-so-far run is a cap artifact ("ran to the N-tick cap with a correct
  k/m prefix"); anything else is labelled WRONG OUTPUT and reports the INDEX of
  the first difference instead of dumping two 100-value lists.  No larger cap
  fixes the second kind, and the message now says so.
- Caps are measured rather than inherited: worst stress emits are memory
  310844, sort 25814, tcp 17649, reverse 9030, brackets 4034.  tcp's row cap
  came down 800000 -> 150000 on that evidence (8 cases x 800k was 6.4M ticks of
  blocked man).
- **tcp's stress cases existed and were never registered.**  `problems/tcp.rkt`
  has had eight of them (in-order, the block-reversed worst case for the
  deposit rotation, both -1 paths, the window extremes) since it was written,
  and the registry row passed `(λ () '())` — so `stress tcp` printed "no stress
  generators registered" and that read as "tcp has none".  Wired up: 8/8.

## tcp migrated onto define-ring-server, and the combo point is baked

`problems/tcp-sol.rkt` is now a declaration on `define-ring-server`'s
`#:out-src 'C` variant: the CFG, the two vetoes and the bouncer, then walls,
`#:near` anchors, three seeds and a band formula.  The bouncer goes in through
`#:forwarder (list blocks chains tight entry)`, which is what that escape hatch
was for.  The gate is byte-identity and it holds.

- **What the migration gave up, deliberately**: the hand builder re-asserted
  `(< ring-ocol out-ocol)` on the SEND columns as well as the reads.  The
  template asserts only the read split — but `c-ok?` is the menu's `#:accept?`
  veto and checks BOTH splits on every shape that reaches the Pareto front, so
  nothing can get past it that the assertion would have caught.  It was a
  second copy of the oracle, which is what L2 v2 deleted everywhere else.  The
  `#:capacity` keyword went the same way (nothing ever passed one, and caps
  6..20 were already measured byte-identical here).
- **The baked point is the combo point**: `cshape 1`, `rec 4`, `O (-10 . 0)` on
  top of the old base — **31x32 @ 4271.8 = 4.374M -> 32x32 @ 4195.2 = 4.296M
  (-1.8%)**, 6/6 public, 8/8 stress.  Note what moved: max-dim did NOT change
  (32 either way); the whole gain is TICKS.  That is precisely the case a `>=`
  prune on the area floor throws away, which the combo-sweep section already
  warned about from the brackets side.  `solutions/tcp.man` is the 32x32 world;
  the previous baked world is kept as `solutions/tcp-prev31x32.man` and
  rebuilds from `(build-tcp-grid #:deltas (hash 'cshape -1 'rec -4 'O '(10 . 0)))`.
  (`solutions/tcp-manual.man`, 28x31 @ 4275.8 = 4.11M, is still the best tcp
  world we own — hand-drawn, not build-reproducible, same story as
  reverse-manual.)
- `tcp-movables` is now EXPORTED (the template's derived list plus tcp's own
  `roc`/`rec` ring anchors), so the registry stops returning #f for it and
  measurement rigs stop carrying a hand-written copy.

## Where to look in this file

NOTES was NOT reorganized this pass: another agent was appending to it
throughout, and moving text under a concurrent writer is a merge hazard for no
correctness gain.  A reading guide by SECTION TITLE instead:

- **Judge facts** (only the real judge can change these): "Judge facts",
  "Parser lesson", "I/O rooms: the judge checks the WALLS", "grading.md,
  recorded", and inside "Reusable idioms" the two-level model and the I/O COUNT
  rule.
- **Idioms and mechanisms**: "Reusable idioms", "L1 v2: code melting", "L4: the
  problem harness", "L3 littlelang", "The 'bump tank former", and the
  per-problem sections (Sort, Brackets, tcp).
- **Landmines** are marked inline in caps.  The recurring ones: the memo key vs
  `#:accept?`; `#:near` for a melt whose partner is far away; giving a room all
  four degrees of freedom; a stress case outside the spec box; first-fit
  bumping starving the next channel; a bumped tank having no capacity margin;
  and the two added here — a former is part of the bake, and a tight body
  cannot hold a backtick literal.
- **Open questions**: pipe-arbitration order-dependence (needs a wall-backed
  bend preceding its own head between two NORMAL rooms); whether f1's two
  same-source walks into O really load; the input-side mirror of f3; and the
  display probes at the end of the file.

### Guide addendum, 2026-07-27 endgame (sections appended tonight, by title)

- **LAWS learned tonight** (also in PLAYBOOK "Landmines added 2026-07-27"):
  cfgsim BEFORE compile-cfg, every CFG, every time — see "THE HEADLINE:
  `gb-blocks` IS NOT CORRECT" (1/7 after three layout sessions; repro
  `scratchpad/gbsplit-simcheck.rkt`); and the PROVENANCE rule — a "validated"
  claim must name the artifact and its scope (gbproto validated the PACKING,
  not the CFG, and the distinction compressed away when the scratch file died).
- **Round-gated scoring is LATENCY**: "SUDOKU-STATION REPACKED BY THE
  FLOORPLAN PACKER" (judge = 48.5 x single-round latency, 0.04% prediction;
  rank floorplans by max-dim^2 x latency).
- **Targeting, not layout, is the station killer**: "Subset, the ROOM SPLIT"
  (enumerate wall assignments against `targeting-ok?` FIRST; `solve-attach`)
  and "Memory, STATION SPLIT" (`solve-pair`; guillotine packer + targeting
  solver = the missing tool, ~1.9x). Manhattan targeting means ROW splits are
  legal — "reverse: the ring was never the problem".
- **Idioms minted tonight**: sentinel-sign lap terminator freeing BP + ring-as-
  scratch discipline ("Gradebook attempt 4", "The two lap tricks"); sign-of-
  the-resident one-cell report ("Subset, the ROOM SPLIT" (2)); register-
  resident counter via `0 +` and direct C->O emission ("reverse: the ring was
  never the problem", 2.24x); auto-terminating unpack cycle (same section,
  honest negatives).
- **Cross-application ranking for the endgame hour**: REINTEGRATION.md in the
  repo root.

# Subset (subset sum): the MEASUREMENT GATE, and what it rules out (2026-07-26)

`problems/subset.rkt` — spec + all 7 public cases + 9 in-box stress cases +
a 400-case brute-force equivalence battery, registered in `harness/problems.rkt`
(id `b5e48adc-317d-480d-88a4-e2edc659453a`, caps 8M verify / 15M stress).
**No solution file yet**: the gate below says what has to be built, and the
numbers are the reason it is not the obvious thing.

- **Include-first DFS gives lex-smallest FOR FREE, and the proof needs
  POSITIVITY.** Try INCLUDE before EXCLUDE at each index; the first complete
  solution is the lex-min index set. That is lex order on decision vectors =
  lex order on sorted index lists **only because all values are positive**, so
  no solution is a proper subset of another — otherwise `{0}` vs `{0,1}` orders
  the wrong way (the DFS finds `{0,1}` first, but `[0]` is lex-smaller). The
  400-case battery in subset.rkt pins this against exhaustive enumeration, and
  separately pins that pruning never changes the answer.
- **The tick cap is 15,000,000 here, not the usual 5M** (stated on the page),
  and it is the whole problem. Node counts under overshoot+undershoot alone,
  n=20, in-box (`t` in 10-60% of the sum):
  avg **88k**, max **613k** over 300 random cases; the *public* n=20 case is
  112k nodes.
- **Four prunes, all NECESSARY conditions, all measured.** With
  `suf_i / smin_i / smax_i / cap_i = suf_i - smax_i` precomputed per index:
  `under` r>suf_i; `smin` r<smin_i; `maxcap` cap_i<r<smax_i (the largest
  remaining element cannot be used, so only cap_i is reachable); `hcap`
  floor(r/smin_i)*smax_i < r (r falls in a gap between the j-element windows).
  Effect on the public n=20 case: 112k -> 25k nodes. On the constructed
  adversaries, each of the last two is the difference between 1 node and a
  full tree:
  | adversary (all in-box) | under only | +smin+maxcap | +hcap |
  |---|---|---|---|
  | 19 small + one 50000, t=49999 | 1,572,863 | **1** | 1 |
  | 20x500, t=4750 | 520,675 | 335,919 | **1** |
  | near-uniform band, t between k-windows | 520,675 | 335,919 | **1** |
  `maxcap` is not optional: the "one big element" shape is PUBLIC TEST 5
  (`last-index-required`), and at n=20 it is 2^19 nodes without it.
  `hcap` is not optional either — it is worth 3x on the public n=20 case and
  infinity on every near-uniform case. **`ceil(r/smax_i) > n-i` adds NOTHING**
  (it is implied by `r > suf_i`, since suf_i <= (n-i)*smax_i): all of hcap's
  power is the `lo > hi` half.
- **A ring is a bad DFS stack, and the cost is exactly measurable.** Values
  live in the ring at one cell-group per index; the ring only rotates forward,
  so moving from index i to index j costs `(j-i) mod n` index-steps. Backtrack
  to the deepest include p lands at p+1, i.e. `n-k` steps where k is the number
  of trailing EXCLUDES stripped — so **a backtrack whose last decision was an
  include costs ZERO** (p+1 = i) and one over k excludes costs n-k. Measured
  over the whole search: **5.7 index-steps per node** (1 descent + ~4.7 wrap).
  At ~8 ticks per rotation that is ~46 ticks/node per cell in the group.
- **PACKING IS BLOCKED BY THE OFF HAND, and that is what sets the cell count.**
  Keep `r` (the remaining target) permanently in B and every prune is
  `(r ring)` + `-` + `X` — one cell, two ops, B survives `-`. But every unpack
  op (`/ % } &`) needs its constant in B, and materialising a constant in B
  destroys r; BP cannot be read back, and a cubby pipe would make five pipes on
  the controller (NOTES: four is where l1's targeting model runs out). So the
  fields cannot be packed: **one field per ring cell**, K cells per index,
  and K multiplies the dominant term. The one arithmetic escape found:
  `hcap` needs (h, smax, r) live at once, but `/` leaves `A=h, B=rem`, then
  `M` parks h in B, then the smax cell arrives in A and `*` gives h*smax in one
  op — so hcap costs one extra r-copy cell in the group, not a room split.
- **The identity worth keeping: `g = suf_i - r` is INVARIANT on include** (both
  drop by v_i) and drops by v_i on exclude, so the undershoot test is `g < 0`
  for free. It does not survive the other three prunes (they all need r itself
  against a different threshold), so it did not make the final design — but it
  is the right first thing to try on any suffix-sum walk.
- **What the gate RULES OUT, each measured rather than argued:**
  - *restart-lap DFS* (replay the path from index 0 each time, no wrap): 2x the
    rotations of the wrap design AND it re-evaluates prunes on the replayed
    prefix — ~6x worse end to end. The wrap is worth its complexity.
  - *greedy + descending-order feasibility oracle* (decide each index by asking
    "is r-v_i reachable from the suffix", oracle searching biggest-first): it
    IS 5x better on dense no-solution cases (64k vs 320k nodes) — but only
    1.6x on solvable ones (max 155k vs 240k over 150 random n=20 cases), and it
    costs a sort, a shrinking available-set, per-call suffix recomputation and
    witness bookkeeping. Wrong ratio of complexity to gain.
  - *bitset DP over sums*: t < 1e6 means 15,625 64-bit words of ring — ~125x125
    of pure pipe. Immune to every adversary and unaffordable on area.
  - *meet-in-the-middle*: 1024 sums per half needs sorted halves; insertion sort
    is 500k compares and tape merge sort is four 1024-cell tanks. No.
- **HONEST RESIDUAL RISK, and it is not fixable by cleverness.** A dense random
  n=20 in-box instance has ~10^5-10^6 near-miss subsets and *no cheap
  certificate exists* for "t is unreachable" — that is the problem itself. With
  the four prunes: median 29k nodes, p90 128k, max 387k over 300 cases. At the
  measured ~5.7 index-steps/node the top decile of n=20 cases will exceed the
  15M cap. All seven PUBLIC cases are comfortable (worst is `near-total-sum`
  at 25,295 nodes / 122,420 index-steps, ~6M ticks at K=5). So the expected
  failure mode on the hidden set is precisely: **n>=19, dense random values,
  no solution** — if casesPassed < casesTotal, that is the case to blame before
  suspecting the machine.
- **k = n is not expressible** and no stress case should try: t <= 60% of the
  value sum means at most ~60% of the values can be chosen. The extreme worth
  testing is k=1, and both directions of the big-element trap are in the stress
  list.

# CORRECTION + History Lesson judge campaign (2026-07-26, three load rules and a cap model)

**The old claim "COLUMN alignment is explicitly NOT an error — shipped
reverse.man stacks literals in the same columns with ops between them"
(appears twice above, in the backtick-statics entries) is WRONG on both
counts.**  Measured: reverse.man has NO column with two backticks at all
(nor do memory/tcp/triangular; sort.man has exactly one, cross-room).  And
the judge DOES pair backticks per column.  Judge-calibrated by two
rejections of history submissions plus the accepted corpus:

- **Backticks pair consecutively per COLUMN within a room, like rows.**
  Span with an op between a pair -> load error "expected a digit or a
  space between backticks, but found 's' at (2, 10)" (judge coords are
  (col,row); our D-room serpentine put word-opening ticks in the same
  column on alternating rows).
- **A clean (digit/space) paired span IS a vertical literal and its VALUE
  is range-checked both directions**: second rejection, "numeric literal
  exceeds the signed 64-bit register range — walked top-to-bottom it reads
  483…843 (35 digits) at (10, 16)".  Keep paired spans <= 18 digits.
- **Exemptions, from accepted files**: odd tick counts per column are fine
  (every literal-bearing accepted file has them); between-pair /
  after-last-tick cells are unconstrained; cross-room spans are exempt
  (sort.man col 14: two ticks in different rooms, ops between, 25/25).
- sim.rkt's `literal-column-warn?` has the polarity BACKWARDS relative to
  the judge: it warns on clean spans (which are fine if <= 18 digits) and
  says nothing about op-containing pairs (which are fatal).  Not changed
  here (sim is shared); the history generator carries its own conservative
  lint (`lint-room-columns!` + the column-class packer in
  problems/history-gen.rkt: op cells only in tick-free columns, <= 16
  digits between pair-forming ticks).

**The step cap is not wall-clock ticks.**  Six delay-probe submissions
(details in probes/literal-probes.md): a 2-man 2.196M-tick program RUNS to
completion, while the 6-man esc decoder step-caps at 1.95M local ticks even
after early-halting its data men (~6M man-steps, under the 7.5M a passing
probe exhibits).  Every surviving model charges for PIPE-VALUE MOVEMENT:
the decoder's 89-value ring travels ~19M value-cells over a run.  Lesson
for any tick-rich footprint problem: **a big circulating ring is not free
under this judge — value-count x pipe-length x rotations is a budget.**
Fix direction (designed, not landed): dispatch the hot 74% of symbols
through in-room base-128 table literals + a divmod extract loop, ring only
for the cold tail.  The hand layout of that CD room kept wedging on
crossing lanes; it wants the placement-search treatment, not more
hand-routing.

Deliverables: solutions/history.man = e0 mode, **judge PASSED 1/1, 91x90 =
8281** (footprint score = area^2 exactly; avgTicks comes back null).
solutions/history-esc-stepcap.man = the denser 87x87 esc build (sim-exact,
judge-step-capped) for whoever picks up the table-dispatch redesign.


# Memory sign-divert: the SIGN is the mark (33x33 @ 66,543,935 — new memory best)

`problems/memory-signdivert-sol.rkt` + `solutions/memory-signdivert.man`, a
SECOND memory world beside the shipped one.  `problems/memory-sol.rkt` and
`solutions/memory.man` are untouched by this pass.

**Judge: 24/24, 33x33, avgTicks 61,105.54, score 66,543,935**
(id `29445b54-1bbc-46c9-be61-ec5f0640d241`) against the previous memory best
`memory-manual.man` 33x33 @ 70,180.71 = 76,426,791 — **-12.9%** — and against
the best AUTOMATED world `memory-bump.man` 34x34 @ 70,133 = 81.1M, -17.9%.
Same max-dim as the hand layout, so the entire gain is TICKS.  The intermediate
34x34 build graded 70,780,435 on the way (id
`8580fa93-8bde-4300-a8b0-2712b8cc9175`), which is also a win over 76.4M and is
what the floorplan work below then improved on.

## The idiom: sign-as-mark halves the divert overhead

The MARK protocol rides each output value behind a sentinel literal 2^20: TWO
ring slots per output, and a forwarder whose per-value cost is a 3-op head plus
a 3-op body compare (idioms' `r W -` / `+ W s`, ~10 ticks/value).

Replace the MARK+value doublet with ONE value `dv = val - 2^22` and let the
SIGN carry the mark:

- everything that circulates (addresses 0..99, values |v| <= 1e6, sentinel -1)
  satisfies `v + 2^21 > 0`;
- every divert satisfies `dv + 2^21 = val - 2^21 < 0`;
- zero is unreachable, so `X` is a clean two-way with a dead straight arm.

F becomes: `B = 2^21` invariant in the prologue, head `r +`, `X`, cw body
`- s` (8 ticks/value), rare ccw arm `+ (s out)`.  C's read arm ends with
`B = 2^22`, which is FLUSH-SAFE — positive, so the sentinel xor stays negative,
and not an address, so the flush compare can never hit zero on another pair.
That invariant REPLACES the MARK build's "M restores B = target", and it is the
one subtle thing in the port: get it wrong and the flush halts on the addr-0
pair instead of draining.

**Channels, walls and the floorplan family are identical to the shipped
build**, so this is a drop-in protocol swap and not a topology change.
Measured: -18.6% on the 100-address stress (253,043 vs 310,844 emit), -12.9% on
the judge's own set.

**Where else this applies.**  Any MARK-protocol ring server whose circulating
domain is bounded away from an offset — i.e. `reverse` and `sort`, both of
which still pay the doublet through `idioms.rkt`'s `ff-blocks`.  Their tick
terms are only ~1.53x local against memory's 5.85x, so the absolute prize is
small (2.15M and 4.25M total), but the port is a CFG swap plus a re-gravity and
nothing else.  The precondition to check first is the same one: every value on
the ring must satisfy `v + K/2 > 0` for the chosen offset K, and `K/2` must
exceed the value bound — for a bound of 1e6 the smallest usable K is 2^22.

## Two floorplan lessons, both worth more here than the protocol was

**(1) CHAIN ORDER IS A FLOORPLAN KNOB, and nobody had turned it.**  The shelf
packer lays chains in LIST ORDER, so the order decides which lanes share a
shelf and therefore C's whole Pareto front.  Same blocks, same tight pairs,
same `#:col-order`, same veto — only the order of the chain list.  A 61-point
random shuffle sweep moved C's front from

    ((22 20) (24 18) (25 18) (27 16))       <- order inherited from memory-sol
    ((20 19) (22 17) (23 16) (24 15) ...)   <- shuffle #13

and the 22x17 room is exactly what takes the world from **34x34 to 33x33**
(-5.7% score at unchanged ticks — the s100 emit actually fell slightly, 253,043
-> 252,978).  This is nearly free: a pure `compile-cfg` loop, no simulation,
~2 minutes per 60 orders.  **Worth running on every room whose menu sits on the
critical dimension** — sort, reverse and tcp have never had it.  One landmine,
which cost an hour here: the screening sweep must use the SAME `#:accept?` veto
the real menu uses, or it advertises fronts the builder cannot reach (shapes
that vanish the moment the targeting rule is applied).

**(2) A BACKTICK LITERAL IS A ROOM-WIDTH FLOOR, so build the constant by
shifting.**  `` `2097152` `` is nine cells in one eastward run and it sets F's
minimum width.  `` `21` `` `M` `1` `{` `M` is eight cells whose longest run is
FOUR and computes the same 2^21: F's menu went 14x6/15x6/16x5 ->
**12x6/13x6/14x5**, and its static tick estimate fell too (1345 -> 1221).  The
same works for C's `` `4194304` `` (`` `22` `` `M` `1` `{` `M`), with one
ordering constraint that is easy to get wrong: the constant must be built
BEFORE the `r ring` that loads the value, because `{` needs B as the shift
count and the value would otherwise be sitting in it.  templates.rkt's landmine
(1) already advised "prefer digit arithmetic, it keeps the constant out of the
room's width floor"; this is the measurement of how much — about five columns
off the floor per nine-digit literal.

HONEST FOOTNOTE: the shift form is NOT in the shipped file.  It is correct
(gated, 33x33, marginally fewer ticks) but at these room sizes it bought no
max-dim, and a bake that does not move the score is not worth the churn.  It is
the right first move for anyone attacking md 32 — see below.

## md 32 was hunted and not found, and the cell budget says why

Four independent searches (two chain orders x two literal encodings, each a
full cshape x fshape x band x F/O/I gravity on the bump former) all bottom out
at **33**, reaching 32 on ONE axis (32x33, 32x36) but never both.  The budget
argument agrees and is worth writing down as the floor for this room set:
C 24x19 walled ~= 456 + F ~= 112 + I/O 50 + two 210-cell tanks 420 ~= 1038
committed cells against 32^2 = 1024.  So 32x32 is *below* the packing floor
unless a room genuinely shrinks — which means the shift-literal C (or a
narrower CFG), not more search.  Do not re-run the gravity hoping for 32.

## Gate, bake and reproducibility

`(build-memory-signdivert-grid)` reproduces `solutions/memory-signdivert.man`
byte for byte.  BASE-DELTAS holds the summed optimum (`cshape 1`, `fshape 0`,
`band 0`, `I (-2 . 4)`, `O (-6 . 0)`, `F (-5 . -3)`) and `MEMORY-TANK-FORMER`
is `'bump` — **the former is part of the bake** here exactly as for memory-sol.
Every md-33/34 point any of the sweeps found was BUMPED; the best melt world in
the same sweeps was md 35, and the melt at THESE deltas is a 37x34 loss.

Gate on every candidate: 7/7 public + all four registered stress cases at their
per-case caps (100-address at 500k, boundary, overwrite, never-written) + the
literal lint + byte-repro + an **output LEAK check**.  The leak check is
specific to this design and worth keeping in any sign/offset protocol: the
trick is internal, so the gate asserts that no emitted value ever leaves the
spec box (|v| <= 1e6) in addition to matching the spec exactly.  A botched
restore in F's cw arm would otherwise surface as an ordinary wrong number
rather than as an obviously out-of-domain one.  Local: 33x33 @ 10,904.4 public
avg = 11.87M (shipped memory 34x34 @ 11,901.1 = 13.76M).

## Method note: what predicts the judge here, and what does not

Public average is a poor ranking signal for memory (x5.85 judge multiplier).
`0.2256 * stress100-emit`, calibrated on the two previously graded builds,
predicted 57.1k against an actual 61.2k — good enough to RANK floorplans, ~7%
optimistic as a level.  The honest calibration after these two graded
sign-divert builds is **judge-avg ~= 0.242 * stress100-emit**.

More useful than either: at a fixed `(cshape, fshape)` with BUMPED tanks, ticks
are essentially INVARIANT to the placement deltas — both tanks are exactly
`cap` cells, so the ring length does not move, and s100 varied by 0.07% across
four md-34/35 winners from different basins.  So memory's floorplan search can
be AREA-ONLY (build + `program-dims` + a cell count, ~0.2 s a point instead of
~3 s), and only a shape or protocol swap needs simulating.  That is what made a
12-way parallel gravity sweep affordable.

## Stretch item #3 (direct C->O bouncer): the report's blocker is REAL but MISDIAGNOSED

`problems/memory-bouncer-sol.rkt` is the speculation report's item #3 built out
on `define-ring-server`'s `#:out-src 'C` variant: C owns a second outgoing pipe
to O, F is tcp's two-op bouncer, both constants vanish.  The report said the
blocker was C's out-targeting and prescribed tcp's playbook.  Two findings, and
the second is the one that matters:

**The playbook works at the ROOM level, but only with a chain-order sweep.**
Every `(s out)` isolated into its own one-op chain plus
`#:col-order '((r ring in) (s out ring))` is NOT sufficient by itself: with the
inherited chain order C's Pareto front collapses to a single **37x13** shape (a
>=39-wide world, ~79M even granting the full tick win), and with HARD bands it
collapses to nothing at all:

    col-order ((r ring in) (s out ring))  strict #t -> ()   (no room at any width)
    col-order ((r ring in) (s out ring))  strict #f -> ()
    col-order ((r ring in) (s ring out))  strict #t -> ()
    col-order ((r ring in) (s ring out))  strict #f -> ((37 13))
    no col-order, no veto                          -> ((14 26) ... (25 14))

Run the chain-order sweep over the four-pipe veto and roughly 1 order in 30
lays a compact room: **24x17 / 25x17**, with F at **5x2, est 8 ticks**.  So the
room is not the wall.

**The wall is the FLOORPLAN, and it is structural.**  Every assemble of that
room fails with `assemble: room C: no out-attachment satisfies targeting`, at
every band, for out-walls `(n nw)`, `(nw)`, `(n nw w)`, `(s sw)`, `(sw w)` and
the union.  The reason is geometric and does not depend on search effort: the
send band puts every `s out` op in C's WEST columns, so the only wall cells
nearer to them than to `ring-out`'s east-wall cell are on C's WEST wall — and
`define-ring-server` anchors C at `CX = 0`, where the west wall faces the world
edge and has no outward cell at all.  The north-west is already the `ret`
landing and the south-west is the world's bottom edge.  tcp escapes this
because its C is naturally DIAGONAL (ring traffic upper-west, I/O lower-east)
and its I/O rooms live in a strip east of C; memory's C is ring code in almost
every block, so the split runs down the middle of the room and both ends of it
are pinned.

**What item #3 actually needs** is therefore one of: (a) C not anchored at
column 0 — a one-line template change, but it moves every other ring server's
bytes, so it needs its own gated pass; or (b) a C CFG restructured so the send
ops are genuinely one-sided rather than merely partitioned. Not "apply tcp's
col-order", which is what the report predicted and what this pass proved
insufficient.  The file is kept, builds its menus, and its 5x2 bouncer is
ready; the prize is still real (an F at 6 ticks/value against the 8 shipped
here), but it is a floorplan project, not a targeting fix.


# The playbook layer: PLAYBOOK.md, CLASSES.md, harness/estimate.rkt (2026-07-26)

Three new files, all DISTILLED from this repo and its history — nothing in them
is a new judgment about the language.  The point is that a brief for a new
problem should be ~200 words ("solve X, it's a heavy-state server, playbook
applies") instead of ~800 words of re-derivation.  `OVERVIEW.md` gained one
section linking them.

- **`PLAYBOOK.md`** — the SOP, in the order the steps actually happen:
  transcribe+assert -> measurement gate (only when algorithmically risky) ->
  implement (littlelang first, hand-CFG fallback, refusals recorded) -> world
  declaration -> verify -> stress at SPEC MAX -> optimize -> bake via OFFSET
  deltas -> lint -> submit -> record.  Plus the operational rules that are
  about the AGENT rather than the compiler (timeout-wrap at 300s;
  foreground-sized chunks, because backgrounded long commands silently
  restart; never emit a large blob — a 64k output cap kills the agent; batch
  into few processes because the first build pays ~70s of menu sweeps; cap
  ticks just above the observed emit), the coexistence etiquette this tree has
  been running on (ownership declarations, side tables instead of struct
  fields, append-last-with-re-read for NOTES/CURRENTSCORES/registry, atomic
  writes, wait-60s-retry), and the five-section report format.
- **`CLASSES.md`** — the casebook: PURE FUNCTION (triangular), PIPELINE
  (brackets), RING SERVER (reverse/sort/tcp, incl. the MARK-vs-direct-out
  decision as a register-pressure question), HEAVY-STATE SERVER
  (memory/gradebook), BOUNDED SEARCH (subset), FIXED-OUTPUT/FOOTPRINT
  (history, the three literal rules, the activity-cap model), DISPLAY
  (infrastructure only, with the d1-d9 probe table and what each costs if we
  guessed wrong).  Each row: the smell, the template and exemplar files, which
  score term dominates, the judge multiplier, the class landmine list.  It
  closes with a decision tree extending OVERVIEW's recipe.
- **`harness/estimate.rkt`** — a cost ORACLE, one screen of arithmetic:

      controller ticks = ops x (TICKS/CELL x walk-fraction x ring-resident
                                + TICKS/RAIL x rails-per-op)
      forwarder ticks  = (ring cells popped) x per-value forwarder cost
      local            = MAX of the two        <- which one binds is the answer
      activity         = ticks x (men + circulating-fraction x ring-resident)

  Constants are the ones NOTES already measured: 10 ticks per ring cell in a
  tight circuit / 12 in a chain loop, 20 per rail transfer (from sort's ~150
  ticks-per-value on rails and tcp's ~8 transfers inside a ~377-tick packet),
  forwarder 10 MARK / 8 sign-divert / 6 bouncer / 0 direct.  Calibration
  against the LARGEST public case of each shipped problem (`racket
  harness/estimate.rkt`; `raco test` asserts the ratios stay in 0.7..1.4):

  | case | estimate | actual | ratio |
  |---|---|---|---|
  | brackets c8 (n=64)    | 3840  | 3495  | 1.10 |
  | reverse c7 (3 rounds) | 7995  | 7392  | 1.08 |
  | sort c6 (4 rounds)    | 12220 | 10580 | 1.16 |
  | tcp c5 (n=32)         | 9920  | 11817 | 0.84 |
  | memory c6 (125 ops)   | 71897 | 71303 | 1.01 |

  triangular is OUT OF MODEL (13 ticks — below ~100 the constants dominate);
  history is out of the TICK model and is the ACTIVITY calibration instead
  (esc decoder 1.95M ticks x (6 men + 0.11x89 circulating) ~ 30.8M units ->
  step-capped, against ~7.5M for a passing probe; shipped e0 ~4.7M -> passed).

- **The one thing that came out of the distillation rather than into it:
  WHY the judge multipliers differ.**  They are not a property of the machine,
  they are how much heavier the HIDDEN case set is than the published one, and
  the rule that fits all five measured problems is whether a PUBLIC case
  already sits at the SPEC MAXIMUM.  reverse/sort/tcp/brackets do (1.53, 1.53,
  1.71, 2.05); memory does NOT — its biggest public case touches 41 distinct
  addresses against a spec maximum of 100, and its cost is ops x ring length,
  so the hidden set finds ~5.85x.  Practical form: **if your public suite's
  worst case is far below the spec box on a superlinear cost, budget ~6x, not
  ~1.5x** — and that is exactly the situation the spec-max stress case exists
  to measure locally before the judge does it for you.

# L3 v2: live-in inference, auto-split, auto-spill, declarative sentinels (2026-07-26)

The whole v1 roadmap in `l3/RESULTS.md` except the chain partition. `l3/` only;
nothing below L3 changed. Numbers are full public suites through the
judge-exact sim, each world given its own shape menus and its own
`gravity-optimize` run.

| | dims | avg ticks | score | suite |
|---|---|---|---|---|
| brackets shipped (hand) | 27x25 | 617.4 | 450,085 | 9/9 |
| brackets littlelang v1 | 25x29 | 644.2 | 541,791 | 9/9 |
| brackets littlelang **v2** | 25x28 | **621.4** | **487,212** | 9/9 |
| brackets **one-room source, AUTO-SPLIT** | 26x34 | 754.8 | 872,523 | **9/9** |
| reverse littlelang v1 = v2 | 30x30 | 1837.9 | 1,654,088 | 8/8 |

brackets v2 is **+0.7% ticks against the hand-written solution** (was +4.3%).
reverse is byte-identical between v1 and v2 in every block, chain and tight
annotation.

- **A label's live-in set has to be inferred BEFORE code is emitted, not
  after.** This is the ordering constraint that makes the feature look harder
  than it is. The obvious design — emit once, run liveness on the CFG, re-emit
  — cannot work on its own, because a label whose *declared* state is wrong
  makes the first pass unschedulable and there is then no CFG to analyse. The
  fixpoint therefore runs over the SOURCE's own goto graph (two booleans per
  statement: may-read-before-write, definitely-overwrites), and the CFG-level
  register liveness is a second, refining pass on top. Deleting all three
  `#:needs ()` from `demo-brackets.rkt` now yields byte-identical blocks.

- **Three places want the same analysis, and the third is the one you forget.**
  Label bodies; loop heads (a `(forever (set! s 0) ...)` head does not need the
  resident back on its own back edge); and **the join labels structured
  lowering mints after every branch and every `break`-carrying loop**. v1 gave
  every join the current B-resident as a live-in, so each arm put it back even
  when nothing downstream looked at it. The enclosing statement list *is* the
  continuation, so it is one more call to the same function — but until it was
  added, every projected one-room program died at its epilogue.

- **The epilogue sharing is BISIMULATION MERGING, and it needs no liveness at
  all.** Coarsest partition refinement on (ops, terminator shape, successor
  classes, must-follow class). Two blocks in one class run the same ops and
  hand control to interchangeable blocks, so they are interchangeable *for any
  entry state* — which is exactly the property an all-or-nothing `#:needs`
  cannot express. brackets C: 18 blocks / 33 ops / 6 chains / 4 tight → **15 /
  29 / 5 / 3**, against the hand-written 14 / 31 / 5 / 3. It found one merge the
  roadmap did not predict: the *balanced* answer's `(s out) -> start` block is
  bisimilar to the `bp-count` exit block, so those merged too.

- **THREE LATENT v1 BUGS, all in the zero-arm refinement, all invisible to v1's
  own demos.** (1) The equation `T = 0` was being substituted into the off
  hand's goal even when the pivot was the B-resident's OWN home atom — so on
  the zero arm of `(case-sign s ...)` B stopped being "s" and became the
  constant 0, and the next jump to any label wanting `s` was unschedulable.
  `unit-pivot` already prefers a non-resident atom; the fix is to skip the
  substitution when there is no other atom to prefer. The forwarder's MARK arm,
  which is the reason the substitution exists, pivots on the read atom and is
  unaffected. (2) `set!` took the resident's home from the ENVIRONMENT, which
  the same equation may have rewritten to a constant, so `(set! s ...)` on that
  arm declared "B holds 0" and the resident silently ceased to exist; take it
  from `bres` instead. (3) A per-op live-after list was built in reverse in
  DCE, which deleted the base-3 push loop outright — caught in one run by
  byte-diffing the smoke tests against v1. **Any `(case-sign <B-resident> ...)`
  whose continuation still wants the resident hits (1) and (2); v1's two demos
  happen never to write one.**

- **Auto-split is a PROJECTION, not a search over cut points.** `l3/autosplit.rkt`.
  Choose which declared storage the consumer keeps, then project the statement
  tree twice; four rules do everything. A `let` whose initialiser is free of
  consumer state but whose body needs it is a CROSSING (send/recv, and it
  collapses to a bare `(send CH expr)` when the producer half of the body is
  empty). A branch whose test is a producer value and whose arms project to the
  SAME consumer code is a CONVERGED CUT — **that is what a classifier is**,
  several arms collapsing to one number, and it is what puts brackets' entire
  `-1 / mod 4 / div 8` in the producer. A branch whose arms disagree goes to the
  consumer whole. A loop containing a cut is SPLIT, the producer appending a
  terminator `(send CH 0)` and the consumer becoming a sentinel-terminated pass
  — with TERMINATOR FUSION into an existing dead zero arm, which is how the
  consumer's scan block comes out as the hand solution's `(x endround push pop)`
  instead of paying an extra test per character. Every candidate is verified by
  compiling both stages; if none works the v1 diagnostic is re-raised with the
  rejected attempts appended, so the diagnostic path survives (test case 10).

- **For brackets there is no one-room program at all, and that is the finding.**
  The stack wants B for a round and the classifier wants B for its divisors;
  the answer position wants the backpack for a round and `countdown` wants the
  backpack to sequence it. Three persistent values against two hands and a
  backpack. **The split is not an optimisation, it is the only legal storage
  assignment** — and the compiler now derives it, emitting a D that is
  byte-identical to the hand-partitioned one (7 blocks, 24 ops, including the
  trailing `0 (s out)` round marker, which it synthesised as the channel
  terminator rather than copying from anywhere) plus a channel manifest the
  demo's `chan-spec` list is built from.

- **A projection can partition; it cannot restructure**, and the cost is
  measurable: +21.5% ticks against the hand partition. The one-room source has
  to encode "this round already failed" in `s` and test it per character
  because it has no second room to hold that state, and that extra `case-sign`
  costs the tight push loop (1 tight circuit against 3) and three extra chains.
  Auto-split will never invent the second room's *algorithm*.

- **A fetched ring value lives in A until it is stored back — there is nowhere
  else for it to be.** That single fact fixes the whole access discipline for
  `#:in 'ring`: the fetch/store pair must bracket the UPDATE, not the loop.
  Statement lists are split into maximal runs mentioning the variable; fetch
  before the run, store immediately after the last statement that assigns it,
  and `(set! x ...)` is then purely symbolic and costs no op. The counter idiom
  comes out as reverse's `passc`, `(r ring) - (s ring)` then the branch, tight
  body included, from one declaration. **What it does not cover**, honestly:
  one slot only; no ring that doubles as a data store (reverse writes `k-1`
  back BEFORE rotating `k` values past it — the write-back POSITION is
  load-bearing and the automatic placement is wrong for it, so reverse's
  controller stays hand-written); no update needing the off hand; no `labels`.
  CFG-validated, not suite-validated.

- **`(ring-pass CH #:sentinel EXPR #:cell y ...)` reproduces tcp's deposit path
  block for block.** Tell the compiler one fact — at the loop exit
  `A = sentinel + 1` — and for `-(waiting+1)` that makes `A = -waiting`, so the
  ordinary shuffle search finds `N M` by itself. Generated head / body / exit
  are `rh` / `rc` / `rdone` from `tcp-sol.rkt` exactly, tight classification
  included; the prologue differs only in building `-(w+1)` as `1 N -` where the
  hand code writes `1 + N`. Nothing about tcp is special-cased. This is finding
  (f) — the spill target is the tag itself — turned into a declaration.

- **Still open, in cost order.** (1) The CHAIN PARTITION, unchanged and still
  the largest lever: the auto-split's C has 8 chains against the hand version's
  5, and `#:chain-limit` from 8 to 24 gives byte-identical output because the
  partition is pinned by hard `must-follow` constraints, not by the budget — so
  exposing it to the L2 search means exposing the *constraints*, not the
  number. (2) auto-split cannot restructure. (3) multi-slot rings and rings
  that double as data stores. (4) backward propagation of the next state goal,
  still the one-op-tolerance heuristic. (5) `#:sentinel` on a plain pipe.
  (6) auto-split refuses sources using `labels`/`goto` — the cut rules are
  defined over structured loops, which is why `demo-brackets.rkt` (labels) and
  `demo-brackets-split.rkt` (structured loops) are two different sources.

# Sudoku: index the ring by the LAST input, and a pipe as the third register

`problems/sudoku.rkt` (spec + a PARSER for the 1779-line page + load assertions
+ 21 stress cases), `problems/sudoku-sol.rkt`, `solutions/sudoku.man` —
**32x32 @ 10094.5 local = 10.34M; judge 20/20, avgTicks 14221.35, score
14,562,662** (id `c904d1a7-68c4-40f6-a17c-782c50103191`, problem
`f66c928f-3369-4870-9153-8b20cafc2ecd`). 6/6 public, 21/21 stress, 200 fuzz
cases against the spec, 0 failures. Uber-strict problem (extra hidden corpus).

- **The state layout was the whole problem, and the obvious one is wrong.**
  27 units (9 rows, 9 cols, 9 boxes) x 9 values = 243 bits, so the state lives
  in the ring. Index the ring BY UNIT — 27 cells of a nine-bit mask — and a
  round touches cells r, 9+c and 18+box: the rotation counts are known from the
  first two inputs and the bit only from the third, but nothing survives a
  rotation except B and B has to hold the bit. Index it BY VALUE instead — 9
  cells of a 27-bit mask over the units — and a round touches exactly ONE cell,
  the rotation count is `v-1` (the LAST input, available exactly when needed),
  and the three unit tests collapse into one word `mask3` = 2^(1+r) + 2^(10+c)
  + 2^(19+b) that is ready before v is even read. Same state, a third of the
  ring traffic, one live value instead of three. **Ask which input arrives LAST
  and index the store by that** — it is the cheapest question in this family
  and I did not think to ask it until the third encoding.
- **The handle: four ops that TEST and UPDATE in one pass, B invariant.** Cell
  y in A, mask3 in B:

      ~          A = t = y XOR mask3     (all three bits toggled at once)
      (s ret)    push t back             (`s` does NOT clobber A)
      &          A = t AND mask3
      -          A = (t AND mask3) - mask3

  which is <= 0 always and ZERO exactly when all three bits are now set, i.e.
  exactly when none was set before. The verdict is an `X` zero arm, B never
  moves, and one visit to the cell is enough. Both obvious orders fail: `&`
  first tests correctly and loses y; `~` first updates correctly and cannot
  test. **Sending BETWEEN them is what makes one pass enough** — `s` is the
  only op that reads A without changing it, so it is free scheduling slack in
  the middle of an expression, and it is worth looking for on any
  read-modify-write of a ring cell.
- **A PIPE IS A THIRD REGISTER if you will spend a send.** mask3 needs r, c,
  r/3 and c/3 live at once plus a shift per term; the ring room needs B for
  mask3 across the whole lap and BP for the rotation count. The fix is not a
  spill: the arithmetic room sends the three terms as THREE SEPARATE VALUES and
  the ring room accumulates them (`r M r + M r + M`), because the consumer's
  registers are free at exactly the instant the producer's are not. The
  producer then never holds a partial sum and its whole round fits in A, B and
  a <=2-iteration backpack count. This is the brackets room-split argument one
  level down: the split is of an EXPRESSION, not of the control flow, and it
  costs three sends on a pipe that already exists.
- **Divide the OFFSET, not the value.** `2 << (9+c)` leaves 9+c in B and c
  apparently gone; recovering it cost four ops (`M 9 W -`) until the identity:
  (9+c)/3 = 3 + c/3 EXACTLY, so dividing the offset value carries the offset
  through, and the constant 3 it adds to the box index is absorbed by starting
  the exponent base at 15 instead of 18. A constant error in an exponent is
  free; a recovery is not. -4 ops, -4% ticks.
- **Put the guard bit at the BOTTOM.** Every ring cell needs a bit no mask
  touches, so that the 0 sentinel is the only non-positive cell and both relay
  loops terminate on a bare `X` with exactly ONE continue arm (the `#:tight`
  precondition — two continue arms cannot both rail-enter a tight body). Bit 27
  costs an eight-op 2^27 in the seeder and starts every shift from `1`; BIT 0
  costs the digit `1` and starts every shift from `2`. Same invariant, seven
  ops cheaper, and the whole program ends up with **no backtick literal at
  all** — every constant is a single digit — so both literal checkers are
  vacuous and no chain heading can reverse anything.
- **Deadlock is a capacity ARGUMENT, not a guess.** Both rooms send into the
  other's tank, so "both tanks full" is a real deadlock, not a stall. The loop
  holds at most 10 ring cells + one round's 4 control values = 14 values ever,
  so any `2*CAP > 14` is provably safe. CAP 10, and the tanks stopped setting
  the floorplan.
- **THE JUDGE'S TICK RATIO IS NOT A CONSTANT OF THE PROBLEM — it is a function
  of the FLOORPLAN, and the local sim cannot see it.** Two builds of this same
  program: 31x33 -> judge 13549.7 against local 10077.2 (**x1.345**), and
  32x32 -> judge 14221.35 against local 10094.5 (**x1.409**). Local ticks moved
  0.2%; judge ticks moved 5%. The reason is round gating: round N+1's input is
  withheld until round N's output arrives, so on a multi-round problem the
  round-trip PIPE LATENCY sits on the critical path of every single round,
  while the continuous-feed local sim hides it. The smaller world routes its
  tanks longer, and part of the 6% area win came back as ticks (net still a
  win: 14.76M -> 14.56M). Two consequences: (1) on a gated problem, prefer the
  floorplan with SHORT pipes between the rooms that talk each round, not merely
  the one with the small bounding box; (2) NOTES' earlier "x1.53 on reverse,
  x1.5-2 on multi-round" is a per-BUILD number, so do not port a ratio from one
  build to another to estimate a score.
- **Empty-line compaction makes `band` a DEAD gravity movable here.** A sweep
  over band deltas -14..+2 produced literally the same height at every value:
  the slack rows are all-empty and compaction deletes them. Gravity spends a
  whole axis of its neighbourhood on it and parks after one step (33 -> 32).
  What actually moved the floorplan was an exhaustive sweep of the two SHAPE
  MENUS x F's offset. If a movable's whole range is score-identical, it is not
  a movable — check that before concluding the basin is flat.
- **l3 wrote the ring room, block for block, including the handle above.**
  `f-prog` is 20 lines of littlelang and the emitted CFG is what I had derived
  by hand, tight loops and all. It REFUSED the arithmetic room, verbatim:

      l3: cannot get the machine into the state this statement needs.
        want:  A = cq.11, B = -
        have:  A = 1, B = 1   (block loop1)

  on a `(bp-count w cq ...)` whose seed is live in A while the count needs
  B = 1. The missing move is the SAVE-LOAD-SWAP, `M` <digit> `W`: it
  materialises a constant into B while PRESERVING A, and it is the only way to
  set up `/`, `{` or a counted add when the value you are about to operate on
  is the one already in A. Four of the arithmetic room's five constant setups
  are that idiom. **Teaching the shuffle search this one three-op pattern would
  have put the whole problem in littlelang** — it is a strictly bigger win than
  any new surface syntax.
- **Negative result, recorded so it is not re-run on a hunch: merging D's chain
  partition (6 chains -> 3, to spend fewer rails) made every floorplan in the
  swept region INFEASIBLE.** Chain length is lane length, the merged room is
  much wider, and the baked deltas plus the whole neighbourhood around them
  stop building — same lesson as l3's "the shipped files' baked deltas are not
  merely suboptimal against generated rooms, they are infeasible". A chain
  repartition is a room-SHAPE change and has to be re-floorplanned from
  scratch, so it is not a cheap experiment even though the edit is one line.

# Subset: the tick model was WRONG BY 2.3x, and `hcap` turns out to be MANDATORY and IMPOSSIBLE (2026-07-26)

Follow-up to "Subset (subset sum): the MEASUREMENT GATE" above.  Three
results, each measured rather than argued, and each one changes what the
next agent should build.  **No solution file was produced**: the design the
gate specified does not fit the cap, and the design that does fit needs a
machine feature this topology does not have.

**(0) THE STEP LIMIT IS NOT THE DEFAULT.**  subset.md line 3 states
`**Tick cap: 15,000,000 per test case.**`  grading.md's 5M is overridden.
The gate entry already said so; recording it again because a brief built on
"6M > the 5M cap, cut per-node cost 25%" reached me and cost real time.

**(1) THE BACKTRACK COSTS A FULL LAP, NOT `n-k`.**  The gate's model says
"backtrack to the deepest include p lands at p+1, i.e. n-k index-steps, so a
backtrack whose last decision was an include costs ZERO."  That is wrong, and
it is the whole error.  Landing at p+1 is not enough: the machine has to
**physically revisit p** to read `v_p` back out of the ring and restore
`r += v_p`, because r's restore value lives nowhere else.  Rotating forward
from i to p costs `(p-i) mod M = M-1-k`, then one more step to p+1, so a
backtrack costs **`M-k` where k=0 gives M — a FULL LAP (M = n+1 groups)**,
not zero.  `(p+1-i) mod n` reads 0 for k=0 only because mod arithmetic
throws away the lap you actually have to walk.

Measured on the true control flow (`scratchpad/ss-steps.rkt`), group
rotations for the worst PUBLIC case (`near-total-sum, 20 values`):

| prune set | nodes | group rotations | ticks @ 22/rot + 25/node |
|---|---|---|---|
| under+smin+maxcap | 77,215 | 804,803 | **19.6M — OVER THE 15M CAP** |
| + hcap | 25,295 | 259,643 | **6.3M — fits, 2.4x margin** |

The gate's "122,420 index-steps, ~6M ticks at K=5" for the same case is the
`n-k` model; the true figure for that prune set is 259,643 rotations.  The
two agree on ticks only by coincidence (their ~49 ticks/step vs the true
~24 ticks/rotation over 2.1x more rotations).

**(2) SO `hcap` IS NOT AN OPTIMIZATION, IT IS THE CAP.**  Without it the
hardest public case is 30% over the judge's own limit, which fails that case
and every hidden case shaped like it.  With it there is 2.4x of margin.  The
gate rated hcap "worth 3x on the public n=20 case"; at the true rotation
count it is worth 3.1x and it is the difference between passing and failing.

**(3) AND `hcap` IS NOT IMPLEMENTABLE WITH TWO REGISTERS.**  This is the
result to carry forward; it generalises past this problem.

*Why every OTHER prune is cheap.*  Keep `r` permanently in B.  Then a ring
cell c costs `(r ring) (s ring) - X` and yields `sign(c - r)`, and **B
survives**, because `-` `*` `%` `}` `{` `&` `|` `~` all leave B untouched.
`s` does not clobber A either, so a cell can be pushed back and still used.
So THRESHOLD prunes are 1 cell each, uniform, and the ring rotation stays
blind.  under/smin/maxcap = cells [suf, smin, cap, smax], plus [v]: K=5.

*Why hcap is different.*  `/` is **the only op that writes B** (A = quotient,
B = remainder).  hcap is `floor(r/smin)*smax < r`, i.e. the identity
`h*(smax-smin) < rem` — and `/` delivers exactly `(h, rem)` into `(A, B)`,
both live.  The third operand (`smax`, or `D = smax-smin`) can only arrive
by `r ring`, which lands in **A**.  Three live values, two registers.

*Why you cannot dodge it.*  Every escape was tried and each one fails for a
stated reason:
- **Re-fetch r.**  A ring cell can be DUPLICATED inside the group, so any
  per-index constant is re-fetchable for the price of one cell.  `r` cannot:
  it is not a ring cell, and anything pushed onto a FIFO ring comes back a
  full lap later, never within the step.  This is the crux.
- **Carry `g = suf - r` instead of r** (the gate's invariant).  It re-derives
  r from any `suf` cell for free (`-` preserves B) and even makes maxcap
  prettier — `maxcap <=> cap < g < smax`, both tests against g — but `/`
  destroys g exactly as it destroys r, and g is then unrecoverable because
  recovering it needs r.  Circular.
- **BP as the third register.**  BP is write-only in the arithmetic sense:
  `b` (BP:=A), `m` (BP-=1), `]` (BP>>=1), `d`/`a`/`x` (branch).  There is no
  add, no read-back, and no way to get BP into an operand.  It can hold a
  SIGN you will test later; it cannot hold a multiplicand.
- **`%` instead of `/`.**  `%` does preserve B — but it preserves the
  DIVISOR, and the dividend (r) is the value you needed to keep.
- **Weaken h.**  Any OVER-estimate of `floor(r/smin)` keeps the prune sound
  (it only fires less).  `h' = r >> floor(log2 smin)` is 2 ops and needs no
  division — but it is up to 2x too big and stops firing on the cases that
  matter: on `20x500, t=4750` it gives 18*500 = 9000 > 4750, i.e. no prune,
  where exact hcap collapses the case to 1 node.
- **Any other modular prune** (gcd of the suffix, divisibility) dies
  identically: it consumes r in `%`/`/` and r cannot be restored.

*The fix, for whoever picks this up.*  A genuine third register.  The
cheapest form is a **cubby**: a 3x3 bounce room with a two-op man
(`(r cin) (s cout)`) and a 2-cell pipe each way, used as `stash` / `fetch`.
That costs C a fifth and sixth pipe (reads {ret, cubby, in}, sends {ring,
cubby}), so C's `#:col-order` grows to three read bands, and the world can
no longer come from `define-ring-server` — it wants `assemble` directly, the
way memory does.  Latency is ~6-8 ticks per round trip and it is paid ONCE
PER NODE (only on the hcap path), i.e. ~25k times on the worst public case:
under 0.2M ticks against a 6.3M budget.  It is cheap; it is just not a small
edit.  **This entry is that task's requirements doc.**

**(4) THE JUDGE'S CAP MAY NOT BE TICKS AT ALL, AND FOR A RING THE LAW IS
EXACT.**  Per the History Lesson probe campaign above, every surviving model
of the step cap charges for PIPE-VALUE MOVEMENT.  For a ring server that
quantity has a closed form:

> **moves = (ring pops) x L**, where L is the ring circumference in cells,
> because each pop is one value having travelled exactly one full lap.
> A melted tank's cell count is its capacity, and the tanks must hold every
> resident value, so **L >= K*n** and therefore
> **moves ~ (index-steps) x K^2 x n** — QUADRATIC in cells-per-index.

For subset at K=5, n=20 that is ~61M moves against ~6M ticks (ratio ~10 —
the same ratio the step-capped esc decoder exhibited).  Worse, the floor is
structural: with the full prune set you need ~5 constants x 20 indices = 100
residents, so moves >= 500 x index-steps, and 15M would demand fewer than
~5k nodes where the worst public case is 25k.  **If the move model is real at
parity, NO ring DFS fits this problem and no K tuning rescues it** — the
answer would have to be a different machine, not a cheaper ring.  Since the
page states a TICK cap and the move model rests on two probe points, the
right move is to build to ticks and MEASURE moves, which is now possible:

**`sim.rkt` gained `sim-pipe-moves`** — a `(box 0)` holding stage-1's total
value-cell-move count for the last `run-program`.  Purely diagnostic,
semantics-neutral (one counter, reset at start, published beside
`sim-result`).  Calibration on files whose judge verdict is known:
memory.man 1.3k-7.5k moves at emit 686-2497 (ratio 1.8-3.0) and sort.man
ratio ~1.3 — both PASS, so those ratios are safe; the failing esc decoder
sat at ~10.  Any tick-rich ring design should print this number.

**(5) WHAT IS STILL TRUE FROM THE GATE.**  Include-first DFS gives lex-min
for free (positivity); the four prunes are all necessary conditions so
pruning cannot change the answer; `ceil(r/smax) > n-i` adds nothing; and the
honest residual risk is unchanged and unfixable — `n=20 dense random, no
solution` is 320,404 nodes / 3.29M rotations / ~80M ticks WITH the full
prune set, i.e. hopeless at any K.  That case, and the hidden top-decile
cases like it, fail regardless.  `hcap` buys the near-uniform and
near-total-sum shapes; nothing buys dense random.

## Subset: the machine that should be built (design, worked out, not yet coded)

Handing over a specification rather than a half-written CFG.  Everything here
follows from the entries above; the only missing piece is the cubby.

**Ring layout.**  `M = n+1` groups of K cells, in index order, plus one
SENTINEL group between index n-1 and index 0.  Group i (r-primary, B = r
invariant) is `[suf_i, cap_i, smax_i, smin_i, v_i]`; each of the first four
is one threshold test `(r ring) (s ring) - X`, and B survives all of them, so
a blind rotation of a whole group is 2K ops in one `#:tight` body
(~`2(2K+1)` = 22 ticks/group at K=5).  With the cubby, `smin` also serves as
hcap's divisor and `smax` as its multiplicand, and hcap costs one extra
`smax` duplicate (K=6).

**The sentinel earns its cell twice**: reaching it means "no indices left"
(if r != 0, backtrack), and backtracking INTO it means "search exhausted",
which is the `0` output.  Mark it with `v = 0` — impossible for a real value
since `1 <= v`.

**Decisions do not need to be stored.**  The natural instinct is a 6th cell
per group holding include/exclude (or the sign of the pushed `v`).  It is not
needed: the only consumer is the backtrack, and the backtrack is driven by a
BP counter instead.  Maintain `BP = (M - k) mod M`, k = trailing excludes:
set `BP := 0` after an include, and after an exclude `m` then, if BP is no
longer positive, reload `BP := M-1` from a single digit-arithmetic constant.
The backtrack is then exactly a BP-counted tight rotate — the counter you
need is already the distance you need to travel.

**The include-feasibility test is free.**  Do NOT spend a cell on `v <= r`.
Take the include unconditionally; if `v > r` then r goes negative, and the
`smin` prune at the very next index fires on it (`r < 0 < smin`), and at the
sentinel `r != 0` fails.  One extra node per infeasible include, one cell
saved on every rotation of every node — and K is the dominant term.

**Emit is two laps.**  Lap 1 counts includes into B (B is free once r = 0):
per include `1 + M` — B is the only register that survives ring reads, and
`+`/`M` against a digit is how you increment it.  Then `W` puts k in A for
the MARK emit; lap 2 emits the included values in index order.  ~880 ticks,
negligible.

**Read-in is the O(n^2) part and it is the one place a reversal is needed.**
Suffix aggregates are computed from the END, the ring rotates FORWARD, so
build the groups back-to-front with n laps: after loading the raw values,
lap j carries the last raw value seen in B (one register, free) and expands
it into a group in front of the already-built groups, reading group j+1's
cells to fold `suf' = v+suf`, `smax' = max(v,smax)`, `smin' = min(v,smin)`.
`cap' = suf' - smax'` is the awkward one — it needs two of the new cells at
once, so either order the group `[.., smax, .., cap]` and recompute, or drop
`cap` entirely and use the g-form `maxcap <=> cap < g < smax` at DFS time.
400 index-steps total; irrelevant against 260k.

# Gradebook: the packing works, the room does not — and l1 has a BLOCK CEILING (2026-07-26)

`problems/gradebook.rkt` (spec + 7 public cases + load assertion, VERIFIED),
`problems/gradebook-sol.rkt` (the CFG, **does not lay out**).  Not registered in
`harness/problems.rkt` and not submitted.  Problem id
`d1415447-bf8d-49ef-924e-e024b06a504d`; the problem-set page lists Grade Book
three times but gradebook.md is ONE instance (one constraint block, one set of
7 cases, one Submit section), so one solution covers all three.

## THE FINDING THAT GENERALISES: l1 tops out around 45-50 blocks / 250 ops

`compile-cfg` refused a 95-block / 441-op CFG at **every** width from 24 to 140,
under the shelf packer AND `#:melt`, and with an explicit `#:max-height` of 40
or 60.  The trace is all `wire arm ... failed` / `wire goto ... failed` with no
structural exception, so the CFG is legal and the placer simply runs out of
board.  Bisected on that same CFG (subsets made self-contained by redirecting
out-of-subset arms to a halt block):

| blocks | ops | result |
|---|---|---|
| 32 | ~150 | 27x28 at w=36 |
| 44 | ~200 | 44x31 at w=44 |
| 62 | ~300 | no feasible layout |
| 64 | ~310 | no feasible layout |
| 95 | 441 | no feasible layout |

**~45-50 blocks is a hard design constraint, not a tuning knob**, and nothing
else in the tree comes near it (memory's C is ~17 blocks, sort's 17, tcp's 12 —
which is why this was never hit before).  Two things that do NOT help, both
measured rather than assumed: merging chains to cut rail count (42 chains -> 28,
still infeasible at w=44..80), and raising the board (`#:max-height` is
accepted, and l1's auto height `8 + 2*nops/W` was not the binding constraint).
**Above the ceiling the answer is more ROOMS, and the cheapest extra room is
one you already have.**

## The cheapest extra room is F

The ring already runs `C -> ring-out -> F -> ret -> C`, so **F sees every cell
of every lap for free** and `define-ring-server` already accepts a custom one
via `#:forwarder (list blocks chains tight entry)` — no hand-written l2 world,
unlike a D/C/E pipeline.  So the seam to reach for first is "what work is a
PASS over the ring?", because that work is already happening inside F:

- the two REDUCTIONS (AVG's sum, TOP's max — 24 blocks here) become arms of
  F's relay loop, with C reduced to a rotate plus a bare relay lap;
- the ROSTER TRANSFORM (four K-variants, 18 blocks) also fits in F: the roster
  reaches F through the ring before anything else, and FIFO order makes the
  handover race-free with no protocol at all.

Two consequences worth keeping whoever builds it:

- **A reducing F cannot run the MARK protocol.**  F's relay head needs B=MARK
  for its compare and a reduction needs B for the accumulator.  The fix is to
  make every ring cell `>= 0` with the SENTINEL 0 and every diverted payload
  NEGATIVE: F's head becomes a bare `X` on the value, needing **no register at
  all**, and the relay body is one op (~6 ticks/value against the MARK
  forwarder's 10).  This is sign-divert (SPECULATION 2) taken one step further
  — the marker stops being a value and becomes a SIGN.
- **A transforming F needs tank capacity for the boot burst**: C pushes ~82 raw
  roster values before reading any back, so both tanks need CAP >= ~90 or the
  two rooms deadlock against each other.

## The packing, which is correct and worth reusing

TOP is "max grade in subject s, ties to the SMALLEST id" — two accumulators,
and l3/DESIGN.md 10 already predicted the refusal verbatim (`l3: two values
want the off hand at once: acc and key`).  Collapse them into one word:

    k   = 10000 - id        (id 1000..9999  =>  k in 1..9000, never 0)
    c_s = g_s * 10000 + k   (g 0..100       =>  c in 1..1009000)

`max c` is max grade then max k = min id, so TOP is an ordinary one-register
scan.  **Use 10000, not a power of two**, for three independent reasons:

1. `/ 10000` unpacks BOTH halves in ONE op — quotient is the grade, remainder
   is k — which is GET's whole body and TOP's whole epilogue.
2. The SAME constant computes `k = 10000 - id` (`- N` with B = 10000) and does
   the pack (`*`), so the roster loop holds one B invariant and needs **no
   literal inside the loop** — and a literal in a tight body is a compile error.
3. **A `<< 14` packing would have halted the server.**  Max packed would be
   1,647,400 > MARK = 2^20, and the shared forwarder computes `MARK - v` and
   sends a NEGATIVE result to its `fdead` arm, which is an `H`.  Decimal keeps
   the maximum at 1,009,000, under MARK by 39,576.  **RULE: every value that
   circulates must be strictly below MARK — `ff-blocks` treats "above MARK" as
   "halt", silently.**  Nothing said so before; every previous problem's domain
   was far under 2^20 by luck.

Validated in `scratchpad/gbproto.rkt` against the spec using the machine's own
floored `/`: 7/7 public cases through a packed-key interpreter, a 400-case fuzz
run with 60% of cases drawn from grades 0..2 so ties are the norm, the id and
grade extremes, 16-way all-tied rosters, and 300 random inputs cross-checked
against `gb-spec`.  0 failures.  Grades are `0 <= g <= 100`, so there is no
sign case in AVG at all — floor(mean) is plain `quotient`.

## Ring-shape tricks that survived the layout failure

- **Pad every record to a FIXED 5 cells** (`k g1 g2 g3 g4`, K<4 padded with
  copies of the last cell, which is never addressed).  Fixed width is what makes
  every skip a CONSTANT; with variable width AVG/TOP need a nested loop per
  record and the tight-body rule kills it.  The cost is that the four K variants
  have to live somewhere — 18 blocks, and on this CFG that is what does not fit.
- **Rotate the ring by s at the top of AVG/TOP** so the target cell of every
  record lands at the front of its 5-group; the pass is then ONE uniform tight
  body (`read+accumulate, skip 4`) instead of four unrolled variants.  The
  rotation overshoots the sentinel by s-1 <= 3 cells, so put **three pad cells
  and a second sentinel** behind the first one: the rotated ops stop on S2, the
  unrotated ops stop on S and step over the pads straight-line, and both paths
  consume EXACTLY L cells, so the ring is canonical at every op boundary.  Lap
  accounting is the whole correctness argument for a rotating ring server —
  write it out before writing the CFG.
- **BP = N as a cross-op invariant.**  The op tail reads N and does `b`, so the
  next op starts with the record count already in the backpack.  That forces
  every dispatch to be an X-LADDER over B (`M 1 W -`, then `-`, `-`) instead of
  the cheaper `b m` + `d` ladder, because `b` would eat N.
- **The three-value squeeze in SET** (`v*10000 + k` wants the multiplier and the
  key in B at once) has two ways out, and the second is better: park `v` in the
  backpack and `W` the seek's k back against a fresh B = 10000, counting out
  `+ m` (<= 100 iterations, ~600 ticks); or have the PRODUCER send `v*10000`
  pre-shifted, which turns the whole thing into one `+` against the seek's own
  B = k.  Whenever an upstream room exists, shift there.

# kernel/: the ISA as a function, a kernel search, and three obligation checkers (2026-07-26)

`kernel/isa.rkt`, `kernel/enum.rkt`, `kernel/verify.rkt`, `kernel/README.md`.
A **design-time** layer one level below `harness/estimate.rkt`: estimate says
whether a shape fits the tick budget, kernel says whether the shape EXISTS and
what the op sequence is.  Nothing here builds a grid.  Usage table + the API is
in `kernel/README.md`; PLAYBOOK step 3 is where it belongs in the flow.

## The ISA is now executable, and it is pinned to sim.rkt by construction

`isa.rkt` is ONE table of pure state transformers written against a `backend`
vtable and instantiated **twice**: exact wrapping integers (fast enough for
millions of search steps) and Rosette bitvectors at a **configurable width**.
There is one copy of each effect, so the two backends cannot drift.  State is
`(kst A B BP in sent turn cubby)`; ops are chars, `(lit n)`, or the modeled
cubby pair.

**12,450 differential cases against sim.rkt, 0 mismatches**, and the harness is
mutation-tested (injecting "`%` clobbers B" produced mismatches immediately).
Two purpose-built grids, both `I -> room -> O`:

- **family V** lays the ops on one row ending `s W s H`, so the comparison is
  the whole emitted list — A, B, and every send along the way.
- **family T** puts the man on the middle of thirteen rows with the last op at a
  junction whose three arms each run `s W s <tag> s H`, so ONE run reports A, B
  **and which arm was taken**.
- **BP is read out ONE BIT AT A TIME**: `]`^k then `x` turns cw iff bit k of BP
  is set.  That is CLASSES' "`b` + `]`*k + `d` is a free magnitude test" used as
  an oracle, and unlike counting the backpack out it works for NEGATIVE BP —
  which is exactly where `]`, `m` and `x` would be wrong.

DELIBERATE ABSTRACTIONS, in full (`isa-abstractions`, printed by
`racket kernel/isa.rkt table`): no geometry (no walls/heading/position; op cost
is CELLS, not room ticks); one pipe each way, so `r`=`R`=`U` and `s`=`S`; no
pipe latency and no send blocking; `q` approximate (the only op excluded from
the differential test); one man, no `Y`; literals direction-blind.  Everything
NOT on that list is exact.

- **LANDMINE — Rosette's `merge` is not exported by `(require rosette)`.**  It is
  in `rosette/base/core/merge`, and importing it is what lets a plain
  `#lang racket` module build symbolic terms without switching languages.
  `clear-asserts!` also does not exist; the name is `clear-vc!`.
- **LANDMINE — a Rosette boolean is not `#f`,** so a raw `if` on one silently
  takes the true arm and half the model is quietly wrong.  Every conditional in
  the table goes through the backend's `ite` for this reason alone.
- **SMT is already the machine on three of four sharp edges.**  `bvsmod` takes
  the DIVISOR's sign (that is `%`'s "with B's sign") and `bvashr` sign-fills
  past the width (that is `}`'s "sign-fill if B > 63").  Floored division is
  `(a - smod(a,b)) / b`.  The one edge SMT does not give is B = 0, which the
  machine defines specially.
- **`X` and `> < ^ v` cannot be differential-tested in a one-row lane** — they
  move the man off it, which is a wall crash, not a mismatch.

## Bounded enumeration rediscovers hand kernels in milliseconds

BFS in cell order over the alphabet, carrying every sample state under the
prefix; identical state vectors are interchangeable forever, so the second
prefix is dropped.  That dedup is the whole performance story: **7^8 = 5.7M
sequences collapse to 146k live states.**  Five acceptance targets, all green:

| spec | alphabet | found | states | time |
|---|---|---|---|---|
| sudoku's handle | `~ & \| - + W M s`, <=6 | **`~ s & -`** (4) | 2,290 | 27 ms |
| sign-divert forwarder | `r s + - W M N`, <=4 | **`r + - s`**, X after cell 2 (4) | 420 | 8 ms |
| MARK v2 pass body | `+ - W M N s`, <=4 | **`+ W s`** (3) | 174 | 1 ms |
| subset hcap, registers only | `r + - * N W M`, <=8 | **REFUSED — space exhausted** | 146,311 | 2.6 s |
| subset hcap, + cubby | the above + `s$ r$`, <=8 | `W s$ r * W r$ W -` and `W N s$ r * W r$ +` (8) | 968,165 | 21 s |

All confirmed on a fresh 300-400 state sample; the search runs on a small one
(10-14 states) and re-validates on the big one.

- **The BRANCH POSTCONDITION is what makes the forwarder spec correct, and the
  send-ordering rule is what makes it right.**  Without the branch requirement,
  `r s` (2 ops) satisfies everything else and is WRONG, because sign(v) is 0 for
  address 0 and negative for the -1 sentinel.  With it but without the ordering
  rule, the search returns `r s +` (3 ops) — classifies perfectly, and has
  already relayed the diverted value.  So the enumerator requires the branch
  cell to PRECEDE every send: ops ahead of a branch run on BOTH arms.  That one
  rule is the difference between a plausible answer and the shipped one.
- **REFUSALS ARE THE OTHER HALF OF THE TOOL, and the certificate has an exact
  scope.**  subset's `hcap` needs sign(h*(smax-smin) - rem); `/` hands you h in A
  and rem in B together, and d arrives only through `r ring`, which lands in A
  and destroys h — saving h with `M` destroys rem.  The search EXHAUSTS
  `{r + - * N W M}` to 8 cells and finds nothing.  That is brackets' "three live
  values into two readable registers doesn't go" **checked** rather than argued,
  and it took 2.6 seconds against the afternoon it has cost by hand each time.
  What it proves: nothing in that box works, because the spec fails on a finite
  sample (a necessary condition).  What it does NOT prove: that no LONGER
  sequence works, that no LARGER alphabet works, or that no different DATA
  LAYOUT dissolves the problem.  Widening one of those three IS the design move.
- **SAMPLE SIZE CUTS BOTH WAYS and the asymmetry is the trick.**  A SMALLER
  sample makes a refusal STRONGER (fewer constraints, still nothing works) and a
  discovery WEAKER.  So: small sample for the search, `#:confirm` on a big one.
  A lazy uniform sample is also a trap — a uniform `(h, rem, d)` makes
  `h*d - rem` positive nearly always, and then ONE-OP sequences match by
  accident; the generator has six sign classes for that reason.
- **The modeled cubby is a PRICING TOOL, not an op.**  `(cubby put/get)` stands
  for a second pipe pair looping out of a room and back — the third register
  NOTES prices at a fifth pipe on the controller.  It is a bounded FIFO
  (capacity 2 = a minimum-length loop) and both blocks prune the search.  Its
  answer for hcap: **8 cells**, e.g. `W s$ r * W r$ W -` (park rem in the loop,
  build h*d, swap it out for rem, subtract).  Same bound as the refusal, so the
  comparison is exact: no cubby-free sequence at 8 cells, a cubby sequence AT 8.
  Cost is understated by one cell each — a real cubby is two pipes plus loop
  latency — so read it as "this needs a third register, here is the schedule".

## Three obligation checkers, one tool per obligation

The rule is the SIMPLEST SOUND tool.  A solver where the failure is a
wraparound; integers where it is counting.

**(a) Ring round-trip is a POTENTIAL FUNCTION, not a solver.**  Give each block
`d(b) = pops - pushes`, solve `phi(succ) = phi(b) + d(b)` by BFS from the entry,
and the two real bugs fall out: a cycle with nonzero net (the lap drifts) and a
join reached at two different offsets (one arm pushed back, the other did not —
tcp's realign).  The report names both blocks and the integer, which IS the
length of the fixup rotation you owe.  Gradebook's "lap accounting is the whole
correctness argument for a rotating ring server — write it out before writing
the CFG" is this, mechanised.
- `#:expect` declares the imbalance a protocol has ON PURPOSE.  The MARK
  forwarder drains **2 ring cells per emission** (the marker and the value) and
  that is not a bug; declaring it is what turns a report into a regression, so
  any OTHER imbalance fails.  Deleting `fpass`' `s ret` is caught immediately.
- **`out` is a DRAIN, not a push.**  Put it in neither list or the MARK arm nets
  0 and the accounting lies.

**(b) Sentinel range is Rosette, and the base-4 regression FIRES.**
`check-stack-roundtrip` at the spec maximum depth 32 returns a 32-digit witness
leaving the emptied stack reading **-1, not 0** — NOTES' measured failure,
proved.  `check-encoding-range` is the cheaper CAUSE check: run the push chain
at width w and again at width 2w (the wide run is exact) and ask whether they
can disagree.  Use it whenever `pop` involves a division — 32 symbolic divisions
is a different order of solver cost from 32 shifts.
- **It also confirms the base-3 margin exactly.**  Bijective base 3 is PROVED in
  range at depth 32 and at depth **39**, and VIOLATED at **40** (witness digits
  printed).  NOTES measured "correct through depth 39, wrong from 40" on the
  shipped grid; that is now a proof rather than a sample, and it took 1 second.
- `push`/`pop` are written against the isa backend, so they are the MACHINE's
  arithmetic, not Racket's.  Digits are a contiguous range so the digit
  constraint is two inequalities instead of a disjunction.

**(c) Protocol preconditions are INTERVAL ARITHMETIC — except the XOR.**  Four
monotone obligations (pass-positive, divert-negative, zero-unreachable so `X`'s
straight arm is dead, no-overflow), all discharged for sign-divert on memory's
domain with margin **1,097,152** on each side.  Porting the same protocol to a
domain with |v| <= 4e6 is caught on three of the four.
- **FINDING: `smallest-offset` says 2^21 already discharges all four**, where
  NOTES says "for a bound of 1e6 the smallest usable K is 2^22".  The shipped
  choice therefore carries one extra doubling of margin.  Not a bug — but if
  anyone is hunting a cheaper constant to build (the `` `21` `` `M` `1` `{` `M`
  trick), 2^20 as the guard is provably enough for this domain.
- **Flush safety is the one part intervals cannot do.**  The flush compare is
  `addr XOR B`, and XOR is not monotone, so it goes to the solver: B = 2^22
  collides with no address in [0,99] and `-1 XOR B` stays negative.  B = 50
  is caught with the witness "address 50 XOR B = 0".

## Honest negatives and residual risk

- **`q` is not differential-tested** and is the only op that is not.  The model
  returns the modeled queue length; the machine returns how many values happen
  to be sitting in the pipe, which is pipe-length and producer-rate dependent.
  A kernel that uses `q` is unverified by this layer.
- **Op cost is CELLS.**  The enumerator ranks by cells, which is ticks only in a
  straight lane.  NOTES has measured repeatedly that rails between chains, not
  op count, are the tick budget, so a 4-cell winner is not automatically faster
  in a room than a 5-cell one laid better.  Use `harness/estimate.rkt` for that.
- **No geometry means no feasibility.**  A sequence the enumerator returns can
  still be unlayable (a tight body may hold no backtick literal; a chain
  straddling a column band may not fit at any width).  kernel answers "does the
  register choreography exist", l1/l2 answer "can it be drawn".
- **The refusal bound is 8 cells over 7 ops.**  Depth 9 over the same alphabet is
  ~7x the states and was not run; depth 8 over an alphabet including `/ % & | ~`
  was not run either (9 ops at depth 8 is ~7x again).  Both are affordable if
  someone wants a stronger certificate; the numbers above are the extrapolation
  base.

# Bundle A: the chain PARTITION and chain ORDER as search dimensions (2026-07-26)

`l3/RESULTS.md` measured the same knob with both signs — the greedy chain
partition cost brackets **+4.3% ticks** and GAINED reverse **-11.8%** — and
concluded "it belongs in the L2 search as a movable".  It does, and it is now
enumerable.  Machinery is in **l1.rkt and l2.rkt only**; every default is
unchanged, `driver verify all` is green with every repro check byte-identical,
and `l3/test-compile.rkt` still exits 0.  The rig is
`scratchpad/partition/lab.rkt`.  **Nothing below is baked.**

## A partition IS a choice of fall-through links, and that is the whole space

`chain-partitions blocks chains tight entry` enumerates it.  The observation
that makes the space small and total:

- a block ending `(x lz _ _)` or `(d ls _)` has a **FORCED** successor —
  `rail-edges` rejects every other partition ("x zero-arm of ~a must be its
  fall-through"), and a tight head is the same case;
- a block ending `(goto L)` has an **OPTIONAL** link to L: with the link the
  goto is a free fall-through, without it the goto is a rail and the chain
  SPLITS there.  Both directions of the knob are one bit — dropping a baseline
  link is a split, adding one MERGES the target's chain onto this one;
- `(halt)`, and a goto into a tight BODY, link to nothing (a body is not a
  chain member at all; `chain-flow` lays it inside its head's circuit).

So the space is the subsets of the optional links that form disjoint paths (a
block with two predecessors would be laid twice) and no cycle (a chain is a
list, so it needs a head).  Candidates come out by ascending EDIT DISTANCE from
the caller's own partition, so index 0 is the caller's list *itself* and the low
indices are the small perturbations — the shape-menu ordering rule ("+-1 must be
a real step, not a plateau") one level up.

**Legality is l1's own front end, not a second copy of it.**  A candidate is
validated by running `make-ctx` and `chain-flow` over every chain — entry heads
a chain, the tight rules, the backtick rules, `rail-edges`' fall-through rules —
with no routing at all, plus ONE rule that is otherwise only discovered as a
width sweep that never succeeds:

> **BAND FEASIBILITY.**  With a `#:col-order`, a chain that reads the WEST
> channel *after* the EAST one satisfies the column split at no width and no
> placement, because both ops sit on one lane in lane order.  `chain-bands`
> already computes those two offsets, so the rule is `woff < eoff`.

That rule is load-bearing, not decoration: on reverse it is what refuses to
merge `fillgo` into `passh` (an `r in` would then precede an `r ring` on one
lane) — the same refusal l3 spells `#:band-channels` and materialises as
`fillgo`, and the same lesson as "one late `r ring` op can cost the whole room".

Counts at `#:max-edits 2`: reverse C **11**, sort C 16, memory C 22, tcp C 34,
brackets D 8, brackets C 3, and 2 for every shared forwarder.  Dozens, as
intended.  `chain-partitions` RAISES when the caller's OWN partition is
illegal, because otherwise a wrong `#:entry` silently reports "this CFG has no
alternatives" — which is exactly what a typo'd entry looks like.

## CHAIN ORDER is a second knob, and on reverse it is the BIGGER one

`attempt-shelf` sorts the tall (tight) chains by width and packs the flat ones
in `wide`/`narrow`/**`given`** order — and Racket's `sort` is stable, so the
caller's list order breaks every tie in all three modes as well as being the
whole ordering in `given`.  `chain-order-variants` offers the local
neighbourhood — adjacent transpositions, move-to-front, move-to-back, reverse:
**3n-1** orders instead of n! — and `chain-partitions #:orders 'basic` appends
them AFTER the whole partition list, so `#:limit` truncates the order dimension
rather than the partition one.

Screened on the static estimate at the same room:

| room | baseline best est | best order variant | min max-dim |
|---|---|---|---|
| memory C | 2828 | **2496** (-11.7%) | 22 -> 22 |
| tcp C | 3291 | **2950** (-10.4%) | 25 -> 25 |
| reverse C | 1213 | **1099** (-9.4%) | 21 -> 21 |
| sort C | 3141 | **2991** (-4.8%) | 25 -> **23** |
| brackets C, D | 3206 / 106 | no change at all | — |

Brackets is where the knob is worth exactly nothing, and the reason is the one
that makes it worth something elsewhere: with five short chains the packer has
no ties to break.  **And the est screen is not the verdict** — see the landmine
below: memory's -11.7% est variant simulated to the shipped world exactly,
while reverse's -9.4% one is the best candidate in this whole pass.

## The two menus, and the HOOK that sweeps an EXISTING builder

- **l2 `build-partition-menu`** is the shape-menu pattern one level up: sweep
  the dimension, compile, **dedupe by the compiled ROOM** at a few probe widths,
  keep a small stably ordered vector, hand the search an `'int` movable.  Cells
  are in the fingerprint, not just dimensions — NOTES' "dimensions are not a
  fingerprint", here in the cheap direction, since collapsing two different
  rooms that share a bounding box would silently delete a candidate.  Each entry
  carries its shape menu as a PROMISE, so a 12-entry menu over a 32-width sweep
  costs only the indices the search visits.
- **l1 `current-chain-partition`** is a parameter, `#f` by default, applied
  BEFORE the memo key — so with no hook `compile-cfg` is bit-for-bit the
  function it was, and with one, every compile in the process is re-partitioned,
  including the ones inside a shape menu a template already built.  That is what
  let this pass sweep all five shipped problems **without editing a single sol
  file or harness/templates.rkt**.
  **Verified rather than argued**: `compile-cfg blocks P` and
  `compile-cfg blocks chains` under the hook produce identical cells, pipe-ops
  and tick estimates at all 17 feasible widths of reverse C's partition 3.  So
  A BAKE IS LITERALLY "REPLACE THE CHAINS LIST" — the hook is a measurement
  device, never a shipping mechanism, exactly as with a tank former ("the former
  is part of the bake").  `grep -n chains harness/templates.rkt` confirms the
  other half: `chains` reaches `compile-cfg` and nothing else.
- **One process per candidate, on purpose.**  A template's shape menu is a
  `delay` forced on the first build, so a second partition in the same process
  would silently reuse the first one's rooms.

## Validation: both of l3/RESULTS' cases reproduce

**reverse — the search finds l3's partition from the HAND CFG.**  Index [2] is
`(passc roth emitgo)` merged, which is exactly the five-chain partition l3's
greedy heuristic produced (RESULTS §3), and it is reachable from the hand CFG by
one merge.  Measured end to end, 8/8 public: **33x23 @ 1820.8 = -12.6% ticks**
against the shipped 27x26 @ 2084.25, where l3 reported -11.8%.  Area went the
other way, as RESULTS said it does.  The mechanism reproduces from the opposite
direction: it was never the compiler, it was the partition.

**brackets — the +4.3% is not merely undone.**  On the L3-GENERATED brackets CFG
(the one that pays +4.3%), partition [5] — four chains where the greedy gave six
— builds **24x27 @ 594.3 = 433,269**: -20% against the l3 world's 25x29 @ 644.2
= 541,791, and **-3.7% on ticks AND score against the shipped HAND solution's
27x25 @ 617.4 = 450,117**.  A generated room with a searched partition beats the
hand-written one.  (Measured against `l3/compile.rkt` as of this afternoon; that
file was being edited concurrently and the generated CFG has since changed, so
re-derive before acting on it.)  On the SHIPPED brackets CFG the hand partition
is already optimal — the best alternative is score-neutral (27x27 @ 617.4, the
extra rows land on the free short side) and every other one is worse.  Both
halves are the same finding.

## Candidates (measured, NOT baked)

Full public suite each, judge-exact sim, tick cap 1.5x the shipped worst emit,
rescue scan then bounded gravity (8-24 rounds) from the rescue point.  These are
**upper bounds on the score**: the shipped rows are fully converged optima and
the candidates got a cold start.

| problem | knob | world | avg ticks | score | vs shipped |
|---|---|---|---|---|---|
| tcp | partition [6] `(r1e rh rdone)` merged | 30x30 | 3968.5 | **3,571,650** | **-16.9%** |
| reverse | ORDER only: the chain list REVERSED | 27x25 | 1927.5 | **1,405,148** | **-7.5%** |
| sort | partition [1]: split `(boot)(rstart)` | 26x28 | 3484.9 | **2,732,128** | **-1.4%** |
| memory | partition [6] `(write-mb flush dead)` | 34x33 | 11841.0 | **13,688,196** | **-0.5%** |
| brackets | — | — | — | — | hand partition already optimal |

Bake instructions, per the maintenance lesson (never hand-sum a base):

    ;; tcp    problems/tcp-sol.rkt, c-chains: merge r1e's goto into rh's chain
    (build-tcp-grid #:deltas (hash 'I '(3 . 0) 'O '(-2 . 0) 'cshape -1))
    ;; reverse  problems/reverse-sol.rkt: r-chains reversed, CFG untouched
    (build-reverse-grid #:deltas (hash 'F '(2 . 0) 'I '(0 . -2) 'O '(-1 . 0)
                                       'band 1 'cshape -2))
    ;; sort   problems/sort-sol.rkt, s-chains: (boot rstart) -> (boot) (rstart)
    (build-sort-grid #:deltas (hash 'F '(1 . -2) 'I '(-2 . -1) 'O '(0 . 2)
                                    'band 1))
    ;; memory problems/memory-sol.rkt, c-chains: (write-mb) -> (write-mb flush dead)
    ;;        and drop the now-merged (flush dead) chain
    (build-memory-grid #:deltas (hash 'O '(-2 . 0) 'cshape 1))

Edit the chains list, pass the deltas as OFFSETS through the builder, confirm
the world, and only then fold them into BASE-DELTAS with `merge-deltas` and
re-run `verify` — the repro check is on BYTES, and dimensions are not a
fingerprint.

## Landmines

- **A new partition makes the baked deltas INFEASIBLE, not merely suboptimal.**
  RESULTS said this of generated rooms; it is just as true one merge away from a
  hand-written one.  Measured on reverse's five-chain partition: EVERY
  band x cshape within +-3 fails (overlapping boxes, then "no sweep works"), and
  the nearest feasible world sits at a different band entirely.  **So a
  partition index cannot simply be dropped into `gravity-optimize` beside
  `cshape`** — a unit step in it lands outside the feasible region and the search
  parks on round 0.  It needs the combo sweep's RESCUE SCAN (band-major, one room
  offset at a time) to find a starting point first, and that is why the rig
  scans before it climbs.
- **`menu-ref` CLAMPS, and a partition changes the menu's LENGTH.**  A baked
  `cshape 2` indexes a different room under a partition whose front shrank to
  four shapes — or the widest one on the front.  Any joint sweep must sweep the
  SHAPE INDEX too; the rescue scan here does, which is the "partition x shape
  jointly" half of the combo sweep.
- **The static `ticks` estimate is a good SCREEN and a bad PREDICTOR.**  It is
  reliable on direction (reverse [2]: est -38%, measured -12.6%) and it found
  every candidate in the table for the price of one menu build each.  It is not
  a ranking: memory C's best order variant is -11.7% est and simulates to the
  shipped world EXACTLY, and tcp's best combined partition+order candidate is
  -22% est and scores WORSE than the partition alone.  Use est to choose what to
  simulate, never to rank a final candidate.
- **A LITERAL can be the room's width floor, and no search moves it.**
  `chain-width-floors blocks chains tight entry` reports it: memory C's widest
  chain is `notfound` at 17 tokens of which **9 are one backtick literal** in
  `read-nf` (and `read-m-b` is 16 with a 9-cell literal).  `nobend` forbids an
  arrow between backticks, so a literal cannot be folded by any width budget —
  the fix is one level up, in how the constant is MATERIALIZED (digit arithmetic
  or the `` `21` `` `M` `1` `{` `M` shift trick), which is l3's
  `materialize-const` and the caller's business.  Worth checking before a sweep
  spends an hour proving a room cannot be narrower.
- **The two dimensions do NOT compose additively.**  Screened and simulated on
  both winners: tcp's best partition plus its best order is 3,588,900 against
  3,571,650 for the partition alone, and reverse's best partition plus the
  reversed order is 1,484,062 against 1,405,148 for the order alone.  Each is a
  real gradient; their sum is not.  Sweep them jointly or accept the better
  single one — do not stack the two winners and assume.

## Display probes ADJUDICATED (editor run, 2026-07-27)

d1 = white pixel: DATA before SWAP within the tick — sim model CONFIRMED
(no spare tick before commits). d4 = blacks out: SWAP always commits even
with untouched NEXT — CONFIRMED (avoid stray SWAPs). d6 = pixel landed
(purple — the probe writes DATA 5; the probe doc's "white" is a typo):
post-halt flush COVERS displays — CONFIRMED, H stays free on display
problems. All three match sim.rkt as built; display verification stack is
sound. Remaining open: d5 (idle O room) — adjudicated by first plotter
submission; d7/d8 optional. Pathfinder trail question: editor eyeball
confirms NO TRAIL (spec agents' A1 verdict).

# The first DISPLAY problem arrived: plotter (spec phase only, 2026-07-26)

`plotter.md` (id `0c3e3d4d-2901-45f1-81cf-5704d49c9139`, Semester 2,
footprint-tick) is the **first display-judged problem published to us**, so
CLASSES.md's "DISPLAY — infrastructure ready, no problem yet" and this file's
"no display problem has been published" are now out of date on that one point.
`problems/plotter.rkt` is the spec + all six public cases; nothing is
registered in `harness/problems.rkt`, no world, no submission.

## The md answers three of the four things we assumed we would have to probe

Worth recording because the DISPLAY class's open-question list reads as if
every display problem will be a semantics fight, and this one is not:

- **Colour is stated**: "in **bright white (color 15)**; every other pixel
  stays black."  No probe.
- **Persistence is stated**: "Lines do not persist between rounds."  Frame K
  is round K's segment alone.
- **Frames per round is stated twice**: "Each round expects a single frame"
  and "Commit the segment only when it is finished."
- Which settles **SWAP mode as a derived choice, not an open one**: SWAP 0
  (NEXT->CURRENT, clear NEXT, home cursor) delivers non-persistence and a
  cursor home for free; SWAP 1 would carry the previous round's <= 32 lit
  pixels into the next frame and fail the streaming compare unless the
  solution hand-erases them.  **Accumulating rounds want SWAP 1; these rounds
  explicitly do not accumulate.**  Round gating is about when INPUT arrives,
  not about what the buffer holds — the two are easy to conflate.

What the md does NOT answer is the list we already had: d1 (same-tick DATA in
the frame), d4 (empty SWAP commits), d5 (idle O room), d6 (post-halt flush),
and O2 round gating.  All five are solution-side; none changes a frame's
content.

## The pictures did not extract, so the generator is the ground truth

Every "screen:" image in the md is absent from the text.  That removes the
playbook's step-1 safety net — there is no published output to assert the
spec against — so `problems/plotter.rkt` replaces it with a golden property
battery plus an **independent closed-form reference**, both asserted at load
(0.29s, whole file).  This is the shape to reuse on any future display problem
whose expected frames are pictures.

## Closed form for the md's symmetric-error Bresenham, and the equivalence

Derived and then checked EXHAUSTIVELY: all 32*24*32*24 = **589,824 endpoint
pairs in the box agree, 0 mismatches**, between the md's incremental
pseudocode and this non-incremental form (exact rationals, no accumulator).
Writing it down because it is the cheap way to cross-check any future
line/raster problem, and because deriving it twice is wasted work:

With `D = |dx|`, `E = |dy|`, `sx`, `sy` as in the pseudocode —

- `D = E = 0`: the single pixel `(x0,y0)`.
- `D >= E` (x-major): x steps EVERY iteration, and for `k = 0..D` the point is
  `(x0 + sx*k, y0 + sy*m_k)` with `m_k = floor((2Ek - D) / (2D)) + 1`.
- `E > D` (y-major): the same algebra with D and E swapped — y steps every
  iteration and `n_k = floor((2Dk - E) / (2E)) + 1`.

Two consequences that make good assertions: the point count is **exactly
max(D,E)+1** (x and y arrive at their targets on the same iteration, since
`m_D = floor(E - 1/2) + 1 = E`), and A->B is the point reflection of B->A
through the segment midpoint.  That reflection is the tightest statement of
what "direction-sensitive" means here — the md's "both ways" example
(0,0)->(8,4) picks `(1,1)`, the reverse picks `(1,0)`, and the two sets map
onto each other under `(x,y) -> (8-x, 4-y)`.

**A tempting golden that is FALSE**: "the 8 rays of the octant fan leave the
centre in 8 distinct directions".  A shallow ray holds its row for two pixels,
so (15,11)->(29,16) and (15,11)->(29,6) share the prefix (15,11),(16,11).
Mirrored shallow rays share a prefix; assert distinct SETS, not distinct
second pixels.

## Sizing, for whoever builds the world

32x24 = 768 pixels per frame but at most **max(dx,dy)+1 = 32 lit**, and at
most 20 rounds, so the whole worst case is <= 640 lit pixels and 20 SWAPs.
Painting only the lit pixels (ADDR per pixel) is ~2 display writes per pixel
against 768 DATA writes per frame for painting the full field — a 20x gap at
the spec maximum, and it is the first design call to make.

# Snake: the second DISPLAY problem, and ROUND COUNTS as the missing safety net (spec phase only, 2026-07-26)

`snake.md` (id `15982f19-7465-4902-b7ef-c592e2b0150b`, Semester 4,
footprint-tick, 15M tick cap) is the **second display-judged problem**, after
plotter.  `problems/snake.rkt` is the spec + all five public inputs + the
validation battery; nothing registered in `harness/problems.rkt`, no world, no
submission.  16x16 display, so a row in `display-problems` would be
`'snake (hash 'res (cons 16 16))`.

## It is the ACCUMULATING display problem, which is the opposite of plotter

Plotter's md says "lines do not persist between rounds", which made SWAP 0 the
derived choice.  Snake persists by construction: consecutive frames differ by
**2-3 pixels** (erase the tail, paint the head, and on a fruit tick erase the
fruit), against 256 pixels for a full field.  So snake is the SWAP 1 case the
plotter note predicted would exist, and the choice now depends on open display
questions d1 (same-tick DATA visible in this tick's frame) and d3 (SWAP 1
cursor/buffer preservation) in a way plotter's did not.  Worst case is 100
frames, so full-redraw is 25600 DATA writes against roughly 300 for the diff.

## The pictures did not extract here either — but the ROUND COUNTS do

Same hole as plotter (the md's frames are images), same replacement (property
battery + an independent second engine), plus one thing plotter did not have
and that is worth reusing: **the md marks direction-change rounds "no output"
and states "each round expects a single frame", so `frames = rounds - direction
changes` is a published, checkable number for every case.**  The ledger:

    first bites 13/2/11 · wall 5/0/5 · full circle 23/7/16 ·
    second course 22/5/17 · long game 92/12/80

That arithmetic is not just a transcription checksum — it **settles semantics**.
"game over at the wall" is 5 rounds, 0 direction changes, and its 5 frames are:
start (12,3) and ticks to (13,3), (14,3), (15,3), then a 4th tick off the east
edge.  Those five frames exist only if **round 1 commits a frame AND the losing
tick commits a frame**.  Two would-be probes answered by counting.  On any
display problem where the pictures do not extract, count the rounds against the
"no output" markers before assuming anything is a probe.

## What the counts CANNOT settle, and the one no public case can

Parameterized in `problems/snake.rkt`, each with a probe plan in the file:

- `snake-red-on-loss-frame?` — is the snake red on the loss frame itself, or is
  that frame still the ongoing (green) pre-tick picture?  Under #f the md's
  "if the game has ended, draw the snake in red" is dead text, since the loss
  frame is the only frame that can ever be drawn after the end.  Default #t.
- `snake-fruit-persists?` — an uneaten fruit on every frame, or only on its
  spawn frame?  Default #t, and it is load-bearing on public cases ("second
  course" ends with an uneaten fruit alive across 4 frames).
- `snake-fruit-on-loss-frame?` — **no public case can settle this one, even in
  principle**: the wall case never spawns a fruit, and "full circle" eats its
  last fruit six rounds before the self-collision.  Pure hidden-case exposure.
  Note the two readings disagree only about whether that pixel is LIT — its
  colour is 9 either way, since fruit red and dead-snake red are the same 9.
- `snake-loss-commits-frame?` — pinned #t by the count above; the flag exists
  so a grader contradiction is a one-parameter rebuild.

## Three rules a snake solution gets wrong, all confirmed by the publics

- **The collision test excludes the TAIL** on a non-growing tick ("the tail
  moves before the head; moving to where the tail just was is legal").  "full
  circle" exercises it TWICE, rounds 13 and 15, and then dies at round 23 by
  moving into body index 3 while the tail sits elsewhere.  A whole-body test
  fails that case at frame 10 of 16.
- **A direction change need not be a turn.**  "first bites" round 4 sends `3`
  (right) while already moving right, and still commits no frame.
- **Two consecutive frames can be geometrically identical and differ only in
  colour** — the wall case's frames 4 and 5.  A diff-based drawing loop still
  has to repaint that pixel.

## The two-engine crosscheck, and a generator bug that impersonated a spec bug

The spec folds a head-first cell list; the checker is a **countdown grid** (each
cell holds the ticks it stays occupied, all cells decrement on a non-growing
tick, the head is stamped with the current length, growth = skip the decrement
and stamp length+1).  No explicit tail in the second engine, so a tail-handling
mistake cannot be mirrored.  Asserted equal frame-for-frame on the publics under
all 16 combinations of the four flags, and on 200 fuzz games under two of them;
whole file loads in 0.4s.

Landmine, and it cost the only red in the session: the fuzz generator drew
`(list-ref opts (random ...))` **twice** — once for its own state, once for the
round it emitted — so it generated games that turned one way and told the input
they turned the other.  The symptom was the SPEC raising "N rounds after a
loss", which reads exactly like a transcription error in a 92-round public case.
When a generator and a spec disagree, suspect the generator's own bookkeeping
before re-reading the transcription.

# Pathfinder: the third DISPLAY problem — the image NUMBERING is the frame count (spec phase only, 2026-07-26)

`problems/pathfinder.rkt` only (id c778ba35-4918-415b-83d0-37dc8f6f68c9, 16x16
display, tick cap 15M).  No solution, no world, nothing submitted.

## The pictures did not extract here either, but the md NUMBERS them

Third time, third replacement.  Plotter had nothing; snake had
`frames = rounds - direction changes`; pathfinder has the strongest form yet:
each round's screens are rendered as a **numbered image list**, so the last
number IS that round's frame count, and a round with a single screen carries no
number at all.  31 rounds across the 7 cases, extracted mechanically:

    straight shot 1/9/12/1 · pillars 1/9/10/17 · long way 1/49/40 ·
    rooms and doors 1/10/12/17/17 · cluttered field 1/10/12/13/9 ·
    running errands 1/10/9/13/8/7/9 · there and back 1/35/42

The spec reproduces all 31 exactly.  That kills three rival frame accountings
(no setup frame, a pre-move frame per round, one frame per round) and confirms
the whole BFS half of the problem on seven real mazes.

**But read what k is: a DISTANCE.** Every reading of the tie-break, and every
reading of the trail question, produces the SAME 31 numbers.  Snake's count
ledger settled semantics; pathfinder's settles arithmetic and nothing else.  A
machine that walks the wrong shortest route or paints a trail passes all 31
counts and still scores zero, because a streaming frame compare fails at the
first wrong pixel.  When you replace missing pictures with a published count,
ask which quantity the count is a function of before believing it is a probe.

## The colour list is the exhaustive draw list

The title says "draw the robot's path on a display", which reads like a trail
behind the robot.  It is not, and the argument generalises: **the Output
paragraph's colour list enumerates everything that gets drawn**, and there is
no colour for a trail (path 0, wall 7, flag 9, robot 10).  "Paths in colour 0"
is the board's `path` CELL TYPE from the first paragraph, i.e. the background —
snake.md fills the identical slot with "other cells should be left black
(color 0)".  The title describes the ANIMATION: one frame per move IS how the
path gets drawn, and that is why the problem demands a frame per move instead
of a frame per round.  Parameterised anyway (`pf-trail-mode`), because the
cheapest disproof is one picture: a k=1 round ("a straight shot" round 4) has
exactly one colour-10 cell under the no-trail reading and exactly two under a
per-round trail.

## A genuine fork in "prefer up, then right, then down, then left"

The reading taken: at each step, among neighbours whose distance-to-flag is one
less, take the first in preference order — BFS from the FLAG, then greedy
descent, which is exactly the lex-smallest shortest path in the alphabet
up<right<down<left (per-step greedy and global lex-min coincide; there is no
third reading between them).  The surviving alternative applies the same
preference while building the path BACKWARDS from the flag, and it is not
academic: **the two disagree on 4 of the 7 public cases**, starting at the very
first frame of "around the pillars" round 2 — forward puts the robot at (2,3),
backward at (3,4).  One glance at one published picture settles it.  Minimal
witness for a bug report: a 2x2 open square, robot (1,2), flag (2,1); forward
goes up-then-right, backward right-then-up.

`problems/pathfinder.rkt` asserts that census at load, so it cannot drift
silently, and carries a per-ambiguity probe plan.  Everything in the file is
parameterised; a probe answer is a one-line default change.

## Pathfinder ambiguities ADJUDICATED (editor screenshots, PIL-decoded)

Setup frame + round-2 first frame of "around the pillars" extracted
pixel-exact (194px = 1px border + 16x12px cells; decode script pattern in
session log). Robot start (2,4) and flag (8,1) match the transcription
cell-for-cell — extraction pipeline validated. Round 2 first frame robot
at (2,3): pf-tiebreak = FORWARD confirmed (BFS-from-flag greedy descent,
the spec default). pf-trail-mode 'none previously eyeball-confirmed. All
pathfinder spec params now judge-anchored except pf-flag-on-intermediate?
(A3, low risk, spec-derived).

# Subset: the design doc's BACKTRACK COUNTER IS WRONG, and what replaces it (2026-07-26)

Follow-up to "Subset: the machine that should be built (design, worked out,
not yet coded)" above.  I was sent to CODE that design.  It does not work, and
the failure is in the one mechanism the design calls free.  **Still no
solution file** — but the mechanism below is verified against the spec and
measured, so the next agent is coding, not deriving.

**(1) `BP = (M-k) mod M` CANNOT DRIVE THE BACKTRACK.**  The design says
"decisions do not need to be stored ... the backtrack is driven by a BP
counter instead ... the counter you need is already the distance you need to
travel."  The counter is right at the moment it is set and wrong immediately
after it is used.  A backtrack lands at `p+1` with `p` newly EXCLUDED, so the
next counter must be `M - k'` with `k' = 1 + (trailing excludes BEFORE p)` —
i.e. it depends on `p'`, the second-deepest include, which no local update of
BP can know.  n=4, M=5, path I,E,I: at j=3, BP=0, the backtrack correctly
rotates a full lap to p=2; the next backtrack needs BP=3, every local rule
gives 4, and the machine restores `v_1` — never included — into r.

Measured rather than argued (`scratchpad/ss-btproto-a11.rkt`, the design's
exact control flow at group-rotation level, checked against `subset-lexmin`):

| backtrack scheme | disagrees with the spec |
|---|---|
| the design's BP rule | **141 / 300** |
| stack oracle | 0 / 300 |
| mark-scan (below) | 0 / 300 |

The root cause generalises past this problem and belongs beside the
"hcap is not implementable with two registers" entry: **BP is write-only in
the arithmetic sense, so it cannot be PUSHED.**  The deepest include is stack
state.  Any design that stores path state in BP is storing one frame and
calling it a stack.

**(2) THE REPLACEMENT: a mark-scan backtrack, one counter live at a time.**
Mark an include by the SIGN of its `v` cell (`v >= 1` always, so the sign is
free and `N` recovers it on unmark).  The sentinel's `v = 0` is a free
landmark.  A backtrack is then three phases:

- **A** — rotate to the sentinel, blind.  Indices ahead of the frontier are
  undecided, hence unmarked, so nothing is missed.
- **B** — ONE scan lap.  `X` on each `v` cell is a genuine three-way:
  positive -> `m`; negative (a mark) -> reload BP := C; zero -> the sentinel
  again, exit.  Seed the lap by treating the sentinel itself as a mark.
- **C** — rotate BP groups; the last group IS `p`; read `v_p`, restore
  `r += v_p`, unmark with `N`, land on `p+1`.  **BP = 0 out of phase B means
  the search is exhausted** — the sentinel was the last "mark" — which is the
  design's sentinel dual role, kept intact.

The reset constant is `C = L`, the sentinel's ring position (`M-1`).  Derive
it by counting: after the last mark at p, phase B decrements once per group
p+1..L-1, so BP = C - (L-1-p), and phase C must rotate p+1, giving C = L.

**(3) C IS A RUNTIME VALUE, AND THERE ARE EXACTLY TWO WAYS TO PAY FOR IT.**
- **Pad the ring to a fixed M=21** with always-prune groups
  (`suf=0, cap=0, smax=0, v=1`: `under` fires for every r>0, `v=1` is neither
  a mark nor the sentinel).  C becomes the literal 20.  Free at n=20, where
  the cap actually binds; ~1.9x rotations at n=10, where nothing binds.
  Pads must be inserted AFTER the suffix fold or they poison `suf`.
- **A 6th cell per group holding +C when excluded and -C when included** —
  its own mark and its own constant, `N` flips it either way, no external
  literal and no padding machinery, +20% ticks.

Padding is the better buy for exactly the reason the cap binds at n=20.

**(4) IT STILL PASSES 6/7 PUBLIC — the fix does not change the verdict, only
the margin.**  Est ticks against the stated 15,000,000 cap, K=5
{under,smin,maxcap}, tick model `2(2K+1)`/rotation + 25/node:

| case | oracle (the design's intended cost) | mark-scan |
|---|---|---|
| near-total-sum, 20 values | **19,907,253 OVER** | **37,014,453 OVER** |
| no solution (n=14) | 379,975 | 687,975 |
| tiny warm up | 7,331 | 12,611 |
| last-index-required | 3,963 | 6,867 |
| the other three | < 100 | < 100 |

The oracle column reproduces the 19.6M this file already records for that
case, which is what calibrates the model.  The correct backtrack costs
**1.86x** and the SAME single public case fails.  Hidden-set proxy, 200
random in-box cases inside the cap: **oracle 193/200, mark-scan 178/200** —
the fix costs ~7% of the hidden set, not the problem.

**(5) HONEST NEGATIVES, each with its number.**
- *under-only, K=2* is tempting because `suf` needs only ONE forward lap
  (`acc := S` then `suf_i := acc; acc -= v_i`) instead of the O(n^2) backward
  fold, and it is a wash on random cases (177/200).  It is not shippable:
  the big-element trap costs **482,344,935** against K=5's 927, and that
  shape is PUBLIC TEST 5 at the spec maximum.  `maxcap` stays mandatory, as
  this file already said; the read-in fold cannot be dodged.
- *no-backtrack greedy, K=1* is a genuinely small machine (no tables, no
  fold, ring = n+1 cells) and provably never emits a WRONG answer — the first
  DFS path is lex-min, so reaching r=0 greedily is correct, and otherwise it
  blocks.  It passes public 2/4/6.  It scores **0/200** on the hidden proxy,
  so it very likely misses the ">= 1 private case" eligibility bar and is not
  worth a submission slot.
- *restart-lap with marks* was re-costed now that the rotation model is
  right: 2 laps per pruned node, ~4x the oracle, worse than mark-scan.  The
  earlier "~6x worse" verdict survives the model correction.

**(6) WHAT IS STILL UNRESOLVED AND SHOULD BE MEASURED FIRST.** Point (4) of
the previous entry — that the judge's cap may charge PIPE-VALUE MOVEMENT
rather than ticks — is untouched by any of this, and a mark-scan machine has
a ~110-cell ring (21 groups x 5) that makes it worse, not better.  Build to
ticks, but print `sim-pipe-moves` on the first grid that runs, before tuning
anything: if the ratio sits near 10 rather than the 1.3-3.0 of the passing
files, no ring DFS fits this problem and the mechanism above is the wrong
thing to have optimised.

# Codifying four field-proven idioms into the reusable layers (2026-07-26)

`idioms.rkt`, `l3/compile.rkt` (one feature), `kernel/isa.rkt` + `kernel/enum.rkt`,
`harness/fragments.rkt`.  Nothing here is a new judgment about the machine —
each item is a shape that had already shipped by hand and was being re-derived
at every next use site.  Every edit is gated on byte-identical repro of the
shipped `.man` files.

## `define-emission-protocol`: the precondition is now DISCHARGED, not remembered

A declared protocol is five things — name, `encode` ops (controller side),
`decoder`/forwarder blocks in named VARIANTS, the register `invariant` as one
string, and the `domain` AS BOUNDS — and the fifth is the point.  The macro
hands the declared bounds to `kernel/verify.rkt`'s `check-offset-protocol` AT
INSTANTIATION and raises `DOMAIN PRECONDITION VIOLATED` naming the obligation
and the witness.  Declaring a protocol you have not checked is now more work
than declaring one you have.

Three instantiations, all shipped shapes: `mark-protocol` (variants `east` =
`ff-blocks`, `corner` = `ff-blocks/corner`), `mark/corner-protocol` (the same,
defaulting to the corner — the 2-D attachment split is a floorplan commitment a
caller names once), and `sign-divert-protocol` (blocks transcribed from
`problems/memory-signdivert-sol.rkt`).  **The sol file is NOT migrated** — that
belongs to the rebake wave, whose evidence has to be a byte-identical `.man`;
what is asserted here is that the protocol definition reproduces `sd-f-blocks`,
`sd-f-chains`, `sd-f-tight` and the entry, block for block.  `raco test
idioms.rkt` is 16 assertions, all green.

- **kernel is reached by `dynamic-require`, not `require`.**  `idioms.rkt` is
  on the load path of every sol file and `kernel/verify.rkt` pulls in Rosette
  and `sim.rkt`.  Measured cost of the check at module instantiation: ~0.4 s,
  once per process.
- **THE TWO SENSES, and why one checker covers both.**  `check-offset-protocol`
  is written for the SIGN family: the decoder branches on `v + G`, pass is
  positive, a diverted `v - K` is negative, zero is dead.  The MARK family
  branches on `MARK - v`, which is the SAME PREDICATE ON THE NEGATED VALUE with
  `G = MARK`, `K = 2*MARK`.  So `#:kind 'mark` negates the declared domain, and
  the four obligations read: every circulating `v` is strictly below MARK
  (gradebook's silent-halt landmine); and strictly above `-MARK`; no `v`
  collides with `±MARK`; `MARK - v` stays in the box.  Only `zero-unreachable`
  differs in MEANING between the families — for MARK the zero arm is the
  marker's own arm and is LIVE, so what the obligation buys there is the
  COLLISION check rather than a dead arm.
- **SURPRISE, and it is the useful one: gradebook's rejected `<< 14` packing
  fires TWO obligations, not one.**  Everyone (this file included) recorded the
  failure as "max packed 1,647,400 > MARK, `ff-blocks` computes `MARK - v`,
  sends a negative to `fdead`, which is an `H` — the server stops silently".
  True, and incomplete: `zero-unreachable` ALSO fires, i.e. a packed value can
  land EXACTLY on MARK and be read as the marker itself.  That is a WRONG
  ANSWER rather than a stop, and it is the strictly worse failure.  Nobody had
  written that half down; the interval check produced it for free.
- Numbers the check now prints rather than asserts: sign-divert on memory's
  domain discharges with margin **1,097,152** each side; MARK on the same
  domain with margin **48,576**; gradebook's decimal pack (0..1,009,000) is
  admitted with **39,576** to spare, exactly this file's earlier hand figure; a
  4e6 sign-divert domain fails on **three of four**.

## l3's save-load-swap: the DIGIT half was already there, and nobody had asked

The sudoku D-room refusal (recorded verbatim above, "want: A = cq.11, B = -;
have: A = 1, B = 1") now compiles, and the whole D room compiles from
littlelang: **9 blocks / 47 ops against the hand-written 11 blocks / 46 ops**.
l3 even beats the hand code in one place — `3 W /` where `dhead` writes `W M 3
W /`, because the divisor is already in B after the shift.

**The diagnosis in the sudoku entry above is wrong and this is the
correction.**  It says "l3's shuffle search does not consider the save-load-swap
(`M` <digit> `W`)".  It does: `M`, `W` and the digit loads are all in
`SHUFFLE-OPS`, so Dijkstra finds `M 1 W` at cost 3 on its own.  What was
missing was that **`bp-count` never stated the B goal.**  It did `want!(A = 1)`
with B FREE, the search took the cheapest route to A = 1 (a bare digit load),
that destroyed the seed, and the next `want!` asked for a value that was now in
neither hand.  One joint `want!(A = seed, B = 1)` fixes it.

- **It is also a CORRECTNESS fix, not only a completeness one.**  The
  `bp-count` body is `m +`, which adds B on every iteration, so B must be 1 on
  entry.  The old second `want!` had `goal-b = 'any` and was free to leave B as
  anything.  Any `bp-count` whose seed expression needed real shuffling was
  silently able to emit a wrong counter.
- **The WIDE half (`M` \`lit\` `W`) was genuinely missing**, and it is a
  separate real gap: gradebook's `/ 10000` unpack refused with "want: A = i3, B
  = 10000".  A backtick literal is not reachable from digit loads, and `M`
  \`10000\` `W` costs 9 against the default search limit of 8 — so it is now a
  STAGED fallback mirroring the existing goal-a one (satisfy A and the pending
  reads with B free, then swap the literal in behind them).
- **LANDMINE found on the way, not fixed, worth knowing: `synth-ops`' memo key
  omits `#:nodes`.**  A `#f` returned because the 60,000-node budget ran out is
  cached under the same key as a genuine refusal, so a later call with a bigger
  budget gets the cached give-up.  This wasted half an hour of diagnosis:
  probes at limit 8/9/10 all said `#f`, and the same query in a FRESH PROCESS
  with `#:nodes 5000000` returned `M 9 + M 6 + W (const 2)` at cost 8.
- **Second gap, recorded so it is not misread as this one:** building a
  TWO-DIGIT constant OFFSET in B (`A = 2, B = w + 15`, sudoku's box exponent,
  hand-written as `M 9 + M 6 + M 2 {`) needs an 8-cost path that exceeds the
  default node budget.  `w + 6` and `w + 9` compile; `w + 15` does not.  It is a
  BUDGET question, not a move-set one, and the fix is either a bigger `#:nodes`
  for wide-goal searches or a staged two-digit build.  The D-room acceptance
  program above sidesteps it by writing `(shl (shl 2 (+ w 9)) 6)`, which is the
  same value in two small wants.
- REGRESSION: `l3/test-compile.rkt` output byte-identical to baseline; both
  demos unchanged against `l3/RESULTS.md` (brackets 25x28 @ 621.4 = 487,212,
  reverse 30x30 @ 1837.9 = 1,654,088).

The acceptance program, kept here because `l3/test-compile.rkt` was outside
this pass's ownership and a regression nobody can re-run is not one:

```racket
(compile-room
 '((forever
    (let ([rr (recv in)])
      (send ring (shl 2 rr))
      (divmod (rq rrem) rr 3
        (bp<- (* rq 3))
        (let ([c9 (+ (recv in) 9)])
          (send ring (shl 2 c9))
          (divmod (cq crem) c9 3
            (bp-count w cq
              (send ring (shl (shl 2 (+ w 9)) 6))
              (send ring (- (recv in) 1))
              (loop (let ([y (recv ring)])
                      (case-sign y
                        [(zero) (send ring y) (break)]
                        [(pos)  (send ring y)]
                        [(neg)  (halt)])))))))))) 
 #:entry 'dstart #:ring 'ring #:chain-limit 12)
```

## kernel: the EXTENSION ALPHABET is now a table with prices on it

Three MODEL-ONLY ops, each buying back one capability `isa-abstractions`
deliberately threw away, each carrying a REALIZATION COST the enumerator's
one-cell-per-op accounting does not charge.  `racket kernel/isa.rkt table`
prints them under the abstractions they lift.

| pseudo-op | buys back | realization |
|---|---|---|
| `s$` / `r$` `(cubby put/get)` | a THIRD REGISTER | a 3x3 cubby room + TWO pipes on the host, **~6-8 ticks/use** — the model's 1 cell understates it ~6x |
| `S*n` `(bcast n)` | N OUTGOING PIPES | one `S` cell where N `s` ops are N cells in N bands; `N <= 3` on a room that also reads (CLASSES' four-pipe wall) |
| `U:cw` `(urecv d)` | a RECEIVE THAT BRANCHES | one cell, but the arms are GEOMETRIC — successors on opposite sides, so the chain partition is constrained and the arms cannot both be `#:tight` |

`(bcast n)` and `(urecv d)` are the UN-ABSTRACTED `S` and `U`: the table's `S`
is `s` and its `U` is `r` only because the model has one pipe each way.  Both
are worth having because the thing they price is a real design choice — a
fan-out room, and a receive that dispatches on WHICH PIPE delivered in ONE cell
where the sentinel-plus-`X` alternative is 2+ cells and a value-domain
obligation on the sentinel.

- **A pseudo-op is a LIST, never a char**, so nothing that walks `isa-chars` —
  the differential test included — can pick one up by accident.  `pseudo-op?`
  and `uses-extensions` are the check to run on a found sequence before quoting
  it at anybody: a result that uses one is a SCHEDULE AND A PRICE, never an op
  string you can lay.
- **`(urecv d)` asserts the turn, it does not discover it.**  The model still
  has ONE incoming queue.  `(urecv TURN-CW)` means "assume this receive came
  from the pipe whose arm is cw" — a way to write the assumption down.
- **They cannot be differential-tested, and that is what MODEL-ONLY means**: a
  pseudo-op that HAD a grid to run in would be an instruction.  So `isa.rkt`'s
  test submodule now also asserts the model's own contract — `(bcast 3)` is `s
  s s` in effect and ONE cell in cost (the point and the trap), `(urecv d)`
  blocks on an empty queue exactly like `r`, and no pseudo-op is a char.
- REGRESSION, the hcap pair, unchanged: register-only **REFUSES**, 146,311
  states / 2.4 s; with the cubby, **two 8-cell schedules** (`W s$ r * W r$ W -`
  and `W N s$ r * W r$ +`), 968,165 states / 21 s.  5 of 5 rediscoveries green,
  differential 1,660 cases / 0 mismatches.

## fragments.rkt catch-up: four shapes, each with its contract and its source

- **`bp-bit-readout`** — `]`^k then a branch, the only way to see the backpack
  without counting it down.  Costs k+1 cells and NO REGISTER, against
  `countdown-to-A`, which buys A at the price of its own magnitude in ticks.
  **RECORDED GAP:** l1's block-TERM vocabulary is `x` (the `X` op, 3-way on
  sign(A)) and `d` (2-way on BP > 0) — there is NO term for the machine's `x`
  op (2-way on BP's LOW BIT) or for `a`.  So the shippable form is the
  MAGNITUDE test and the true BIT test — the one that works for NEGATIVE BP,
  which is exactly where `]`, `m` and `x` are most likely to be wrong — is
  currently expressible only in the kernel model, where it is the differential
  harness's BP oracle.  **Adding a `(bit low high)` term to l1 is the one
  change that would ship it.**
- **`decimal-seed-ops` / `-complement-ops` / `-pack-ops` / `-unpack-ops` /
  `decimal-packed-max`** — gradebook's `g*M + (M - id)` family with M
  parameterised.  One B invariant does the complement (`- N`), the pack (`*`)
  and the unpack (`/`), so the loop needs NO LITERAL INSIDE IT, which matters
  because a backtick literal in a tight body is a compile error.
  `decimal-packed-max` exists to be handed to `protocol-admits?` BEFORE the
  multiplier is chosen: `(0 . 1009000)` is admitted, `(0 . 1647400)` is refused.
  That is the two halves of this pass meeting.
- **`x-ladder-dispatch`** — an n-way opcode dispatch that does NOT touch BP,
  for when BP is carrying a cross-statement invariant and the cheap `b m` + `d`
  ladder would eat it.  Head `M 1 W -` (the save-load-swap again), each rung one
  `-`, each `X`'s zero arm its opcode and cw arm the next rung.  **The ladder is
  LINEAR, not a jump table: put the hot opcode first.**
- **`rotate-by-s`** — `ring-rotate-counted` with the count arriving in A rather
  than off the ring front, the common case when the count was computed.  The
  landmine is LAP ACCOUNTING, not the loop: the rotation overshoots the sentinel
  by s-1 cells, so a rotating ring server needs pad cells and a SECOND sentinel
  behind the first, and both paths must consume exactly L cells.  Hand the block
  list to `check-ring-balance` — that argument is now mechanised.

All four were checked by laying them through l1 rather than by inspection:
bp-bit-readout(k=3) 7x3, the 4-arm x-ladder 14x10, rotate-by-s 6x8.

## Method note: `verify all` was NOT usable as a gate this session

Two independent reasons, both worth knowing before trusting a red.

1. **`subset` alone exceeds a 500 s timeout** (8,000,000-tick stress cap), so
   `verify all` does not finish inside PLAYBOOK's own budget.
2. **Another agent rewrote `tcp-sol.rkt`, `reverse-sol.rkt`, `matmul-sol.rkt`
   and `sort-sol.rkt` in place between 19:57 and 20:04.**  Mid-write those
   produce structural-looking failures that read exactly like a regression —
   `assemble: rooms I (8 11 10 13) and F (3 9 9 26) have overlapping boxes` on
   reverse, `assemble: cannot melt tank ret (cap 16): no sweep works` on sort.
   Both cleared on their own once that agent settled.

So the gate used here was **memory + brackets + sudoku**, the three sol files
nobody else was holding, re-run after every edit; all six shipped problems were
green with byte-identical repro at the end.  **PLAYBOOK's "a transient load
failure is transient" applies to `assemble` errors too, not just load errors** —
check the sol file's mtime before investigating an assemble failure you did not
cause.

# Bundle A, BAKED: the rebake wave (2026-07-26, late evening)

The "Bundle A" section above ends with a candidate table and the words
**"Nothing below is baked."**  This wave baked it.  Four problems, four
outcomes, three new judge rows; `problems/{tcp,reverse,sort}-sol.rkt`,
`problems/memory*-sol.rkt`, `harness/problems.rkt`'s memory and tcp rows, and
`solutions/{tcp,reverse,sort,memory}*.man`.  Every candidate reproduced its
measured world to the tick, which is the first thing worth recording: the
Bundle A rig's numbers were not optimistic.

| problem | knob baked | local before | local after | judge before | judge after |
|---|---|---|---|---|---|
| tcp | partition [6] | 32x32 @ 4195.2 = 4,296,269 | **30x30 @ 3968.5 = 3,571,650** | 7,033,271 | **6,062,760** |
| reverse | ORDER, list reversed | 27x26 @ 2084.3 = 1,519,418 | **27x25 @ 1927.5 = 1,405,148** | 2,147,111 | 2,153,612 (loses) |
| sort | partition [1] | 27x28 @ 3533.7 = 2,770,432 | **26x28 @ 3484.9 = 2,732,128** | 4,248,088 | **4,193,459** |
| memory | none — canonicalization | 33x33 @ 10904.4 | unchanged | 66,543,935 | 66,543,935 (same bytes) |

Submission ids: tcp `11796005-ffd9-4494-b914-ada003093148`, reverse
`b1ace16f-f85e-4666-acf6-b8efb3f99c06`, sort `8f1b8da4-d37f-4996-bca6-ce80c9e975ec`,
memory `b827aa87-f6e0-489d-b781-656e9e8b16f3`.

## The four landmines, each one paid or dodged

- **"A new partition makes the baked deltas INFEASIBLE"** — honoured, not
  tested.  Every one of the three bakes took the rig's rescue-scan point as an
  OFFSET (`#:deltas`), confirmed the world and the suite at that offset, and
  only then folded it into `BASE-DELTAS` with the componentwise merge.  Nobody
  hand-summed a base and nobody re-ran gravity from the old point.
- **`menu-ref` CLAMPS** — every rescue offset carried a `cshape` term except
  sort's, and sort's is the one whose partition split a chain rather than
  merging one (`(boot rstart)` -> `(boot) (rstart)`), i.e. the one that grew
  the front instead of shrinking it.  Consistent with the rule; not a
  coincidence to rely on.
- **est is a screen, not a ranking** — no est number was used anywhere in this
  wave.  Every decision came off a simulated suite.
- **partition and order do NOT compose** — obeyed literally.  Reverse's
  measured best PARTITION ([2]) plus the reversed order is 1,484,062, worse
  than the order alone at 1,405,148; tcp's best partition plus its best order
  is 3,588,900 against 3,571,650.  One knob per problem, every time.

## A PARTITION IS PART OF THE BAKE, in the same class as a tank former

This is the wave's own addition to the maintenance rules, and it is the thing
most likely to be forgotten by whoever next wants an old world back.
`solutions/tcp-prev32x32.man`, `solutions/reverse-prev27x26.man` and
`solutions/sort-prev27x28.man` are all kept — but **their `#:deltas` line alone
will not rebuild them.**  Each needs its predecessor's CHAINS LIST as well,
because the deltas index a room family that no longer exists at that partition.
So each sol file's kept-world comment now names BOTH: the previous chains list
and the offset.  NOTES already says "the former is part of the bake";
partition and chain ORDER join it, and chain order is the sneakier of the two
because the CFG is byte-identical and only a list's order changed.

## The rest of the wave, honestly

- **Reverse is the negative result, and it is worth its space.**  The order
  knob paid exactly what it promised (-7.5% local, judge x1.533 as calibrated)
  and reverse.man went 2,330,613 -> 2,153,612, -7.6%.  It still LOSES to
  `reverse-manual.man` at 2,147,111 — by 6,501 points, **0.30%**.  The whole
  remaining gap is max-dim (26 vs 27); on judge TICKS the searched build is
  0.6% AHEAD (2954.2 vs 3176.2).  Two consequences: (1) the hand-drawn world
  is now beaten on the only axis a search controls and survives purely on one
  column, which is the "floorplan STRUCTURE, not search" residual NOTES
  already recorded for reverse — the 289-position I/O insertion sweep is still
  the thing that would close it; (2) submitting anyway cost nothing and gave
  us the x1.533 calibration point for free, which is the submission-economics
  rule working as written.
- **Sort's win has zero area in it.**  27x28 -> 26x28 leaves max-dim at 28, so
  `area^2` is 784 both times and all 1.29% is ticks.  A search that prunes on
  the area floor with `>=` discards this candidate outright.  Same shape as
  tcp's earlier combo-sweep win; second time it has come up.
- **tcp is now builder-reproducible at the top.**  Every previous tcp winner
  was `tcp-manual.man`, hand-drawn and not rebuildable.  3,571,650 local /
  6,062,760 judge is the first automated world to take that crown, and it
  did it with a ONE-LINE change to a chains list plus a rescue scan.

## Two housekeeping repairs, both of which were quietly costing us

- **`harness/problems.rkt` had `#f` for tcp's problem id**, with a comment
  saying the id "was never recorded here" — but `CURRENTSCORES.txt` has had it
  since the first tcp submission, so every tcp submission for a day went out
  by hand-rolled `curl` while `submit tcp` refused.  Now registered
  (`d61a3af1-c74f-44c0-98f7-4f20eeefa3fb`), confirmed by a graded 20/20
  against it.  **When two files disagree about whether a fact is known, the
  one that says "unknown" is usually just stale.**
- **memory's registry row still pointed at the LOSING protocol.**  The
  sign-divert world had been the judge winner since the evening
  (66,543,935 vs the MARK family's best 76,426,791) and lived under its own
  name, so `verify memory`, `submit memory` and `solutions/memory.man` all
  still meant the MARK build.  Repointed: the row names
  `build-memory-signdivert-grid`, `solutions/memory.man` IS the sign-divert
  world, the MARK world is preserved as `solutions/memory-mark.man` (plain
  `(build-memory-grid)`), and `solutions/memory-signdivert.man` is DELETED as
  a duplicate.  Both builders take the same movable set, so the row's movables
  list is unchanged.  Proof the rename changed nothing: the resubmitted
  `memory.man` graded **66,543,934.875, identical to the original
  sign-divert submission**.  Cost of leaving it: an agent running
  `verify memory` was checking the wrong world, and `submit memory` would have
  posted a 12.9% worse grid.

## Calibration table, re-measured (these ratios exist nowhere else)

    tcp     x1.697   was x1.71   — held
    reverse x1.533   was x1.53   — held
    sort    x1.535   was x1.53   — held
    memory  x5.604   was x5.85   — MOVED, and the direction matters

Memory's ratio dropped because the protocol changed, not because the estimate
was wrong: the sign-divert forwarder is 8 ticks/value against MARK's 10 and
carries one ring slot per output instead of two, and the judge's case set is
heavy enough that its lap count is where that shows.  **A judge/local ratio is
a property of the PROGRAM, not of the problem** — the same lesson sudoku
recorded from the other direction (x1.345 at 31x33 vs x1.409 at 32x32, same
program, different floorplan).  Re-measure the ratio whenever the machine
changes, and never carry a problem's old ratio across a protocol swap.

## Coexistence, from the other side of the earlier note

The section above this one records another agent seeing
`assemble: rooms I ... and F ... have overlapping boxes` on reverse and
`cannot melt tank ret (cap 16): no sweep works` on sort between 19:57 and
20:04, and correctly diagnosing them as a mid-write artifact.  **Those were
this wave's edits** — precisely the window between changing a chains list and
folding in the matching rescue deltas, when the sol file is internally
inconsistent by construction.  Confirming their diagnosis from the writing
side, and adding the mitigation: a partition/order rebake has an unavoidable
inconsistent window, because the chains edit and the deltas edit cannot be one
atomic write to the same file.  Make it as short as possible and expect
exactly those two error messages inside it.

Symmetrically, this wave lost ~25 minutes to `idioms.rkt` and then
`kernel/isa.rkt` being mid-write (`struct-out: identifier is not bound to
struct type information` at `emission-protocol`, then at `isa-ext`, then
`provide: provided identifier is not defined` at `print-extensions` — three
different errors in one file over ten minutes, which is the signature of
someone typing, not of a bug).  What worked: an `until` loop polling
`racket -e '(require "harness/problems.rkt")'` in the background while doing
non-racket work.  **Do not investigate a `struct-out` error in a file you do
not own; poll it.**  Also note `tcp-sol.rkt` does NOT require `idioms.rkt`
(its forwarder is a bare bouncer), which is why tcp's verify slipped through a
window in which reverse/sort/memory could not even load — a dependency the
blast radius of another agent's edit respects.

# Subset: the CFG is written and CORRECT, and l1 cannot lay it out (2026-07-26)

Continuation of "Subset: the design doc's BACKTRACK COUNTER IS WRONG" above,
after being told to build the mark-scan machine.  **The machine exists as a
verified CFG and there is still no grid.**  The blocker moved from the
algorithm to the room packer, and that is worth recording precisely because
it is the first time in this repo that l1 has refused a CFG this size.

**`problems/subset-sol.rkt` holds the shipped-shape CFG** (K=2, `[suf, v]`,
prune set `under`, mark-scan backtrack, padded to 21 groups).  It is not a
sketch:

- **`kernel/cfgsim.rkt` is a block-level interpreter for the l1 IR** (promoted
  out of scratch, since scratch is cleared between sessions)
  — ops, terminators, a FIFO ring and a MARK-diverting forwarder — so a CFG
  can be executed before any layout exists.  It models a blocked `(r in)` as
  normal termination, which is exactly what a correct server looks like.
- Against it the CFG passes **7/7 public cases and 150/150 of a random
  in-box battery vs `subset-spec`**, plus the two-round stream.  Block counts
  per public case: 425 / 413 / 425 / 849,943 / 13,150 / 381,290 / 17,532,295.
- The K=5 {under, smin, maxcap} version was written FIRST and is equally
  green at block level (7/7, 150/150).  It is 66 blocks.

**This interpreter is the reusable part, and it now lives in `kernel/`.**  It
found every control-flow bug before a single width sweep — the measurement
gate's discipline applied one level down — and it is pinned by replaying the
SHIPPED sort CFG against sort's published outputs, so a red self-check
accuses the interpreter rather than the CFG under test.  Any future CFG past
about a dozen blocks should be run through it before any layout work.

## What l1 says, and what it means

Four separate structural fixes were needed just to get past the compiler's
own assertions, and each has a one-line rule worth keeping:

1. **A `goto` that is not to the chain successor must sit at a chain TAIL.**
   (`arl2`, `sumv`, `expg` each tripped this.)
2. **A branch's STRAIGHT arm must be its chain successor — for TAIL blocks
   too.**  "x zero-arm of dv must be its fall-through".  The fix is an empty
   stub as the straight arm, which is CLASSES.md's "one stub block can buy
   six columns" used for correctness rather than width.
3. **A `#:tight` circuit is a rigid token whose width is its whole chain
   LANE, not the head's ops.**  `bta` heading a five-block chain asked for a
   `w=31 h=2` rigid box and no width in the sweep could hold it.  Every
   tight head therefore wants a TWO-BLOCK chain: head + empty stub.
4. **Long chains are rigid width demands.**  `rstart..expg` as one chain
   reported `rstart (w=26 h=1) does not fit` at max-width 30.

After all four the compiler stops complaining and just fails:
**`no feasible layout` at every width from 18 to 70**, on both the shelf and
the melt engine, with `#:strict-bands? #f`, with `#:restarts 30`, with an
explicit `#:max-height` up to 70, and with or without `#:col-order`.  The
trace is all `wire arm ... failed` / `wire goto ... failed` — rail routing,
not a structural error (no exception is being swallowed; `;; shelf exn:`
never appears).

**The bisection is the useful part, and it is clean:**

| sub-CFG | blocks | chains | result at max-width 26 |
|---|---|---|---|
| read-in only | 12 | 5 | **20x13** |
| backtrack only | 15 | 11 | **19x18** |
| emit only | 13 | 10 | **23x13** |
| backtrack + emit | 28 | 21 | fails at 26/32/38/46 |
| whole machine | 44 | 21-26 | fails everywhere |

Every third of the machine lays out; no two thirds do.  `sort-sol`'s C room
(17 blocks, 7 chains) still compiles to 24x17 in this same tree, so nothing
environmental is broken.  Note also that `attempt-shelf` takes **no height
argument at all** — `#:max-height` only reaches the melt engine — so "give
it more rows" is not a lever on the shipped packer.

**The diagnosis is CLASSES.md's addendum, verbatim: "a room grows past ~40
blocks — two half-rooms pack into a smaller bounding square than one big
one".**  This machine is the first one in the repo to actually hit that, and
the sub-CFG table above says the split line is already drawn: read-in /
search / emit are each independently layable.  What makes it a floorplan
project rather than an edit is that all three halves need the SAME ring, so
the split wants `assemble` directly with the rooms strung on one ring cycle
(the way F already is), plus a phase handshake so the idle room relays
transparently.  Cheap in ticks — a relay room is rate-matched to C, exactly
like the forwarder — but it is a new topology, not a parameter.

## Honest negatives, with numbers

- **Dropping K=5 to K=2 did not rescue the layout** — 66 blocks to 44 blocks,
  still infeasible.  Block count alone was not the binding constraint; rail
  congestion across many chains is.
- **Merging chains to cut rails did not help either.**  Rebuilt at 21 chains
  with lanes under 17 wide, tight and non-tight: infeasible at 26/32/40.
  So it is not a simple rails-vs-lane-width trade at this size.
- **The melt engine is not a fallback here.**  30 restarts, soft bands,
  height 70: same verdict, and it is ~10x slower to fail.
- K=2 costs nothing measurable on the hidden-set proxy (177/200, same as
  K=5's 177) but costs the constructed big-element trap: **482M ticks against
  763**.  If the split lands, put `maxcap` back — the read-in fold for it is
  written and verified in the K=5 CFG's history and needs the two-register
  `[smax, v]` pair trick, since a three-field back-to-front fold has no third
  register.

## What the next agent should NOT re-run

The width sweeps above (18..70, both engines, both band modes, restarts to
30, heights to 70) are exhaustive for the single-room shape.  The next move
is the room split, and the sub-CFG table is its specification.

# Pathfinder: the BFS fits in FOUR REGISTERS, and the distances need ONE BIT
# (algorithm proven + machine designed; NOT built, 2026-07-26)

Owner of this section: the pathfinder display-build agent.  Files created:
`problems/pathfinder-proto.rkt` (the validated algorithm, runs in 1s),
`display-world.rkt` (a mini world assembler that knows about DISPLAYS).
Nothing registered in `harness/problems.rkt`, no `.man`, **nothing submitted**.
Read this before starting the build again — the hard thinking is done and the
remaining work is layout, not algorithm.

## The trick: you never store distances, you store BIT 1 OF THE DISTANCE

The problem looks like it needs a distance field (256 cells x 6 bits) to walk
the lexicographically-smallest shortest path.  It does not.

* The board is 256 wall bits = **4 x 64-bit words** = the state of two men,
  exactly snake's bitboard.  Word j holds rows 4j..4j+3, bit i = cell 64j+i.
* A BFS wave from the FLAG is `V' = (V | E(V)) & OPEN`, iterated k times,
  where `E` is the 4-neighbour dilation.
* At a cell of distance d, every neighbour has distance d-1 or d+1 — the grid
  is bipartite — and **bit1(d-1) != bit1(d+1)** (adding 2 always flips bit 1).
  So a single bit-plane `M = { c : bit1(dist(c)) = 1 }` plus a mod-4 countdown
  identifies the descending neighbours EXACTLY.  Parity itself is free
  (it is (x+y) parity) and therefore useless; bit 1 is the one bit that pays.
* k is not searched for: it is the wave's own iteration count when the wave
  reaches the robot, so the countdown `d = k, k-1, …` is free too.
* `M0 = V ^ M` (V = the final visited set, M subset of V) gives the other
  class in 4 XORs, once per round.

Consequence: **one wave of k iterations per round**, not the k^2/2 iterations
that re-running the wave per move would cost.  Cost of the alternative,
measured on the spec box: k=64 x 6 rounds = ~2000 iterations/case ~ 10M ticks,
i.e. inside the 15M cap but only just — the bit-plane turns that into ~34k ops.

## Measured, not estimated (`problems/pathfinder-proto.rkt`)

A register-op-level prototype (64-bit words, the machine's own shift
semantics) that emits the display script and renders it back into frames:

    a straight shot 23/23 · around the pillars 37/37 · the long way 90/90 ·
    rooms and doors 57/57 · a cluttered field 45/45 · running errands 57/57 ·
    there and back again 78/78     — all MATCH pf-spec frame for frame

    avg 9,436 machine ops/case; worst public 14,239; #:min-k 40, 6-round
    stress case 34,185 ops and MATCHes.

At a pessimistic 5-10 ticks/op that is 50-350k ticks against a **15M cap**:
this problem is **area-bound, not tick-bound**, which inverts the usual
priority — spend ticks to buy a smaller floorplan, not the other way round.

## Four machine facts that make the bitboard cheap (all from the ISA, not luck)

1. **E/W shifts need no edge masking.**  A shift by 1 that crosses a row
   boundary lands on column 0 or 15, and *every border cell is a wall*, so the
   `& OPEN` kills it.  Cross-WORD carry on an E/W shift lands on a border cell
   too, so the dropped carry is correct.  Only the +-16 shifts need real
   carries: `cS_j = V_j >> 48` into word j+1, `cN_j = V_j << 48` into j-1.
2. **Every board word has bit 63 = 0** (bit 63 of word j is cell (15, 4j+3), a
   border wall), so the *arithmetic* `}` is a logical shift on our data and no
   sign-masking is needed.  The WALL board is the exception (its bit 63 is 1);
   store `OPEN = ~WALL` and the invariant holds for V, M, M0 too.
3. **Out-of-range shifts return 0, and that IS the word selector.**  `{` is 0
   when B is outside 0..63 and `}` is 0 for B<0 and sign-fills (= 0 here) for
   B>63.  So `hot[j] = 1 << (p - 64j)` for j=0..3 builds a one-hot board with
   NO branch and NO word-index arithmetic, and `OR_j ((T_j >> (q - 64j)) & 1)`
   tests bit q of a 4-word board the same way.  This is the single most useful
   thing found this session; it removes every 4-way dispatch the design
   otherwise needs.
4. **One shift aligns all four neighbours at once.**  Shifting word j right by
   `pos - 16 - 64j` maps global cell g to bit `g - pos + 16` *independently of
   j*, so the OR over the four words puts up/left/robot/right/down at bits
   0/15/16/17/32.  Then "is direction D available" is `X` on the SIGN of
   `S << (63-k)` — no mask constant, no `& 1`, and `X`'s three-way is exactly
   the branch you want.

## The frame protocol (settled, and cheaper than it looks)

SWAP **1** (preserve NEXT and the cursor) throughout, because pathfinder is an
ACCUMULATING display problem in snake's sense: consecutive frames differ by
2 pixels.  Per move: `ADDR old, DATA 0, ADDR new, DATA 10, SWAP 1` — 5 values.
Round start additionally paints the flag once (`ADDR f, DATA 9`); it persists
in NEXT for the whole round and the robot's own colour-10 write covers it on
the last frame, so "the flag is not drawn on the last frame" costs zero ops.
The setup frame needs no ADDR at all: 256 DATA writes ride the cursor's
auto-advance.  d1 (same-tick DATA is in the frame) is CONFIRMED, so no spare
tick before a SWAP; d4 (empty SWAP commits) is CONFIRMED, so the machine must
never SWAP anywhere else — 1 + sum(k) SWAPs, exactly.

## The machine that was designed for it (built as far as the assembler)

`l2.rkt` **cannot place a display** — there is no display support in it at all
(kinds are 'cfg/'in/'out).  `display-world.rkt` is the replacement: rooms at
caller-chosen origins, `+`/`=`/`:` display walls, a pipe router over
(pos, dir) with the same grammar guards l2 uses, and a targeting oracle for
the sim's nearest-pipe rule.  Smoke-tested: display + rooms + pipes assemble,
load and commit frames under sim.rkt.

Intended world — display + I room + **three men**:

* **U, the shifter/ALU** — `r M r { s r } s`: reads `(amt, v, v)`, returns
  `(v<<amt, v>>amt)`.  Stateless, no phase discipline, 1 in / 1 out.  Every
  shift the algorithm needs comes in pairs of opposite direction (1, 16, 48),
  so one request serves both.  With `amt = 0` the same request is a **2-slot
  park** — the third and fourth registers the controller does not have.  The
  amount may be pre-sent while A is free, which is what makes parking a value
  that is *already in A* possible.
* **P, the painter** — one sign-tagged command stream: `>0` = ADDR then read
  the colour, `0` = SWAP 1, `<0` = toggle a raw board mode that paints `7*v`
  (so the controller never computes the wall colour and never addresses during
  setup).  Cell (0,0) is always a wall and the robot/flag are never there, so
  0 is free to mean SWAP.
* **C, the controller** (l1 CFG) + a **tape**: a long FIFO through a relay
  holding the 12+ state words.  Channels: `in`, `tape` s/r, `alu` s/r,
  `paint` s — 6, banded with l1's `#:col-order` and vetoed with `#:accept?`
  against the targeting oracle.

Two schedules worth keeping, both worked out against the 2-register limit:

* **Building the OPEN words from the input stream** costs 3 live values
  (accumulator, running power, incoming cell) and therefore looks impossible.
  It is not: park `(p, w)` in the ALU and run
  `0 s | r(alu)->p | M | + (=2p) | s(alu) | r(in) | s(paint) | * (=v*p) | M |
  r(alu)->w | + | s(alu)` — 13 ops/cell, 2 registers, and `+` is `|` because
  the bit being set is fresh.  (The tempting alternative, `w = (w>>1) |
  (v<<63)`, is WRONG: the arithmetic `}` sign-fills once an intermediate w has
  bit 63 set, and the 63-bit mask constant is an 19-digit literal the lint
  rejects.)
* **The wave's north carry is a LOOKAHEAD** — word j needs `cN_{j+1}` — and
  that is the one place a FIFO tape cannot help, because a value pushed this
  lap returns next lap.  The fix is a one-word LAG: body j finishes word j-1.
  With pass 1 pushing `[V_j, X_j, cS_j, cN_j]` per word (X = the 5-term smear,
  computed while V_j sits in B and the amounts ride A as literals) and pass 2
  carrying exactly ONE value across the body boundary, everything fits in A/B
  plus one ALU park.  Both boundary carries are *identically zero*
  (`cN_0` is row 0, `cS_3` is row 15, both all-wall), so there are no edge
  cases in the j-loop.

## Honest status and what is left

Left to build: C's CFG (~350 ops across setup / wave / descent / paint / round
loop), the floorplan, and the targeting solve.  The recommended order is to
run the op program against a Racket VM of this machine model (registers, tape
FIFO, ALU FIFO, painter) FIRST — the frames it emits can be compared to
`pf-spec` exactly as the prototype does, so every logic bug is caught before a
single grid exists; only then compile with l1 and lay out.

Sizing to expect: display 18x18 forces max-dim >= 18 on its own; C is the only
big room (~350 ops ~ 25x24 at l1 densities).  A squarish pack around the
display is worth real score here because ticks are ~100x under the cap —
**every hour spent on ticks in this problem is misspent; spend it on area.**

## Build checkpoint: the machine VM exists and PHASE 1 IS GREEN

`problems/pathfinder-machine.rkt` is the machine model (registers A/B/BP, the
tape FIFO, the shifter FIFO, the painter, the LM-75) plus the controller
program written in **l1's own IR** — blocks of ops with `(goto …)/(x …)/(d …)`
terminators — so a validated program compiles with `compile-cfg` unchanged.

**PHASE 1 (setup) matches `pf-spec`'s setup frame on all 7 public cases**, and
the tape it leaves behind (`[O0 O1 O2 O3 pos]`) is asserted against an
independently computed OPEN board and robot position — the half a frame
compare cannot see.  3,667 ops, **tape depth <= 5, ALU depth <= 3**.  Those
two high-water marks are the pipe capacities the layout must provide; the VM
reports them for every phase, so the tank is sized by measurement.

Two things the phase-1 debug settled, both of which will bite again:

* **Every ALU request must be accounted for exactly.**  The park is a FIFO, so
  a request left half-sent (amount queued, values not) puts junk outputs at
  the head of the queue and every later `r alu` reads the wrong value — the
  frames still looked plausible.  The fix that generalises: when a phase ends
  mid-request, *reuse* the queued amount as the next request's amount rather
  than draining (the word-boundary flush does exactly this and costs 0 ops).
* **`p` wrapping to 0 after 64 doublings is the word boundary**, so the setup
  needs ONE counter (BP = 256 cells), not two nested ones, and the boundary
  test is an `X` on a value that is already in A.

Remaining phases, in order: wave (pass 1 expand / pass 2 combine-with-lag /
M-plane + reached test), descent, round loop.  Write each against the VM,
compare frames with `pf-spec`, and only then lay out.

# SNAKE: the second display problem SHIPPED — and three findings that outlive it (2026-07-27)

`problems/snake-sol.rkt` + `solutions/snake.man`, registered in
`harness/problems.rkt` (registry row + `display-problems` entry
`'snake (hash 'res (cons 16 16))`).  **SUBMITTED, 17/17 hidden cases, 57x51,
avgTicks 14956, score 48,590,897** (id `06e6060e-7b0a-4925-9e1e-3b22313b1c59`;
the capacity-fixed rebuild is `f53667f0-7aab-4c61-befc-fa3e57850788`, also
17/17).  Verify GREEN, stress GREEN, repro byte-identical, lint clean.

## The grader ADJUDICATED all four of snake.rkt's ambiguity parameters at once

17/17 on the defaults means `snake-loss-commits-frame?`,
`snake-red-on-loss-frame?`, `snake-fruit-persists?` and
`snake-fruit-on-loss-frame?` are **all #t** — including A4, the one the spec
file says "no public case can settle even in principle".  A full pass on a
17-case hidden set settles every parameter simultaneously and for free; that
is worth remembering the next time a spec file parameterises an ambiguity.
No probe was ever built.

## l2 CANNOT ASSEMBLE A DISPLAY — budget for a hand-assembled world

`grep -c display l2.rkt` is **0**.  Displays exist in sim.rkt and in the
harness, but `assemble` has no notion of one, so a display problem's world is
hand-placed: l1 compiles the code rooms, the floorplan and every pipe path are
explicit coordinates, and gravity/shape-menus are unavailable (the footprint
is whatever you pack by hand).  What made it tractable in a day:

- **`targeting-ok?` is exported from l2** and is the sim's own rule, so a
  hand-built world can still *prove* every `s`/`r` talks to its intended pipe.
  Searching candidate attach cells (perimeter x perimeter, 4 walls) against it
  replaces the whole `attach-at` machinery in ~20 lines.
- A pipe leaving a room must step **away from the wall it attaches to first**
  (`parse-pipes: stray pipe glyph` otherwise), and a loop room needs a `>` at
  the corner *before* the `@` — **`@` is a nop, not a turn**, so `^` into `@`
  walks the man straight into the ceiling.  Both cost a debug cycle.

## THE DISPLAY'S THREE PIPES MUST BE LENGTH-MATCHED (ADDR vs DATA)

The display consumes at most one value per pipe per tick and processes
ADDR -> DATA -> SWAP.  With the painter sending `ADDR_i` then `DATA_i` g1
ticks later, correctness needs

    LD - g2  <  LA  <  LD + g1

(g1 = ticks between the two sends, g2 = ticks from `DATA_i` to `ADDR_i+1`).
An 18-cell ADDR pipe against a 9-cell DATA pipe **paints every pixel at the
PREVIOUS address** — the frames come out plausible and wrong.  The fix is to
pad the shorter pipe with a detour (a vertical run alongside the display's
left wall is free: only an *arrowhead* pointing into the border terminates a
pipe, body glyphs alongside it do not).  SWAP may be long: it only has to land
after this frame's last DATA and before the next frame's first, and a round is
tens of ticks.  `build-snake-grid` asserts `|LA - LD| <= 3`.

## TWO OUTGOING CHANNELS ON THE QUEUE ROOM ARE UNSOLVABLE — merge them with SIGNS

The queue room wants `s tk` (push) and `s pt` (paint) on separate pipes.  Over
l1's **entire** search space (25 chain partitions x widths 16..34, plus the
melt), **no layout separates them** under the nearest-segment rule: 16 tank
sends and 11 paint sends interleave in every packing, and `#:col-order` cannot
help because `chain-bands` shares one woff/eoff across *both* kinds, so a
chain that reads the ring and then paints is band-infeasible by construction.

The fix generalises: **make the painter the tank's relay and tag the single
stream by SIGN.**  Addresses ride biased (a+3), so `v >= -1` is a queue
payload (forward it into the tank pipe), `v = -2` is SWAP, and `v <= -3` is a
pixel address whose *next* value is its raw colour.  One outgoing pipe, no
targeting problem, and the painter's forward path is 3 ops.  The same trick
bought the sentinel test: with payloads strictly positive, `N b` + a backpack
`d` splits body from sentinel in ONE rail where a 3-way `X` costs two — which
is what got C2 under l1's block ceiling at all.

## A TANK LOOP DEADLOCKS AT ~queue+15, NOT AT queue+1 — and it fails SILENTLY

Sized the loop at 61 cells for a queue of 52 (spec max length 50 + sentinel +
fruit) with "plenty of margin".  It **deadlocks at length 46** (queue 48): the
frames simply stop, no error, the run just times out with a correct prefix —
the exact signature of a wrong answer.  Both pipes back up while C2 wants to
send and P wants to send; paint commands share the C2->P pipe and both men
hold a value, so the usable capacity is well under the cell count.  Empirical
rule from this problem: **size a two-room tank loop at queue + 15**, and put
the capacity in a build-time assertion, because the failure mode is invisible.
81 cells clears the spec maximum; the cost was +1.2% ticks.

The stress suite now carries the case that finds it — a boustrophedon that
eats a fruit spawned in front of the head every other round, reaching length
46 in 93 rounds.  It needs a per-case cap (150000 in `stress-case-ticks`):
at the row's 40000 it stops at frame 73 of 91 and the driver calls it WRONG
OUTPUT.  Every other generated game keeps the snake short and never touches
the tank's limit, which is why the capacity bug survived a GREEN stress run.

## Cost structure, for whoever tunes this

Judge/local is **x2.67** (14995 vs 5625), the highest ratio in the tree after
memory's 5.85 — it is round gating: the input for round k+1 is withheld until
frame k commits, so every round pays the whole I -> D1 -> D2 -> C1 -> C2 -> P
-> display latency, and that chain is 5 rooms and ~60 pipe cells.  Locally the
per-round cost is `max(tank-loop transit, painter cycle x (L+2))`; the painter
relay is ~20 ticks per queued value and is the binding term for any snake
longer than three cells.  The two levers, in order: **shorten the painter's
racetrack** (a 1-op sign dispatch makes the forward path `r X s` — the
encoding above already supports it) and **repack the floorplan** (57x51 is
loose; the room set totals ~2250 cells, so ~48x48 is the packing floor).

# The STATION FLOORPLAN PACKER, and the thing it taught us about the judge
# (`floorplan.rkt`, new; `l2.rkt` NOT modified; 2026-07-27)

Owner of this section: the floorplan-packer agent.  Files: **`floorplan.rkt`**
(new, reusable, fully documented in its own header), `problems/
sudoku-station-sol.rkt` (rebuilt on it), `solutions/sudoku-station.man`
(31x33, resubmitted), `solutions/sudoku-station-prev41x41.man` (kept).
`CLASSES.md` has the addendum that tells the next agent when to reach for it.

## The headline, and it is not the packing

    JUDGE avgTicks  =  48.5  x  SINGLE-ROUND LATENCY

where latency is the emit tick of `(run-program g '(0 0 1))` — one sim run on a
one-round input.  Fitted on the two ALREADY-GRADED sudoku-station builds
(latency 106 -> judge 5139.35; latency 99 -> judge 4802, both within 0.3%) it
**predicted the third submission at 4,964,751 against an actual 4,966,874, an
error of 0.04%.**

Why it holds: the judge withholds round N+1 until round N has answered, so it
charges the input->output LATENCY of the whole chain, every round.  A local run
feeds continuously, so it measures THROUGHPUT — the slowest man's cycle — and
on a pipelined machine those are different numbers.  That is the whole content
of the "judge/local ratio" for round-gated problems, and the ratio is the wrong
way to hold it: the ratio moves with the floorplan (x2.030 at 41x41, x1.901 for
the hand layout, x1.809 here) precisely because pipe cells are latency and are
almost invisible to local average emit.

**So rank pipelined floorplans by `max-dim^2 x latency`, never by local avg.**
This is not academic — it changed the answer.  The 32x33 candidate has the
better local average and LOSES on the judge to the 31x33 one, because its pipes
are five ticks longer.  Ranking by local average would have shipped it.

## What the packer is

`l2` assembles a world from origins the caller supplies; it has no opinion
about where rooms go, so every station sol file hand-stacked its rooms.  A hand
stack is a local optimum gravity cannot leave — gravity moves one room one cell,
so it shaves columns and never re-bands a stack.  sudoku-station shipped at
41x41 with 40% occupancy for exactly that reason.

Two packers, both emitting ORIGINS that `assemble` consumes unchanged:

- **snake shelf packer** — rooms along horizontal shelves in chain order,
  direction reversing per shelf; exact DP per width cap.  Predictable, and the
  honest answer for sudoku-station is **34x34**, i.e. not good enough.
- **guillotine packer** — recursively cut the rectangle and give each side a
  CONTIGUOUS RUN OF THE CHAIN, keeping the (W,H) Pareto front per segment.
  Contiguity is the whole trick: every cut is crossed by exactly one channel,
  so no packing decision can lengthen more than one pipe.  Exact, sub-second on
  11 rooms, and a strict generalisation of the shelf snake.

The guillotine DP reproduces the hand-drawn 31x33 exactly — `I|D1|D2` over two
flush columns `G/S0/S1/S2` and `S3/S4/N/O` — which is how we knew the model was
the right one before any of it routed.

## RESULT: 41x41 / 8,639,247 -> 31x33 / 4,966,874 (-42.5%), 20/20 uberStrict

id `28ae5992-a758-408c-9791-2b464828ee0c`.  Beats the hand-drawn reference
(33x33 / 5,229,324) by **5.02%** at the same max-dim, on latency: 94 vs 99.
Not one CFG, protocol or register assignment changed — only the floorplan.
6/6 public + 21/21 stress + 200-case fuzz green, byte-reproducible.

## Four landmines, all measured, all in `floorplan.rkt`'s header too

1. **NEVER hand l2 unconstrained walls at 10+ rooms.**  `assemble` keeps
   `attach-tries` assignments per (room, kind) group and CROSS-PRODUCTS the
   groups.  An 11-room chain has ~20 groups, so `#:attach-tries 2` is 2^20
   picks: the process reached **25 GB RSS** and never returned.  At
   `#:attach-tries 1` it terminates, but the single centre-ranked pick per room
   usually has no coherent completion and assemble dies inside its own error
   path with `first: contract violation  expected: (and/c list? (not/c empty?))
   given: '()` — naming neither the room nor the channel.  (The proximate cause
   is real and worth knowing on its own: **l2 solves a room's `in` and `out`
   attachments as separate groups and `spread?` only separates cells WITHIN a
   group, so nothing stops one room's two pipes landing on the same wall cell**;
   `coherent?` then rejects the only pick there is.)
   The fix that works is to stop asking: the packer names the exact cell per
   end (`plan-attach-cells` -> `attach-at ... #:fixed`) and l2's search never
   runs.  Sound on a chain because with one channel per kind the sim's
   nearest-segment targeting rule is satisfied by ANY legal cell.  A broadcast
   or merge room does not get that for free.
2. **A 2-row corridor carries a vertical hop but NOT a sideways hook.**  Out of
   a room's south wall the pipe can only bend in the second corridor row, and
   climbing back into a neighbour's south wall needs a north bend there — which
   `bend-ok?` forbids, since the cell behind it is the next shelf's north wall
   and the bend would read as a second pipe start.  Symptom: every TURN in the
   world routes and every IN-SHELF link fails.  A hook wants three free rows.
3. **NOTCHES BEAT GAPS.**  Because of (2), the winning geometry is not wider
   corridors — it is rooms FLUSH with RAGGED widths.  The overhang beside a
   narrower room is a pocket, and the CORNER cell facing it is a judge-legal
   attach point (l2's `edge-of` gives corners two outward normals) that costs
   zero separating rows or columns.  A uniform gap grid destroys exactly this.
   Corollary that cost a debugging pass: l2 calls the four corner cells
   'nw/'ne/'sw/'se, so `walls '(n)` does NOT admit the ends of the north wall —
   a clearance check that counts them passes and then dies at "no free wall
   cell for channel X".
4. **Reserve ~2 cells of margin around the whole packing.**  A room flush
   against coordinate 0 has no outward cells at all (the router's world starts
   there), so a tight column pins its middle rooms with zero attachable walls.
   `render` drops whatever no pipe used, so unused margin is free.  The hand
   floorplan does this too — its rooms start at column 2.

## Honest negatives

- **The snake shelf packer is not the answer for this room set.**  Its exact
  optimum is 34x34 (assembled, 6/6 green) against the guillotine's 31x33.  It
  is kept because it is predictable and because its shelf/gap vocabulary is
  what a hand floorplan already speaks, but reach for `guillotine-search`.
- **hgap 0 / vgap 2 does not route** on a full-width shelf stack, for landmine
  (2).  Its best estimate was 35x35 and it never assembled; do not re-derive it.
- **Pareto-on-dims alone throws away the winner.**  A dominated box can win the
  real objective, because a 2-row serpentine is both wider and faster than the
  4-row one.  `guillotine-front` takes `#:pareto? #f` for this reason, and the
  31x33 winner came out of the non-Pareto sweep.
- **Gravity was not run on the packed world and is not expected to pay.**  The
  packing is flush by construction; there is no single-cell slack left to take.
  `plan-shift` is wired so gravity still composes (attach cells are recomputed
  after the move), but the deltas are all zero and a sweep is a fresh idea, not
  a rebake.

## What the packer does NOT cover, i.e. the next move

**Tanks.**  The constraint model is explicitly "no capacity channels, no melt
regions", which is what makes a station world pure rectangle packing.  matmul
(two ~270-cell melted tanks needing free FIELDS) and snake (tank loop + a
display, and `l2` still has no `'display` kind) are therefore OUT OF MODEL, and
both sol files were being actively edited when this was written — untouched by
design, on both counts.

The extension is small and worth doing: **a melt region is a rectangle**, so a
tank can enter the guillotine tree as an `fp-fixed` pseudo-room between the two
rooms it joins, with a menu of aspect ratios whose area >= capacity.  The tree
then places the field, and the builder passes it straight into `chan-spec`'s
capacity region.  That single change would put matmul (55x63, 96% area score)
and snake (57x51, ~48x48 packing floor) in range of the same treatment.

# PLOTTER: the packed-V Bresenham, and four L2 attachment landmines (2026-07-27)

`problems/plotter-sol.rkt`. The first display-judged world we have built.

## The algorithm: nine live values collapse to ONE

The md's Bresenham carries `x0 y0 x1 y1 dx dy err sx sy` against two readable
registers. Three moves in sequence remove the pressure entirely, and the third
is the one worth reusing:

1. **Major axis once per round.** With `D=|dx|`, `E=|dy|`, `M=max`, `m=min`,
   the major axis steps on EVERY iteration (this is exactly what
   `problems/plotter.rkt`'s closed form proves), so the pseudocode's two `if`s
   become ONE test and `sx/sy` stop being control flow.
2. **Track `p = M - 2e`, not `e`.** Then the test is `p >= 0` — a SIGN test,
   not a comparison — with `p += 2m` every iteration and `p -= 2M` when it
   fires. `p0 = 2m - M`.
3. **Pack the error and the address into one integer.**
   `V = p*1024 + addr`, `addr = 32y+x in [0,767]`. Because `|addr| < 1024`
   cannot carry into the high field, `V >= 0` IS `p >= 0`, and both updates
   become a single add: `K1 = 2m*1024 + sa` always, `K2 = -2M*1024 + sc` when
   the test fires. ONE loop variable, and `addr` comes back out as `V % 1024`.

So the FOUR SIGN COMBINATIONS never become code paths and never become live
data — the per-round setup folds them into K1/K2, where `sa` is the major step
(±1 or ±32) and `sc` the minor one.

Two more things fall out:

- **Termination is a backpack counter of `M+1` pixels**, so `addr1 = 32y1+x1`
  is never computed or stored.
- **The K2 station is asked for exactly `m` additions per round** — the minor
  axis's total travel — so the setup can tell it how many requests to expect.
  That is what lets a station reload a per-round constant with NO `q` poll, NO
  sentinel value and NO handshake: it counts down to zero and goes back to
  waiting. This idiom generalises to any station whose per-round work count is
  computable upstream.

**Verified exhaustively**: a Racket transcription of exactly what the rooms
compute matches `pl-bresenham` on all 32*24*32*24 = **589,824 endpoint pairs,
0 mismatches**, and the Q-request count equals `m` in every one. Do this
before building a grid; it cost minutes and would have cost hours later.

## FOUR L2 ATTACHMENT LANDMINES, all with the same misleading symptom

Every one of these reports as `assemble: cannot route channel X` or
`room X: no attachment satisfies targeting` — i.e. as a SPACE problem. None of
them is. The diagnostic that settles it: **rerun the same floorplan at gap
widths from 6 to 40 cells; byte-identical failures mean it is structural.**

1. **Two pipes of the same kind read/sent in ALTERNATION cannot be targeted.**
   Both ops sit on one lane in lane order, so no pair of attachment cells puts
   each op nearest its own pipe. A four-input splitter that alternates
   `(s x)/(s y)` is refused outright. Fix: make the front end a strict LINE,
   each room keeping what it needs and forwarding the rest in the order the
   NEXT room wants. Costs a few `s` ops, removes the constraint.
2. **L2 solves a room's IN group and its OUT group INDEPENDENTLY**, so it can
   hand one room THE SAME WALL CELL twice. Verbatim from its own trace:
   `attach R/in: best ((qr (110 . 38)))` / `attach R/out: best ((rm (110 . 38)))`.
   Small rooms are worst — a two-op relay's `r` and `s` are adjacent, so its
   two attachments are adjacent and each one's halo kills the other.
3. **A two-room cycle is two anti-parallel pipes in one corridor.** The router
   lays the first and the second has nowhere to go, at ANY corridor width.
   Fix: make it a cycle of THREE, where every adjacent pair carries exactly
   one pipe.
4. **`#:attach-tries` is a cross product over (room, kind) groups.** Fifteen
   groups at 2 tries is 32k picks (fine); at 3 it is 14M and the process never
   returns. At 1 the single centre-ranked pick often has no global completion
   and `assemble` dies inside its own error path with
   `first: contract violation ... given '()`.

**Where this landed:** l2 could not assemble this world at all. `display-world.rkt`
could — rooms at caller-chosen origins, pipes as explicit (src wall cell -> dst
wall cell) pairs, and `targeting-report` to check the sim's nearest-pipe rule
afterwards. Choosing the wall cells makes landmine 2 impossible by
construction. On a chain of nine rooms with three multi-channel rooms, that is
the cheaper tool.

## Two DISPLAY timing landmines (new; they are not in the d-probe list)

Both follow from the LM-75 taking at most one value per pipe per tick and
processing ADDR then DATA then SWAP.

- **L1. ADDR_k and DATA_k must land in the same tick or adjacent ticks, and
  DATA_k strictly before ADDR_{k+1}.** So the ADDR pipe and the DATA pipe must
  be nearly the same LENGTH. A driver placed at the display's bottom (which
  makes the SWAP short) puts ~28 cells between them and paints garbage. Pin the
  driver at the display's TOP-LEFT corner, where the top wall's first cell and
  the left wall's first cell are diagonally adjacent.
- **L2. SWAP_k must land after the round's last DATA and before the next
  round's first ADDR** — SWAP 0 homes the cursor, so an ADDR that arrives
  first is erased and its pixel lands at (0,0). The SWAP pipe has to reach the
  BOTTOM wall ~28 rows away, so it lands late. Give the driver a countdown
  delay after each SWAP; because it is ONE man, that delay directly gates the
  next ADDR. Under the judge's round gating the delay is free — the next
  round's input is withheld until the frame lands anyway.

## Sizing

Rooms total ~1200 boxed cells against the display's 884, so max-dim is
room-bound, not display-bound: the 35 floor the display implies is not
reachable with this room set. Footprint is the standing debt here, not ticks.

## The judge's verdict, and what variant A settled

**20/20 cases, 56x145, avgTicks 6941.25, score 145,939,781**
(id `e858a4d9-6fdc-4b82-ad75-d7b54260c096`). Judge/local = **x1.53** on
avgTicks (4548.83 local), the same ratio as reverse and sort.

Variant A passing EVERY case settles the whole probe plan at once: SWAP 0,
colour 15, one frame per round, no leading frame, no accumulation, (col,row)
coordinates. B/C/D were never spent. And **probe d5 is answered** — this world
has no output room at all and the judge accepted it, so a display-judged
program is not required to keep one.

## A LOAD ERROR that l2's linter cannot see

The first submission (`232dae69-...`) was rejected before running:

    expected a digit or a space between backticks, but found 's' at (16, 24)

Two of ONE room's own `32` literals landed in the same COLUMN with an `s`
between them. **l2's `check-literals!` has the column half backwards**: it
errors on a CLEAN paired span — which the judge accepts, it is simply a
vertical literal — and says nothing about a span containing an OP, which the
judge rejects. That is the same polarity bug NOTES already records for
sim.rkt's `literal-column-warn?`, so it is now confirmed in BOTH linters.
`judge-lint!` in `problems/plotter-sol.rkt` implements the judge's actual rule
(pair per row and per column; every cell strictly between a pair is a digit or
a space; spans <= 18 digits) and should be what the next literal-bearing world
uses. Judge coordinates are (col, row), again.

## The router order that finally worked

Four "no route" failures in a row came from ONE cause: the greedy router lays
channels in list order, and the only channel that is not a straight drop — the
ring's return leg — takes a long way round and consumes a corridor that a
later straight drop needs. **Route every straight channel first and the
wandering one LAST.** Likewise, when two pipes must pass the same gap, the one
with further to travel goes first (the SWAP before the ADDR and DATA).

## Honest negative: the footprint

56x145. Rooms total ~1200 boxed cells against the display's 884, and they are
stacked in ONE COLUMN because that was the only arrangement whose pipes would
route. area2 x avgTicks is 96% area. `floorplan.rkt`'s guillotine packer over
these same rooms should reach max-dim ~56-60 for a ~6x score improvement with
no change to a single op. That, not ticks, is the work left here.

## Correction to BOTH literal linters (2026-07-27, evidence-backed)

Auditing every shipped `.man` against the judge's own verdicts settles the
column rule, and the tree had it wrong in two different directions.

- **`l2`'s `check-literals!` errored on a CLEAN paired column span.**  The
  judge ACCEPTS those — a clean digit/space span down a column is just a
  vertical literal.  `history.man` carries **319** of them and `plotter.man`
  three; both are graded.  No *registered* solution happened to have one, which
  is the only reason this never fired, and it would have vetoed good floorplans
  silently as soon as one did.
- **It said nothing about a paired column span with an OP in it**, which the
  judge does reject.  Verbatim, from the plotter build's load rejection:
  `expected a digit or a space between backticks, but found 's' at (16, 24)`
  — judge coordinates are **(col, row)**.
- **But the fix is NOT the row rule applied to whole columns.**  Four
  judge-ACCEPTED worlds — `reverse.man`, `sort.man`, `snake.man`,
  `history-esc-stepcap.man` — carry column spans whose interior holds `s`, `W`,
  `m`, `M`, `v`, `<`, and **every one of those spans crosses a room wall**.  A
  wall glyph BREAKS the pair: the rule is per ROOM, not per grid.  Lifting
  plotter's whole-grid `judge-lint!` into l2 unchanged would have turned four
  graded solutions RED against files the judge has already accepted.

`check-literals!`'s column half is now: walk the column, restart the backtick
pairing at every wall glyph (`- | + = :`), and inside a segment require every
cell strictly between a pair to be a digit or a space.  **Flags nothing in any
shipped world** — 28 `.man` files at the time of writing, and that audit is
what gated this edit — while still catching
plotter's case, where both backticks and the `s` sat inside one room.
Re-verified GREEN and byte-identical AFTER the change: sudoku-station, sort,
reverse, brackets.  tcp and sudoku were verified GREEN before it and are
covered by the 28/28 audit rather than by a re-run (the tree had four agents
building concurrently and the re-verify made no progress in ~40 minutes).

# matmul: the LOOP ORDER is the architecture (judge 20/20, 55x63 @ 20618.55 = 81.8M)

`problems/matmul.rkt` (spec + all 7 public cases + load assertion + 12 stress
cases + a fuzz generator), `problems/matmul-sol.rkt`, `solutions/matmul.man`
(and `matmul-submitted.man`, the exact graded bytes). Local 55x63 @ 16631.3
avg emit; judge **20/20, avgTicks 20618.55, score 81,835,024.95**, submission
`d6a45b8e-c27e-409d-8004-4a4a442aee5f`, problem
`58f54636-3ec4-497d-8102-b486f13a1ed1`. Judge/local ratio **1.24x** — a third
data point for that table (reverse/sort 1.53x, memory 5.85x), and the lowest
yet, which fits the explanation: matmul's published suite already contains the
SPEC MAXIMUM case, so the hidden set cannot be much heavier than ours.

- **Take the loops in the order (i, t, j) and every stream is
  sequential-cyclic, so B never needs transposing.** The obvious order — one
  output element at a time — reads B with stride K, which on a ring costs a
  full pass per element, and the standard fix (transpose B on read-in) costs
  its own M*K rotations. With t as the MIDDLE loop the machine does
  `for i: for t: a = A[i][t]; for j: Cacc[j] += a*B[t][j]`, and then: A is
  read once front-to-back in arrival order, B is read one full cyclic pass per
  row of A, and the K accumulators cycle once per t. Nothing is ever indexed,
  nothing is ever transposed, and the whole solution follows. **This is the
  single decision that mattered; everything downstream is bookkeeping.**
- **A queue is not a ring, and a melted tank is already a queue.** A is
  consumed exactly once in arrival order, so it does not need a ring at all —
  it lives in the 262-cell `afeed` TANK between the loader and the multiplier,
  with no bouncer room and no rotation. Only B (read N times) and the
  accumulators (read N*M times) are real rings. Look for the once-consumed
  stream before building a ring for it.
- **Three live values per product (a, b, acc) is the B-pressure case, and the
  remedy is the room split** — MUL keeps `a` in B for a whole lap and never
  touches it (`(r bret) (s bout) * (s prod) m`: pop b, put it straight back on
  the ring, multiply by the resident, ship the product), while ACC keeps
  nothing across a product (`(r cret) M (r prod) + (s cout) m`). Both are
  5-6 op tight bodies; the two rooms pipeline through the `prod` pipe, so the
  cost is ~16 ticks per product, not 30.
- **ONE NEGATED CELL replaces every row counter in the system.** The row
  boundary is exactly the moment the B ring wraps, so F1 (the ring's bouncer)
  negates the LAST value it relays during the load — the ring becomes
  `[row0, K, row1, K, ..., row(M-1), -K]` and that one negative cell rides
  round forever, arriving at MUL exactly once per pass. MUL forwards each
  header to ACC as a per-lap flag (positive = accumulate that many, negative =
  the row is done: emit K values and push zeros back). Consequences: MUL never
  learns M or N, ACC never learns M or K after boot, P never counts B's rows,
  and ACC's ring holds ONLY the K accumulators. The draft it replaced carried
  `[K, L, M, c_0..]` in ACC's ring and cost three pops, three pushes and two
  extra chain cuts per lap.
- **The loader terminates by BLOCKING, not by counting.** P sends the K header
  AFTER each B row, so the loop that would have needed a third live value
  (outer row count + inner value count + the reload constant) just blocks on
  exhausted input after the last header. Emission-time scoring makes that
  free. Same trick as tcp's `lw`, one level up: if a loop's exit condition
  needs a register you do not have, check whether input exhaustion IS the exit
  condition.
- **`S` (send to ALL outgoing pipes) is the cheap way out of a column-band
  fight.** P must hand M and K to both MUL (via afeed) and F1 (via bfeed), and
  a chain holding `(s afeed) (s bfeed) (s afeed) (s bfeed)` is unlayable at
  every width — the two channels are opposite column bands and the ops
  alternate. `S` has no channel at all, so both copies leave in one op and the
  band constraint evaporates. First use of `S` in this repo.
- **A tight body's op order IS its column order, reversed** — l1 lays the body
  westward under the head — so the bands a room can accept are read off its
  bodies, not chosen. ACC's emit body `(r cret) (s out) 0 (s cout) m` forces
  cout=west, out=east AND cret=east, which then forces prod=west and forces
  the accumulate body to be written `(r cret) M (r prod) + ...` rather than
  the other way round (both compute the same sum). Getting this backwards
  produces "no feasible layout" at every width with no other diagnostic. Write
  the bodies down, read the offsets off them, and only then pick the bands.
- **Two big melts starve each other in one field; give each its own.** With
  `afeed` (262) and `bout` (276) melting into a shared region, whichever went
  first filled the entrance and the second reported "no sweep works" four
  cells in — at every field size, including one twice as big as both tanks
  together. The fix is two fields side by side with the tank's DESTINATION
  ROOM directly below its own field, so each snake grows downward and glues a
  few cells later. Before that, `bout` repeatedly grew its full 276 cells and
  then failed with NO GLUE, which is the same lesson from the other side.
- **Room bounding box = the world.** l2 clamps a melt to the box over the
  ROOMS, so a field only exists if some room sits south of it; F1 and ACC at
  the bottom are load-bearing floorplan elements, not just rooms that happened
  to go there. Empty canvas outside the box is not space.
- **The routing failures rotate, and each one names the wrong culprit.** Over
  ~25 build attempts the same floorplan reported, in turn: "no free wall cell
  for channel bfeed" (gap too small for the 2-cell clearance rule), "no
  in-attachment satisfies targeting" (bands read off the wrong body), coincident
  F2 segments (`cout` and `cret` assigned the same cell on a 5x2 room — NOTES
  landmine 4, still live), "cannot route channel bret" (the corridor was outside
  the room bounding box), a 103-cell `in` pipe between two FLUSH rooms (no legal
  hook existed between the cells the solver picked, so it wandered), and finally
  the two melts above. The one habit that paid: after each failure, print the
  room boxes and the chosen attachment cells (`#:verbose #t` plus a one-line
  room dump) rather than re-guessing the geometry.
- **Sizing the tanks is a DEADLOCK argument, not a performance one.** `afeed`
  must hold all of A (N*M = 256 plus the two broadcast dimensions), because P
  cannot start the B phase until every A value is out of its hands. `bout`
  must hold M*(K+1) = 272, because during the load phase F1 is busy relaying
  `bfeed` and is NOT draining `bout` while MUL is already running laps and
  pushing recycled values into it. Anything smaller deadlocks the whole ring
  P -> bfeed -> F1 -> bret -> MUL -> bout -> F1.
- **F1 must not use `R` (read any).** During the load both of its incoming
  pipes have values — the arriving B stream and the values MUL has already
  recycled — and `R` interleaves them, which scrambles the ring's order
  silently. The load-then-bounce structure (relay a counted prefix from
  `bfeed`, then bounce `bout` forever) is what keeps the two streams in order,
  and the count is computed by F1 itself from the M and K that P broadcast.
- **Validate the algorithm BEFORE the floorplan.** A ~120-line block-level
  interpreter of the CFGs (registers + FIFO channels, no geometry) ran the 7
  public cases, 12 stress cases and 200 fuzz cases in seconds and caught the
  one real logic bug (the per-lap flag was off by one: MUL owes ACC an extra K
  at boot because the first flag is consumed by the zero-fill). Finding that
  through l2 would have meant a 3-minute build per iteration. The interpreter
  lives in the scratchpad, not the repo, but the pattern is worth repeating:
  the CFG and the world are independent, and only one of them is slow.

# DISPLAYS in the layout TOOL and in l2 — the tool's bug was a STALE SERVER, and l2 can place a display now (2026-07-27)

Owner of this section: the display-layers agent.  Files edited:
`tools/layout/{engine.rkt,index.html,manifests.rkt,README.md}`, `l2.rkt`
(additive: a new room kind), `display-world.rkt` (deprecation header).  New:
`tests-l2-display.rkt` (35 checks).  Nothing submitted, no `.man` changed.

## The tool "dropped" snake's display because the SERVER PROCESS was older than the feature

The lead loaded `solutions/snake.man` in the layout tool and the 16x16 display
was simply missing from the render.  It was not a renderer bug, a parse bug or
a payload bug: **`index.html` is read from disk on every request, but
`engine.rkt` is compiled INTO the running server process.**  `ps` said the
server started 16:18:32; `ls` said engine.rkt landed its display support at
16:40:40.  For 22 minutes onward the tool served a display-blind engine behind
a display-aware UI.

Verbatim, what the stale process returned for snake.man:

    rooms [('R0','in'), ('R1','normal'), ... ]        # six rooms, no display
    pipe roles [(P0,None) … (P5,None)]                # no roles at all
    issues ['stray pipe glyph at (0,31)', … 44 of them]

and what a fresh `racket -e '(require "tools/layout/engine.rkt") …'` returned
from the SAME file at the same moment:

    R1 display D dw=16 dh=16
    P1 R2->R1 role ADDR · P2 R2->R1 role DATA · P5 R2->R1 role SWAP
    issues: ()

**The diagnostic that costs ten seconds: if the tool disagrees with a fresh
`racket -e` against `engine.rkt`, restart the server before investigating
anything.**  Restarting fixed the render, the roles, the pixel grid and all 44
phantom issues at once.  This is now the first entry under the README's known
limitations.

## Three real gaps that the stale server was hiding

1. **`validate` had no display problems in it.**  `engine.rkt`'s
   `problem-files` table listed seven ring problems and none of the display
   ones, so the button could only ever go green on snake by validating it
   against `memory`'s tests.  Added `snake` / `plotter` / `pathfinder`, plus a
   `display-res` side table (mirroring `harness/problems.rkt`'s
   `display-problems`, and a side table for the same anti-collision reason)
   that switches `/api/validate` to the judge's **streaming frame compare**:
   `display-judged?` on, frames compared in order, the case scored at the tick
   of the final matching frame.  Neither the expected nor the got frame
   sequence is shipped to the browser — a 16x16x11 sequence is the thing that
   must not cross the wire — so a failure carries driver.rkt's one-line detail
   instead.  snake.man now validates 5/5, `avgEmit 5625.4`, which is the
   number CURRENTSCORES records for it; plotter.man 6/6, `avgEmit 4549.3`.

2. **The problem select never auto-picked.**  `probSel` was set from
   `p.manifest`, and a hand-assembled display world has no channel manifest,
   so loading snake.man left the target on whatever was there.  `parse-grid-text`
   now also reports `'problem` (the file-name stem, via manifests.rkt's
   `problem-of-name`), and the UI falls back to it.

3. **THE AUTO-ROUTER WAS NOT DISPLAY-AWARE, and the failure was silent.**
   This is the one worth remembering.  Nudging snake's painter room one row
   and letting the "attachments follow the room" reroute run produced a grid
   that PARSES, has zero broken channels, and is a **load error**:

       display at (1,39): a pipe flows OUT of the display at (19,40)
       roles=[('P1','ADDR'), ('P2','DATA'), ('P5','DATA')]

   The SWAP pipe came back as a second DATA pipe — the frames would have gone
   wrong with no error anywhere — and a bend under the display's bottom wall
   became a candidate walk out of the display.  Two rules now ride the
   `/api/routepipe` payload (`displays`, `role`), and neither relaxes under
   the router's permissive fallback, because both are LOAD rules:

   * **no arrowhead may have a display wall behind it** — not the start, not a
     bend, not an edge bump's new corner.  A display is a pipe DESTINATION
     only, and the judge validates that over the candidate walks, rivals
     included, so reading-order arbitration never saves it.
   * **the side is the function**, so a reroute is pinned to the wall its ROLE
     names.  The client keeps the last FUNCTIONAL role (`roleWas`) precisely
     because a `RIGHT`/`CORNER` attachment carries none.

   A `RIGHT`/`CORNER` attachment is now a **broken** channel rather than a
   listed issue, which is what puts it back through the router on a drag
   instead of leaving it silently wrong: dragging the display one column used
   to leave its ADDR pipe attached to the new top-left corner, status "ok".

   And one ordering fact that is not display-specific but only bites displays:
   **display pipes must reroute FIRST.**  They are pinned to one wall of one
   side of one room and lose every lane race — measured on snake, the 50-cell
   C-pipe takes the corridor under the display and the SWAP pipe then has no
   legal route at all ("no route inside the bounds"), while routing it first
   succeeds at 20 cells.  Both `afterRoomMove` and `rerouteAll` now order that
   way.

   End state, from a scripted replay of the UI's own drag path: painter +1
   row, painter back, and the DISPLAY itself +1 column — **zero broken pipes,
   zero issues, ADDR/DATA/SWAP all preserved, and the dragged grid still
   validates 5/5 (58x51, avgEmit 5631.8 vs the original 57x51 / 5625.4).**

Regression: all 28 `solutions/*.man` parse + check + recompose byte-identical
with zero issues; `tools/layout/test-roundtrip.rkt` 51/51.

## l2 CAN PLACE A DISPLAY NOW — the note at "l2 CANNOT ASSEMBLE A DISPLAY" is superseded

`grep -c display l2.rkt` was 0 and three separate agents recorded it
independently (pathfinder built `display-world.rkt` around it; snake and
plotter hand-assembled).  `l2.rkt` now has a fourth room kind:

    (display-room 'D 16 16 '(1 . 39))      ; => (room-spec 'D 'display '(16 . 16) '(1 . 39))
    (assemble rooms chans #:display-roles (hash 'addr 'addr 'data 'data 'swap 'swap))

The edit is deliberately small, because almost nothing about a display is
special to an ASSEMBLER:

* `add-room!` gets the resolution from `layout` (a `(w . h)` pair instead of a
  `cfg-layout`), stamps `+`/`=`/`:` instead of `+`/`-`/`|`, and stamps nothing
  inside.  Everything else — occupancy, the box-overlap rejection, `inside?`
  keeping the router out, the perimeter attachment search, world compaction,
  the literal lint — already works on any rectangle.
* **Gravity is rigid for free.** Deltas only ever move a room ORIGIN, and a
  display has no interior for a move to corrupt; a placement that overlaps it
  or routes through it is already infeasible.  Nothing was added for this.
* **Compaction cannot collapse a display** either, and the reason is worth
  writing down because it is not obvious: `render` drops fully empty rows and
  columns, and a display's interior is blank — but every interior COLUMN
  carries an `=` on the top and bottom walls and every interior ROW carries a
  `:` on the left and right, so no line of the box is ever empty.
* `#:display-roles` is a SIDE TABLE keyed by channel name (`'addr`/`'data`/
  `'swap`), not a fifth `chan-spec` field: `chan-spec` is positional and
  constructed in every sol file, so growing it is the edit that collides with
  everyone.  A role both **restricts the attachment search to that wall** and
  is **re-checked against the committed cell**, so a `#:fixed` pin gets the
  same treatment — the rules are the judge's, there is no opting out.
* `io-room?` (the level-1 hazard predicate that forbids wall-backed arrowheads
  near I/O rooms) now includes `'display`, since both halves of its reasoning
  apply verbatim.  Byte-identical for every existing build: no shipped world
  has a display.

Four load rules are refused at ASSEMBLY time with a sentence naming the
channel: a pipe out of a display, a corner, the right wall, two pipes on one
side — plus the 64x64 resolution limit and a role that disagrees with a pinned
cell.  One of them has to be checked EARLY, before the attachment search: a
display can have no outgoing candidate at all, and the search's own failure on
an empty candidate list is `first: contract violation` from inside
`solve-room`, which tells the caller nothing.

`tests-l2-display.rkt` is the worked example: an l2-assembled display + two
driver rooms commits `tests-display.rkt`'s bench frame, passes under
`display-judged?` at the stated resolution, survives seven gravity nudges and
a `gravity-optimize` run with the display intact, and is re-parsed by the
LAYOUT TOOL (an independent copy of sim.rkt's parser) as one 2x2 display with
DATA and SWAP roles and zero issues.  35 checks, all green.

**`display-world.rkt` is deprecated** with a header pointing at l2.  Nothing
requires it — only comments do.  It stays because two builds in flight were
written against it (`problems/pathfinder-machine.rkt` designs to it,
`problems/plotter-world.rkt` is a bounded-router fork) and because its
unbounded uniform-cost route is an independent check on l2's BFS.  Do not add
a caller; port instead.

**FOR THE FLOORPLAN OWNER:** `floorplan.rkt`'s header says "l2 cannot place a
display at all … those origins must then be handed to display-world.rkt".
That is now false in the useful direction: `fp-fixed` already packs any
rectangle, so a display box packed at `(w+2) x (h+2)` can be handed straight
to `(display-room name w h origin)` and assembled by l2 with the rest of the
world.  The comment is yours to update; nothing in floorplan.rkt was touched.

## Honest negatives / residual risk

* The six ring problems' byte-repro is the gate on the l2 edit and was run
  before and after.  `subset` fails to BUILD in both runs
  (`vector-ref: index is out of range for empty vector`) — that is
  pre-existing and belongs to whoever owns subset, not to this change.
* The tool's `problem-files` table still omits `matmul`, `sudoku`,
  `sudoku-station`, `gradebook` and `subset`; only the three display problems
  were added, because those are what this task was scoped to.  Adding a row is
  two lines and cannot break anything else.
* `#:display-roles` restricts the SEARCH but does not RANK inside the chosen
  wall, and it knows nothing about NOTES' "the display's three pipes must be
  length-matched (ADDR vs DATA)" constraint — `LD - g2 < LA < LD + g1` is a
  timing property of the routed lengths, and l2 will happily hand back an
  18-cell ADDR against a 9-cell DATA, which paints every pixel at the previous
  address and looks plausible.  Keep snake's `|LA - LD| <= 3` build-time
  assertion in the sol file; l2 does not replace it.

Regression run at the end of this session, one process per chunk:
`verify memory reverse sort brackets tcp sudoku sudoku-station snake plotter`
= **9/9 GREEN**, every repro byte-identical, every literal lint clean;
`tests-display.rkt` 0 failures, `tests-foldback.rkt` 0 failures,
`tools/layout/test-roundtrip.rkt` 51/51, `tests-l2-display.rkt` 35/35, and the
full `all-problems` byte-repro table identical line for line to the run taken
BEFORE the l2 edit (same dimensions, same `subset` build error).

One operational note that cost time and is already in the PLAYBOOK: a
backgrounded 25-minute racket run **silently restarts**.  Two of them did,
showing `ELAPSED 00:29` half an hour after launch.  `verify` and the repro
sweep both had to be chunked into foreground calls under 600s.


# Subset: the STATION CHAIN — the ring machinery DISSOLVES, and l1 still refuses the room (2026-07-27)

`problems/subset-station-sol.rkt` (block-level green, **no grid**),
`kernel/mansim.rkt` (new, reusable).  Read this before re-attacking subset:
three of its results are not about subset at all.

**(1) THE RECURSION IS THE CHAIN, and that kills the whole backtrack
problem.**  Station i's man holds `v_i` in B forever and IS DFS level i.  A
descend is one pipe hop down; the man then BLOCKS on its child's answer with
its own `r` still in A.  **The DFS stack is the chain of parked men** — there
is no stack data structure.  Everything the two earlier subset entries built
for the ring evaporates: no mark-scan, no rotation, no "backtrack costs a full
lap, not `n-k`", no re-fetch of `v_p`.  The parent never lost `r`.  Cost per
node is a constant two hops instead of O(n) rotations.  The follow-up entry's
result (1) is TRUE OF RINGS ONLY and should not be carried forward as a fact
about the problem.

**One word per message, and the sign is the whole protocol.**  Down: `r`,
always > 0, because the parent screens `c == 0` (its own win) and `c < 0`
(skip the include).  Up: **the r I was given** (> 0) = fail, anything < 0 =
success.  Returning the value you were given is the load-bearing choice — the
parent's A is destroyed by reading the answer and `r` lives nowhere else, but
the answer IS `c`, so one `+` restores it (B survives every arith op; only `/`
writes B).

**(2) A STATION CANNOT HOLD A PACKED WORD.  This generalises past subset.**
Unpacking needs the divisor or shift count in B, and every constant-building
op (a digit, a backtick literal) writes A — so the only way to load B is
`M`/`W` from A, i.e. *the constant must be in B before the value arrives in
A*.  A resident packed word already occupies B and can therefore never be
unpacked in place.  **LAW: one resident constant per station man, used
directly.**  Corollaries: the "3 values per 64-bit register across ~7 men"
sketch is not buildable; and `hcap` is refused a SECOND time, independently of
the two-register argument above — `/` writes the remainder into B and would
destroy the resident `smin_i`.

**(3) THE PRUNES BUY BACK EXACTLY THE ROOMS THEY COST — measured, and it
inverts the obvious answer.**  One prune needs one resident constant, hence
one more room per index.  Worst-case *visits x rooms-per-index* over 300
random n=20 in-box cases:

| prune set | worst visits | rooms/idx | product |
|---|---|---|---|
| bare (undershoot+terminal) | 1,545,547 | 2 | 3.1M |
| +under | 726,854 | 4 | 2.9M |
| +under+smin | 515,590 | 6 | 3.1M |
| +under+maxcap | 463,195 | 6 | 2.8M |
| all four (+hcap) | 414,728 | 10 | 4.1M |

Flat.  Area is SQUARED in the score and the typical case is small, so **fewest
rooms wins outright**: 20 stations, bare prune set.  The full public/stress
table is `scratchpad/subset-station/nodes.rkt`; `maxcap` alone still collapses
the big-element trap from 1,572,863 visits to 1, and `hcap` alone collapses
all-equal and near-uniform to 1, so a room-cheap way to get either would be
worth real money.

**(4) `kernel/mansim.rkt` — a MULTI-MAN cfgsim, and the landmine inside it.**
`kernel/cfgsim.rkt` runs one man; a station world is 22, and the entire
question is the protocol between them.  `run-men` takes `(name blocks entry)`
triples, shares named FIFO channels, and round-robins.  It found 7/7 public +
120/120 battery on this design before any layout existed.  **A man that blocks
on a read STALLS AT THAT CELL.**  The first version rolled the block back and
re-ran it, which re-executed every `s` before the read and silently DUPLICATED
SENDS; it presented as a hang and cost a hand-written trace to find.  Hence
the intra-block op index.  Anyone simulating multiple men needs this.

**(5) THE REFUSAL: l1's wall is CHAIN COUNT, not block count.**  Bisected on
the station room:

| room | blocks | chains | result |
|---|---|---|---|
| search half, `head` 2-way | 18 | 8 | 18x15 |
| emit half | 11 | 6 | 15x13 |
| both | 23 | 13 | **REFUSED** |

Refused at every width 12..33 (and explicit widths to 62), in BOTH engines
(shelf and `#:melt`), `#:restarts` to 24, and over an explicit width x height
grid to 30x44 — always the diagnosis-free `no feasible layout`.  The
controller (15x8) and terminal (13x12) lay fine.  Also tried and still
refused: merging `iskip` into `ilost`; routing `padf` through `elost`; folding
the relay arm into a single `head -> hem -> htok -> hdone` chain so `head` has
one fall-through instead of two rails.  A rewrite using **BP as the emit pass
counter** (`2 b` at read-in, one `m` per token, `d` picks the pass) took the
room from 27/17 to 23/13 and did not cross the line.  Do not re-run these.

The remedy is CLASSES' own: split the room.  Both halves are known to lay at
known dimensions, so it is search-room + emit-room, 40 stations, and the two
open questions are (a) whether E_i sits IN the chain (doubles the hop count,
which is the architecture's whole advantage) or off to the side (a fifth and
sixth pipe on S_i, which is already at CLASSES' four-pipe wall), and (b) how
E_i learns "am I included" — one marker sent downstream at `iwin`/`iwon`,
which E_i consumes rather than forwards.  `v_i` is free either way: the
read-in stream passes through E_i too.

**Honest hole, unchanged:** n=20 dense-random-no-solution and the n=20
big-element trap exceed the 15M cap under the bare prune set.  All seven
public cases fit with margin (worst is near-total-sum at 907,831 blocks).
**Nothing was submitted** — there is no grid to submit, and the id
`b5e48adc-317d-480d-88a4-e2edc659453a` is still unspent.

# Memory, SHARDED STATION CHAIN: the protocol is green, the ROOM is a four-pipe refusal (2026-07-27)

`problems/memory-station-sol.rkt` (new), `kernel/mcfgsim.rkt` (new, a
MULTI-ROOM cfgsim, self-check green).  **No submission**: the world does not
assemble.  `solutions/memory.man` (33x33 @ 66,543,935) is untouched and is
still the Memory best.  Nothing else in the tree was edited.

## The fact that reframes this whole problem: MEMORY IS SINGLE-ROUND

Already in this file ("Resubmission round": *"Memory is single-round, so this
is not the withheld-input effect"*) but never used as a DESIGN input.  It
means the 1000-token stream is fed continuously, so a chain of rooms is a
PIPELINE: the score is set by the SLOWEST STAGE, not by the path length.
**Room count is nearly free in ticks and costs only area.**  That inverts the
usual trade — sudoku's "prefer SHORT pipes between rooms that talk each round"
is a GATED-problem rule and does not apply here — and it is the entire reason a
station chain is worth considering for memory at all.

Corollary worth carrying: on a single-round problem, price a design by
`max over rooms of (that room's ops per input item)`, not by the sum.

## The spec bound nobody had written down

memory.md, Constraints: **"The operation stream contains between 2 and 1000
input tokens."**  So <= 500 ops, and the 100-address stress (write 0..99, read
0..99) is 500 tokens — only HALF the spec box.  `s-allread` (500 reads = 1000
tokens) and a 996-token mixed case are both inside it and both heavier.

## The architecture, and the three ideas in it that are reusable anywhere

`I -> C -> S0 -> ... -> S7 -> T -> O`; station i owns a shard of addresses in a
POSITIONAL private tank (slot j is j rotations in, no compares).

1. **THE RUNNING-OFFSET HEADER.**  Station i keeps `B = WM` permanently; its
   head is `(r g) - X`.  `x < WM` -> ccw, MINE, and `+` recovers the slot
   index; otherwise A is ALREADY `x - WM`, the next station's header, so the
   decrement costs no op.  Ownership as `0 <= x <= WM` (not `x < WM`) is what
   makes RELAY THE CW ARM ALONE and therefore `#:tight`-able; the `x < WM`
   split puts both the straight and the cw arm on the relay path and costs a
   duplicated block.
2. **A RESULT IS ITS OWN HEADER.**  A read replies `(v, v)`.  Stored values are
   biased by `BIAS = 9^8 = 43,046,721` (seven digit cells, `9 M * M * M *`, no
   backtick literal), so a result header is ~4.3e7 and stays hugely positive
   through every remaining station (it only loses WM per hop) — always relayed,
   and T ignores headers.  No marker literal, no ordering problem: `s`
   preserves A, so `(s n) (s n)` ships the pair in two cells.
3. **ORDER IS PRESERVED FOR FREE** because a station rewrites IN PLACE: the
   reply sits exactly where its request sat in the FIFO.
4. **THE PREAMBLE, not a per-station fill.**  C emits SLOTS copies of BIAS then
   the sentinel; every station keeps a copy in its tank AND forwards the whole
   preamble.  One constant build and one counted loop serve all stations —
   worth 7 op cells and a whole block PER STATION, which is what this
   architecture pays in.
5. **ROTATION IS A CYCLIC SHIFT**, so a value replaced mid-lap lands back in
   its own slot.  WRITE is `(s t) (r t)` IN THAT ORDER (append at the tail,
   drop the head); READ is `(r t) (s t)`.  The lap is closed by rotating until
   the negative sentinel comes round — sign-divert again — which is what avoids
   a SECOND counter, and a second counter is exactly what the station cannot
   afford: BP is the first one and `+`/`-` need B, which is nailed to WM.

## kernel/mcfgsim.rkt — cfgsim for N ROOMS

`kernel/cfgsim.rkt` runs ONE CFG; a station chain is ten cooperating rooms, and
the interesting bugs (phase, ordering, who consumes the preamble) are all
BETWEEN rooms.  `run-rooms` is the same idea with a scheduler: named FIFOs,
blocking receives, round-robin to quiescence, and **per-room op-level parking**
— a starved `r` parks the room MID-BLOCK and is retried, so no side effect is
ever replayed.  Same caveats as cfgsim (no layout, no ticks, no capacity, no
targeting), and it is pinned the same way: its `module+ test` runs the memory
station chain and requires memory's published outputs.

It found real bugs before any room existed and it is problem-agnostic — reach
for it the moment a design has more than two rooms.

## THE WALL: A STATION IS A FOUR-PIPE ROOM, and l1 refuses it

`assemble: room S0: no out-attachment satisfies targeting`.  A station needs
`g` in, `t` in, `n` out, `t` out — and CLASSES already names four pipes on one
room as the limit of l1's targeting model.  Three escalating attempts, each a
stronger refusal than the last:

1. `#:strict-bands? #t` with `#:col-order '((r g t) (s n t))`: **empty menu** at
   every width 12..46 AND at every explicit `#:split` 4..16.
2. Soft bands: a menu, but the ops interleave — `r g` at columns 1,2,7,5
   against `r t` at 6,8,8,9 — and l2 refuses.
3. An `#:accept?` veto asking **l2's own question** (is there ANY pair of
   west/east wall ROWS under which every op is strictly nearer its own
   segment?): false for every layout at every width.  That is a certificate,
   not a tuning failure.

**Three band landmines found on the way, all of which cost a cycle:**

- **`chain-bands` merges READS AND SENDS into ONE (woff, eoff) per lane.**  It
  is not per-kind.  So a lane holding an EAST read and a WEST send is
  unsatisfiable at every width no matter how its ops are ordered — which is why
  `sread` had to be split into `(r t)(s t)` and `(s n)(s n)`.  Registers
  survive a goto, so splitting a block costs a rail and nothing else.
- **A `#:tight` BODY'S LANE IS WALKED BACKWARDS, so its band sense INVERTS.**
  `sfbody` wants `(s t) (s n)` — the tank send FIRST — to put the tank op in
  the EAST band, the opposite of what the same pair needs in a normal eastward
  block.  Nothing warns you; the partition just reports illegal.
- **`d`/`x` straight arms are FORCED fall-throughs**, so two blocks that must
  live on different lanes need a ZERO-OP JOIN between them (`sjoin`, `sjoin2`
  here).  A zero-op block is free in cells and buys a lane break.

Also, plainly: **a wrong chain list is an EMPTY SHAPE MENU, not a worse room.**
The first station compile returned `'#()` at every width because the tight
bodies were listed in `chains` and the fall-throughs were the cw arms rather
than the straight ones.  `chain-partitions` RAISES on an illegal caller
partition and that error is the fastest diagnosis available.

## What it would score, and the honest trade

Measured rooms after a `chain-partitions` x `chain-order-variants` search:
station **21x9 = 253 boxed cells**, C 17x7 = 171, T 15x4 = 102.  A tight-loop
iteration is a 2-row circuit (~8 ticks a cell), so the station term is
`~8 + 8*(SLOTS+1)/SHARDS` ticks against the shipped ring's `~12.65 * (distinct
addresses)` — at SHARDS = 8 that is **~24 ticks/op against ~1265** on the
100-address case, a 15-20x tick win, and it is flat in SHARDS from 5 to 12
(the relay floor and the amortised lap trade against each other).

**And the area gives most of it back.**  Ten l1 rooms at ~250 cells is ~2500
committed cells, md >= 50, where the shipped ring is 33x33 = 1089.  Projected
**~10-15M against the shipped 66.5M and a field top of 5.05M**.  So: the
architecture is right about the ASYMPTOTE and expensive in the CONSTANT, and
the constant is *l1 room density* — 30 ops became 189 interior cells (16%),
which is the same 13-22% every l1 room in this tree lands at.  sudoku-station's
serpentine is the only thing in the repo that beats it, and a station cannot be
branchless: its loops are the point.

## The fix that was designed and not built

Split the station the way memory itself is split — `C` is 2-in-1-out, `F` is
1-in-2-out, which is exactly why the shipped ring never hits this wall.  SA
keeps the CFG as written but with `g`/`u` in and ONE outgoing pipe `o`; a tiny
SB (memory's F is 5x2) reads `o` and routes by SIGN: `X` cw to the chain,
otherwise `N` and back into the tank loop.  Three cheap encoding changes make
the sign a valid router, and they are the part worth keeping:

- SA marks every tank-bound value with `N` — one cell, and B-preserving, which
  matters because B is nailed to WM;
- the tank sentinel becomes **0** instead of -1, so `X` still closes the lap
  (straight = sentinel, cw = data) and negating it keeps it non-positive;
- the READ payload becomes **1** instead of -1, so every chain-bound value is
  strictly positive; `satgt` then discriminates with `- X` against B = WM
  (`1 - WM < 0` = read, `stored - WM > 0` = write) and `+` restores it.

That leaves SA with ONE same-kind pair to separate instead of two — the
configuration matmul's MUL/ACC (`#:col-order '((r afeed bret) (s prod bout))`,
`#:strict-bands? #t`) and memory's own C are shipped on.  It costs SHARDS extra
tiny rooms, which on the numbers above is ~600 more cells and pushes the
projection toward the top of the 10-15M band — so whoever picks this up should
decide whether that trade is worth making at all before writing the code.

## Honest negatives, with numbers

- **B-RESIDENT STATIONS ARE IMPOSSIBLE, and this is the finding that killed the
  brief's headline design.**  100 values x 21 bits = 2100 bits; B gives 64
  bits, so 3 values a man and 34 stations.  But a station whose B holds the
  DATA has only A as scratch, and EVERY arithmetic op on this machine takes B
  as its operand — so such a station cannot decrement, shift, compare or mask
  a dispatch selector at all.  BP does not rescue it (`b`/`m`/`]`/`d`/`a`/`x`
  can only count and test bits, and BP CANNOT BE READ BACK).  The only escapes
  are a per-station `m` count (linear cells: station 33 needs 33 of them) or a
  per-station literal (a different room per station).  **The dispatch constant
  and the data cannot share B**, which is why every station here owns a tank
  and why the count is 8 and not 34.  Register residence is a fine idea for
  sudoku, where the state IS the thing being tested; it does not survive a
  problem where the state must be ADDRESSED.
- 34 register-resident stations, priced anyway: ~48 boxed cells each if they
  could be serpentines, 1632 cells, md >= 46 — and they cannot be serpentines.
- Packing 3 values per tank cell (34-cell global ring): shortens the lap 3x and
  needs shifts, which need constants, which need B.  Refused for the same
  reason as above.
- Single positional ring, no sharding (the cheap version of this design): a lap
  is ~101 cells x ~3 ops, ~300 ticks/op, ~28M.  With 3-value packing ~105
  ticks/op, ~12M at md 30 — better than shipped, worse than sharded, and it
  hits the SAME four-pipe wall on C.
- `const-ops` covers 0..99 with `a M b * M r +` and no backtick literal;
  verified against `kernel/isa.rkt` for every n in 0..99.  A literal is a
  room-width floor, and this file has none anywhere.

# Sort as a streaming compare-exchange network: the protocol WORKS, the AREA does not (2026-07-27)

Brief: the field's 250K vs our 4.19M on sort says "sorted in flight, not sorted
in storage" — build a systolic insertion array, sixteen register-resident
stations in a chain, values stream through.  The protocol was designed,
validated end-to-end, and then **priced and rejected on area**.  Files landed:
`kernel/netsim.rkt` (new tool), `probes/sortnet-proto.rkt` (the validated
protocol).  `problems/sort-sol.rkt` and `solutions/sort.man` untouched.

## The verdict, as a table (this is the whole entry)

Score is `max(w,h)^2 x avgTicks`.  Shipped ring sort: 26x28, local avg 3484.9,
**local score 2,732,128**; judge x1.535 -> 4,193,459.

| station room | area2 (guillotine, MEASURED) | T (ticks/value) | avgTicks | local score | vs ring |
|---|---|---|---|---|---|
| l1-compiled, 21x11 boxed | no plan under 60x60 (>=3600) | ~30 | ~2300 | >8.3M | **0.3x** |
| hand-laid 11x8 (realistic) | 41x41 = 1681 | ~21 | ~1630 | 2.74M | **1.0x** |
| hand-laid 10x7 (optimistic) | 37x37 = 1369 | ~17 | ~1320 | 1.81M | 1.5x |
| 9x5 (unreachable floor) | 31x31 = 961 | ~12 | ~930 | 0.90M | 3.0x |

The architecture's **ceiling is ~3x and its realistic value is ~1x**, before
paying the judge's round-gating penalty — which is WORSE for a deep pipeline
than for a ring (sudoku's lesson), so the realistic column probably loses.
Sixteen rooms cost ~2.1x the ring's area, i.e. **4.6x in the score**, and the
tick win is only ~2.1x.  That is the entire finding.

Tick model, if you want to re-derive it: per round the last output leaves at
`(2n + K)` station-steps (K = 16: n loads, the DRAIN walking the chain, then
n drained values pipelining out).  Summed over the 7 public cases and averaged,
`avg over cases of sum over rounds of (2n + 16)` = **77.7 station-steps**, so
avgTicks = 77.7 x T.  Area numbers are `floorplan.rkt`'s `guillotine-search`
on 16 station boxes + D + F + I/O, before pipe-routing feasibility, so they are
OPTIMISTIC.

## Why T cannot reach the belt's 2.3 t/v: THREE REFUSAL CERTIFICATES

ARCH's 2.3-4 t/v is a BRANCHLESS dense relay tile — many `r`/`s` sites per walk
lap.  A compare-exchange branches, so a station pays a whole walk lap per value
and its cost is set by the room's PERIMETER, not by its op count.  The only way
out is a branchless compare-exchange, and `kernel/enum.rkt` says there isn't
one in reach (spec: start `A = x, B = s` -> `sent = min(x,s)`, `B = max(x,s)`):

    cmpex-plain  {+ - W M N & | ~ s}                 7 cells,  558k states — EXHAUSTED
    cmpex-shift  {+ - W M N & | ~ } { s `63` `15`}   7 cells,  941k states — EXHAUSTED
    cmpex-cubby  {+ - W M N & | ~ } s `63` s$ r$}    7 cells, 2267k states — EXHAUSTED

The third one is the informative one: **even with the modelled cubby** (a
second pipe pair = a third register) there is no 7-cell sequence.  The
sign-mask form `min = s + (d & (d>>63))` has three simultaneously live values
(d, s, mask) plus the constant 63 against two registers, and it is 8+ cells
before the send.  Read `certificate-text`: a longer sequence or a different
DATA LAYOUT could still dissolve it, and the data-layout escape is the one to
try next (see "what would actually be worth building" below).

## The protocol itself is CORRECT and is kept: `probes/sortnet-proto.rkt`

12/12 (7 public + 5 spec-maximum stress) in `kernel/netsim.rkt`.  Four things
in it are reusable and were expensive to find:

- **The hot path is FOUR OPS.**  With `A = x` (received) and `B = s`
  (resident), `-` gives `A = x - s` in ONE op because `-` is `A-B` and the
  resident value is already the subtrahend; then the two arms are `+ W (s n)`
  and `+ (s n)` — they differ by exactly one `W`.  That is sort-sol's `+ W s`
  scan body one level up.
- **THE RELAY MODE IS NOT CODE.**  After it drains, a station must forward what
  its upstream neighbours drain.  Setting `B := INF` buys it for free: every
  arriving value loses the compare, so the compare-exchange loop IS the relay
  loop.  The first draft had an explicit relay mode (a second `r`, a second
  loop head, a second junction) and deleting it removed four blocks.  Generalise
  it: **a resident sentinel can replace a mode bit** wherever the mode only
  changes which arm a compare takes.
- **Tokens are told apart BY SIGN, so dispatch is one `X` on the raw word.**
  `LOADTOK = -1`, `DRAIN = 0`, reals biased to `[1, 20001]` by D and un-biased
  by F.  Three sign classes is exactly three protocol classes; wanting a fourth
  is what forces a second test, and that is where the design got expensive.
- **DRAIN ORDER IS SET BY ONE LINE.**  Station i on DRAIN sends DRAIN, then its
  OWN B, then relays, so S15 emits `[DRAIN, B_15, ..., B_0]` = ascending.
  Relaying first and sending own-B last gives exactly the reverse.

## `kernel/netsim.rkt` — the multi-room analogue of `cfgsim.rkt`

cfgsim runs ONE CFG; a station world is twenty rooms and its bugs are in the
PROTOCOL.  netsim runs rooms as threads over unbounded blocking FIFOs, with
`isa.rkt`'s op table, so the arithmetic cannot drift.  It found both real bugs
in the first run, minutes after the CFG was written and hours before any room
was laid out:

1. **The value an EMPTY station forwards aliased the DRAIN token.**  Fill = 0 =
   DRAIN, so every station downstream drained mid-round.  The symptom is the
   killer: output of the RIGHT LENGTH and the WRONG ORDER, which reads exactly
   like an ordering bug in the sort.  Fix: an empty station forwards nothing
   (`keepx` tests A after `+ W`, which is free — A is already the resident
   value there).
2. The drain order above.

Because rooms are threads the interleaving is arbitrary, which is a FEATURE for
protocol testing (a protocol that works under only one schedule flakes here)
and useless as a tick estimate.  It models no layout, no ticks, no pipe
capacity and no targeting; `steps` counts blocks.  Self-check: `raco test
kernel/netsim.rkt` replays the sort publics through the network, 7 tests.

## Honest negatives, each with its number

- **l1's shelf packer is the wrong tool for a room that will exist 16 times.**
  The 10-block station compiles to 21x11 boxed = **231 cells** at its best
  width, over four chain partitions and widths 7..30 (a 12-block earlier draft:
  240-320).  16 of those do not pack under 60x60.  The room needs ~50 interior
  cells; l1 spends ~190 on shelves and rails.  For a room instanced N times,
  hand-lay it or write a generator (`serpentine` is the precedent) — the packer
  is priced per instance and l1 does not know that.
- **Two-pipes-each-way (drain BACKWARD along the chain, output at the near end)
  was designed and dropped.**  It removes the `(2n + K)` latency's K term —
  station i's value travels i hops instead of K-i — worth ~35% of the ticks.
  It costs 4 attach cells per station under l2's `spread?` rule, two more pipe
  runs per gap, and a `q`-poll loop to decide which pipe to read.  On a design
  whose ceiling is 3x, that is not where the missing 15x is.
- **Split into two 8-chains + a merge room**: `avg sum (n + 12)` = 49.7
  station-steps vs 77.7, i.e. 1.56x on ticks for the SAME 16 stations and one
  extra room.  It is the right next move IF the area problem is ever solved; it
  does nothing about the area problem, which is the binding constraint.
- Sentinel-only drain (no DRAIN token, push k sentinels) does not work in
  either polarity: a keep-max array with a -INF fill ejects the value at the
  FAR end, so the first `k-n` outputs are fill and the reset state after the
  drain is +INF, not -INF.  2k+n pushes per round and a filter to match.  The
  explicit DRAIN token is cheaper and is what the probe uses.

## What would actually be worth building next on sort

The certificate names the escape: **a different DATA LAYOUT.**  The ring build's
own profile (NOTES, "Sort: insertion sort in the ring") says ~150 ticks per
input value go on RAILS BETWEEN CHAINS and only ~10 inside the loops.  That is a
5-10x sitting inside the CURRENT 784-area world, with no new rooms and no new
protocol — a hand-laid / serpentine-style controller instead of l1's shelf
packer, exactly the lever that took sudoku's arithmetic room from 146 ticks to
44.  It is the same finding as the first bullet under honest negatives, applied
to the room we already ship, and it does not pay 4.6x in area to get there.

---

# reverse: the ring was never the problem — the block transitions were (2026-07-27)

`problems/reverse-rr-sol.rkt`, `solutions/reverse-rr.man`, registry row
`reverse-rr` (same problem id as `reverse`).  **20x20 @ 1563.4 local, judge
20/20 @ 2396.45 = 958,580**, id `73b82a16-18f9-489a-8fbf-f20ff72f1a4c`.
Previous best was the hand-drawn `reverse-manual` at 2,147,111; this is 2.24x
and it is builder-reproducible.

**Fit the cost model before designing the rebuild.** Running the shipped
`reverse.man` over the eight public cases and regressing emit against
(sum n, sum n^2, rounds) gives

    emit  ~=  94.5 * (values)  +  5.0 * (sum n^2)  +  10 * (rounds)

which kills the obvious story.  The ring's O(n^2) rotation is the **5.0**
term: at the spec maximum n=16 it is 1280 ticks against 1512 for the linear
term, and across the whole suite it is a fifth of the total.  **94.5 ticks per
value is the room walk**, and ~75 of it is five rail transfers between chains
on the emit path.  Any design that keeps one controller room and one branchy
block per value pays that again, whatever it does to the ring.

**Two moves, both about the per-value block count, not the algorithm:**

- **The pass counter leaves the ring.**  The shipped build keeps `k`, the
  rotations still owed, in ring cell 0 (`ring = [k, v1..vm]`), which costs an
  `r ring` and an `s ring` every pass and sizes the ring at n+1.  `m` — the
  number of values still owed — fits in B for the whole round once the MARK
  protocol stops claiming it, and `0 +` reads B into A **without disturbing
  it**, which is the whole trick.  `passc` is then `1 W - b M`: BP = m-1
  rotations, B = m-1 for the next pass.
- **Direct C->O.**  `#:out-src 'C`, F degenerates to tcp's two-op bouncer, and
  an emission is `(r ring) (s out)`.  That deletes a **nine-cell backtick MARK
  literal walked once per emitted value** plus two ring slots per emission.

**THE TARGETING SPLIT CAN BE BY ROW, and here it has to be.**  Four pipes on
C, and the exhaustive sweep (widths 16..33 x four chain partitions x
strict/soft bands) returns **nothing** under a column veto: l1 packs the two
`r in` ops and the two `r ring` ops into interleaved columns at every width.
The same layouts separate cleanly by ROW — every `r in` above every `r ring`,
every `s ring` above the `s out` — and the sim ranks pipes by MANHATTAN
distance, so a row split discriminates exactly as well.  `in` and `ring-out`
attach on C's north wall, `ret` and `out` on its south, and the `ret` tank
melts around C's west side.  That long route is not a cost: the ring needs its
capacity cells somewhere.

Consequence: **`define-ring-server` cannot build this world.**  The template
hard-asserts the column split ("ring reads not west of input reads") so it can
park I over the input reads.  The builder here is 40 lines of `room-spec` /
`chan-spec` / `assemble` instead.  If a third row-split world turns up, the
template wants a `#:c-split '(col | row)` keyword rather than a fork.

**PIPELINE THE FILL LOOP BY ONE to make the two-sided blocks agree.**  The
natural body `(r in) (s ring) m` runs east-then-west while `emitb`'s
`(r ring) (s out)` runs west-then-east, and l1 cannot seat two tight bodies
that straddle the split in opposite directions — that partition is unlayable
at every width, veto or no veto.  Reading one value ahead turns the body into
`(s ring) (r in) m` (push what is in A, read the next), with `rhead` doing the
pre-read and the `d`-branch's straight arm `fillgo` pushing the last value.
Now both straddling blocks run the same way and the room lays out.  **A loop
body's op ORDER is a layout knob, not just a semantics one.**

**CAP was over-provisioned and it cost a max-dim.**  Both tanks get
`#:capacity` each, so `CAP 18` reserves 36 ring cells for a ring that never
holds more than 16 values.  18 -> 9 took the world 21x22 -> 21x21 and unlocked
the `cx -2` / `O (-1 . 2)` pair that took it to 20x20 (-18.1% together;
neither pays alone, and single-cell gravity parks immediately at 21x22).
tcp measured caps 6..20 as byte-identical — that is a property of tcp's
floorplan, **not a general one**, and reverse is the counterexample.

## honest negatives, with the numbers

- **A station-chain LIFO for reverse loses, and the arithmetic says so before
  any code.**  16 values x 21 bits = 336 bits = six 63-bit registers minimum,
  so six-plus station men.  Packing 3 values per register needs a `/` by 2^42
  and a `*` by 2^21, and **a station's B holds the stack, so both constants
  have to arrive by pipe** — 13-14 ops per value per station against `r W s`
  for one value per station.  Either way the storage costs ~7 rooms where the
  ring costs ~9 pipe cells, and area is SQUARED in the score: 7 tiny rooms is
  ~+200 cells (27 -> 33 max-dim is +49% score) to save the 5.0*n^2 term, which
  is +22% of ticks at n=16 and less everywhere else.  **The ring wins outright
  at n <= 16.**  The station architecture is a lever for problems whose state
  is traversed O(state) times per round (tcp, sudoku), not for one whose ring
  is walked n/2 times.
- **A word-packed ring (3 values per cell, base 2^21, bias 2^20 so digit 0 is
  a free end-of-round sentinel and `q = 0` terminates the unpack by itself)
  does pay on paper — ~2.3x on ticks — but it needs five new rooms** (a bias
  front end, a K generator, and the U1/U2/U3 unpack cycle: `%` and `}` are the
  only B-preserving extractors and they need different constants, so the
  quotient loop cannot be one room).  Estimated ~26x26 against the 20x20 that
  the two cheap moves already reach; **not built, and not obviously ahead of
  it.**  If it is revisited, the auto-terminating unpack cycle is the good part
  and it generalises: U1 (B = base) does `r (s U2) % (s out)`, U2 (B = shift)
  does `r } X{+ -> s U1}`, and a partial word stops itself.

# Memory, STATION SPLIT: the remedy WORKS and the architecture still LOSES (2026-07-27)

`problems/memory-station-split-sol.rkt` (new; `raco test` it — 396 tests).
`problems/memory-station-sol.rkt` (the unsplit RED file), `kernel/mcfgsim.rkt`
and `solutions/memory.man` are all UNTOUCHED. **Nothing was submitted**;
`solutions/memory.man` 33x33 @ 66,543,935 stands, and the id
`d0b34a23-67c1-4087-b88e-90a74404d50e` was not spent.

## The remedy in the unsplit file's header is correct and it assembles

Split the four-pipe station into `SA` (reads `g` + `u`, sends everything on one
pipe `o`) and `SB` (reads `o`, routes BY SIGN: cw -> `n` the chain, otherwise
`N` and back into the tank `u`).  The three encoding changes are exactly as
written — mark tank-bound values with `N` (B-preserving), tank sentinel 0 not
-1, READ payload 1 not -1 with `satgt` discriminating `- X` against B = WM.

**One thing the remedy did not name and every re-attempt will hit:** the
PREAMBLE TERMINATOR is chain-bound too, so it cannot stay -1 (SB would divert
it into the tank) and cannot be 0.  Make it **1** and let `sfill` discriminate
the same way `satgt` does (`(r g) -` against B = WM; `BIAS - WM > 0` = a
preamble value, `1 - WM < 0` = the terminator).  That moves the `B = WM` set-up
into a one-block `sprol` prologue.  No new mechanism.

Result: **7/7 public, 5 spec-max stress cases, 120 fuzz, 8 (shards x slots)
splits — green on the FIRST mcfgsim run**, and the world assembles at 80x70,
7/7 in the real sim.  The four-pipe wall is genuinely gone: SA compiles under
HARD `#:col-order '((r g u))` where the unsplit station was empty at every
width.

## And it still loses, by a factor the projection got wrong

| case (local ticks)   | split 80x70 | memory.man 33x33 |
|----------------------|-------------|------------------|
| public case 6        | 18,468      | 64,341           |
| 120 ops / 100 addr   | 16,714      | 71,412           |
| 120 ops / 40 addr    | 24,031      | 55,982           |
| 120 ops / 10 addr    | 41,682      | 53,899           |
| 300 ops / 100 addr   | 35,316      | 248,863          |
| 100 ops / 1 addr     | 67,302      | 89,174           |
| 100 writes+100 reads | 50,205      | 252,978          |

It wins the TICK column on every case and loses SCORE on all but the 300-op
one, because 80^2 / 33^2 = **5.88**.

**THE TICK MODEL IN THE PREVIOUS ENTRY IS WRONG BY 3x.**  Fitted over three
shard counts (4x26, 6x18, 14x9) the real cost is

    T = 21 + ~25 * V  ticks/op,   V = 2 + (SLOTS+1)/SHARDS

i.e. **~25 ticks per value per SA/SB pair**, not the ~8 that "a tight loop
iteration is a 2-row circuit" implies.  V's floor is 2 — the two relay values
EVERY station forwards for EVERY op — so T can never drop below ~70 whatever
the sharding, while area grows linearly in SHARDS.  Measured shard sweep on one
120-op/100-addr probe, `per-band 2`:

    4x26 md  80 emit 28904 -> 185.0M   10x12 md 106 emit 11456 -> 128.7M
    6x18 md  80 emit 16714 -> 107.0M   12x10 md 136 emit 10361 -> 191.6M
    8x15 md  88 emit 14653 -> 113.5M   14x9  md 156 emit  9979 -> 242.8M

The emit column FLATTENS at ~10k: that is the relay floor, and it is why more
shards stop paying.  **Even at a perfect 75%-occupancy packing the sweep
bottoms out at ~67M — a tie with the shipped ring, not a win.**  So this is not
a floorplan bug; the constant is the architecture.

## The reusable landmines

- **A COLUMN BAND IS NOT A TARGETING PROOF.**  l2 ranks by MANHATTAN distance
  from the op to the segment, so ROWS count as much as columns.  SA's `r g` at
  layout (10, 9) is 19 from a west-wall cell on row 2 and 16 from an east-wall
  cell on row 12 — it targets `u` even though every g op is strictly west of
  every u op, and `assemble` says `room SA0: no in-attachment satisfies
  targeting`.  The fix is to SOLVE the wall cells with l2's own exported
  `targeting-ok?` over the candidate walls and keep the pair with the best
  margin (`solve-pair` in the sol file).  Do this instead of assuming a band.
- **A ROOM'S IN- AND OUT-ATTACHMENTS CAN LAND ON THE SAME CELL.**  l2 solves
  them as separate groups and `spread?` only separates within a group, so
  nothing stops it; the symptom is `first: contract violation ... given '()`
  from l2's own error path, naming neither room nor channel (it is `coherent?`
  rejecting the only pick).  Measured: `u2` and `o2` both at (33 . 24).  Reserve
  one cell explicitly and exclude it from the other end's candidates.
- **`floorplan.rkt`'s `plan-attach-cells` CANNOT be used on this room set**, and
  its own header says why: "A room with TWO channels of one kind does NOT get
  this for free."  Every SA (two `r`) and every SB (two `s`) is that room.  The
  packer finds 55x55 for the 5-shard set — genuinely better than the 80x70 hand
  plan — and dies at `room SA0` the moment l2 sees its cells.  **Combining the
  guillotine packer with a `targeting-ok?` cell solver is the missing tool**,
  and it would be worth ~1.9x here and on every future station world.
- **SB has no `#:tight` body and that is forced, not chosen.**  `bchain` is the
  only tight-able block (cw arm), but a tight lane is walked backwards and its
  band sense inverts, so the tight compile only ever lays `n` WEST of `u` — the
  wrong way round for a router that must hand `u` back to an SA on its west.
  Menus: `(s n u)` strict+tight 11x7 (n west), `(s u n)` strict+tight EMPTY,
  `(s u n)` soft+tight 10x7 (n west anyway), `(s u n)` strict no-tight 12x6
  (u west) <- shipped.  The mirrored world does not exist either: **SA compiles
  under `(r g u)` only; `(r u g)` is EMPTY at every width.**
- Tank capacity for a two-pipe loop: `SLOTS+3` makes `u` strictly larger than
  the most tokens it can hold (SLOTS+2 during a write), so SB can never block on
  `(s u)` and the loop cannot wedge.  It is also the SHORTEST safe capacity, and
  short matters — a tank cell is a tick of latency.
- `chain-partitions` x `chain-order-variants` over SA (40 partitions): **the
  caller's own partition is already the best**, 23x15 boxed; the search only
  adds ASPECTS (20x18, 22x17, 31x12), not area.  Not worth re-running.
- Shape x gap sweep, 240 builds (sashape 0..4 x cshape 0..1 x each gap +0..2 x
  per-band 2/3): **md 80 is the floor** and only sashape 2 reaches it.  The
  world is WIDTH-bound at two 37-wide pairs and no gap is removable, because l2
  needs two free cells outward from every wall cell.

## What would have to be true for this to be worth re-attacking

Both of: (1) a tight SB, which needs the whole floorplan mirrored and therefore
needs SA to compile under `(r u g)` — today it does not; (2) the guillotine
packer taught to respect targeting.  ~2x and ~1.9x respectively, which is the
only route to the 10-15M the previous entry projected.  Short of that, the
sharded station chain is a correct machine that is 1.4x worse than the lazy
ring on memory, and the previous entry's "~10-15M" should be read as **~107M
measured, ~67M at a perfect packing**.

# Subset, the ROOM SPLIT: the protocol is green twice over, and the wall that stopped it is TARGETING, not layout (2026-07-27)

`problems/subset-split-sol.rkt` (new), `scratchpad/subset-split/` (validation
harness + five measurement scripts).  **No submission**: the world does not
assemble, so `b5e48adc-317d-480d-88a4-e2edc659453a` is still unspent.
`problems/subset-station-sol.rkt` is untouched.

## (1) The split works, and the search room collapses much further than expected

`subset-station-sol.rkt`'s combined station is 23 blocks / 13 chains and l1
refuses it.  Splitting it does not just get under the chain wall — it lets
four separate merges happen, because once S_i no longer emits it no longer
needs the BP pass counter, and once it does not need BP the emit tokens can be
replaced by ONE end-of-case word:

| room | blocks | chains | l1 |
|---|---|---|---|
| combined (the refusal) | 23 | 13 | refused |
| S_i search, off-chain split | 14 | 5 | 15x15 |
| S_i search, spliced split | 15 | 7 | 20x18 |
| E_i emit | 11..15 | 4..8 | 21x18 |

The merges, all of them *literal* block equality once the protocol is right:
`iskip == ilost` (A = c, one `+` restores r); `iwon == iwin` (B holds v_i in
both and B is dead after a win); `elost == ewon` (send A up and idle), which
makes `ego` an unconditional `goto`.  And the case barrier stopped needing a
MARK at all: the controller sends `v_0..v_19, SENTINEL(-1), t, END(-1)` and
goes STRAIGHT BACK for the next case with no wait, because each DN pipe has
exactly one writer and S_(i-1) forwards the END only from its own `head` —
i.e. only after its whole subtree is done — so FIFO delivers case k+1 to S_i
strictly after all of case k.  **An eager controller is safe on a DFS chain.**
That removed the controller's second input pipe, which is what had made C
untargetable (`no in-attachment satisfies targeting`).

## (2) THE SIGN OF THE RESIDENT IS THE REPORT — a one-cell idiom worth stealing

E_i needs two facts, "am I included" and "what is v_i", and the obvious two
words cost a branch and two send cells.  Instead let B be **+v_i when excluded
and -v_i when included** — `iwin` does `W N M` and nothing else ever writes B
(`hchk`'s swap is always undone by `ok`'s or `padf`'s) — and the whole report
is `W` followed by ONE send.  The collect pass then emits the report itself.
One send cell instead of two is not a micro-optimisation here: it is the
difference between 18 and 0 targetable layouts (see (3)).

## (3) THE FOUR-PIPE WALL IS THE SIM'S NEAREST-SEGMENT RULE, and it is a WALL-ASSIGNMENT refusal

The off-chain split gives S_i a fifth pipe (EM i to its emit room): 2 in, 3
out.  It lays fine.  It cannot be *attached*.  Exhaustively, over every l1
chaining x width that lays (93 layouts), with `targeting-ok?` as the oracle
and every perimeter cell allowed:

* 18 of 93 admit ANY separation of the three outgoing channels.
* every one of those 18 has the same feasible wall triples:
  `(dn bk em)` in `{ (n e e), (n e n), (n e ne) }` — the child must be NORTH
  and the parent EAST.
* the incoming pairs `(up kid)` NEVER put `kid` on a north wall.

So there is no orientation, in any of the four chain directions, in which the
outgoing pipe to the child and the incoming pipe from that same child both
attach on the child's side.  **The room is refused by targeting, not by l1 and
not by the packer.**  Two lessons that generalise: (a) `plan-attach-cells`
ranks by pipe length and only then hopes, which is exactly backwards for a
room with two channels of one kind — cells must be chosen by satisfying
`targeting-ok?` FIRST and minimising length inside the satisfying set (there
is such a solver in `subset-split-sol.rkt`, `solve-attach`); (b) the cheap
pre-flight for any multi-channel room is "enumerate wall assignments against
`targeting-ok?`", which is seconds and replaces a day of assemble failures.

Also measured and worth not re-running: with `GAP 2` between boxes, a wall
facing a neighbour has NO attachable cell at all — `clear?` wants two free
cells outward and the second one is the neighbour's wall.  Flush and 2-gap
packing attach only through CORNERS; a facing wall needs GAP 3.

## (4) THE ESCAPE IS THE MERGED STREAM, and it costs 1.42x

Splice E_i into the DOWN chain between S_i and S_(i+1) and merge the status
report into that stream — it is the first word after the END, and the END is
the first negative word after the search, so the demultiplex is free.  The up
chain still bypasses E_i, so a node costs THREE hops, not four.  Every room is
then 2-in / 2-out and every room type is orientable:

    S  20x18 @ w=20   up=e kid=w / dn=w bk=e
    E  21x18 @ w=19   up=e ed=e  / dn=w eo=w
    E0 18x13 @ w=18   C 13x12 @ w=14   TS 8x7 @ w=9   TE 13x10 @ w=16

Measured cost of the splice, worst public case (near-total-sum): 1,287,808
blocks against 907,990 for the off-chain protocol and 907,831 for the unsplit
one.  **The off-chain split itself is free (+0.01%); the splice is +42%.**

## (5) Where it stopped, and the next move

All seven public cases, 60 random in-box cases, a five-case run and all seven
public cases fed back to back through ONE world are green on
`kernel/mansim.rkt` for BOTH split protocols (`scratchpad/subset-split/
check.rkt`, which now loads the shipped sol file directly).  What is missing
is only a floorplan.  The orientable wall assignment makes the chain run RIGHT
TO LEFT, and 42 rooms in one right-to-left row is 1000+ columns; folding it
into bands breaks the orientation at every turn, because a turn room needs the
mirrored assignment.  The next move is small and specific: probe for a SECOND
orientable layout family for S and E — the vertical `(s n n s)` family already
exists for S at 25x13 @ w=26 — and give the turn rooms that one, so a
serpentine can alternate horizontal and vertical runs.  A per-room layout is
free here: every station is already compiled separately, because the pipe-op
CHANNEL NAMES are baked into the layout (sharing one compiled layout across
twenty stations silently gives them all S1's channel names, which presents as
`no in-attachment satisfies targeting` and is worth an hour if you do not know
it).

**Honest hole, unchanged:** n=20 dense-random-no-solution and the n=20
big-element trap exceed the tick cap under the bare prune set.

# Gradebook attempt 4: the STATION sketch is arithmetically dead, and the
# reason generalises (design only, NOTHING BUILT, 2026-07-27)

Owner: the gradebook-station agent.  **No files created in the repo, nothing
registered, nothing submitted.**  This section is the whole deliverable: it
kills one architecture with a proof, replaces it with a design that is
complete on paper, and states exactly what is left.  Read it before starting
attempt 5 — the design work below is the expensive part and it is done.

## THE KILLER, and it is a one-line theorem about the ISA

**A register-resident STATION has exactly ONE scratch register.**  Its record
lives in B (that is what "resident" means and B is the only place a value can
live across a round).  A is clobbered by every `r`.  BP is write-only for
practical purposes (`b` writes it; `d`/`a`/`x` only branch on it; getting it
back into A costs one loop iteration per unit).

Therefore the complete vocabulary of a station is

    r  ->  A = C            (one control word from the chain)
    ?  ->  A = C (op) B     where (op) is one of  + - * / % & | ~ { }
    s  ->  emit A

and, crucially, **only `/` and `M`/`W` write B**, so `+ - * % & | ~ { }` all
preserve residence and can be chained — but each additional operand has to
arrive by `r`, which destroys the previous result.  So:

> **A station can produce exactly ONE derived value per control word, and it
> must emit that value before it reads the next control word.**

Consequences, each of which independently sinks the brief's sketch:

1. **The membership test (`GET`/`SET` route by id) does not exist at a
   station.**  Testing `id_field(R) == T` needs the XOR *and* a mask, or a
   subtract *and* a range test — two operands against a B that is already
   full.  The only single-op tests available are `X` on `C (op) R`, i.e. a
   SIGN test.  (There is a real escape, see "the two-sided compare" below,
   but it costs two control words and two branches.)
2. **`TOP` cannot reduce in the chain.**  `max(acc, key_i)` needs `acc` and
   `key_i` simultaneously; B is the record.  The reduce has to happen in a
   room that holds no record, so the stations can only GATHER.
3. **`SET` writeback needs the old field and the new value at once**, which
   is two control words with a branch between them — possible, but only in a
   station that has already proven it is the target, i.e. after (1).
4. Gathering forces an **O(N^2) relay**: station i must forward the header,
   emit its own value, then relay the i values from upstream.  With N=16 that
   is 240 relay ops and 16+ values through the last pipe per operation.

The sketch's own arithmetic was also wrong in the cheap direction: one record
is `id (14b) + 4 grades (7b) = 42 bits`, so **one record per station-register
is not a constraint at all** — the constraint is registers, not width.  Two
records per station (84 bits) genuinely does not fit, and no "2-slot
micro-tank" fixes (1)–(3), because a micro-tank is a pipe and a pipe cannot
return to its own source room (ARCH.md milestone 1) — it needs a second room,
at which point you have paid 32 rooms for 16 records.

**Room-count verdict for the station family:** 16 record stations + 16 index
stations (or a feedback pipe) + D + C + I + O = 20–36 rooms of ~8–18 blocks
each.  Estimated 55x65 world.  Area is squared in the score; `sudoku-station`
is 11 rooms at 31x33.  **The station family is the wrong shape for gradebook**
and the reason is register pressure, not layout.

## THE REPLACEMENT: one packed value per student on a sentinel-terminated ring

The actual fix for the 95-block room is **not more rooms first — it is a
smaller ring**.  The dead attempt spent 5 ring cells per student (80 cells)
and needed the rotation trick and the four K-variants *inside the op path*,
which is where the 95 blocks came from.  Pack the student into ONE value and
all of that disappears.

### The packing (verified by hand; ranges below are exact)

    idc = 16383 - id                 id in 1000..9999  =>  idc in 6384..15383
    R   = g1*2^51 + g2*2^40 + g3*2^29 + g4*2^18 + idc

  * **11-bit grade fields, not 7.**  A grade is 0..100 (7 bits) but the SUM of
    16 grades is <= 1600, and 1600 < 2048.  Eleven bits is what makes
    `acc += R` a legal one-op reduction with no carry between fields.
  * **18-bit id field at the BOTTOM, not 14.**  `sum(idc) <= 16*16383 =
    262128 < 2^18 = 262144` — it fits with 16 to spare, which is why the field
    is 18 wide and the value only 14.  This is the load-bearing number; at 17
    bits the id sum carries into g4 and AVG is silently wrong on big rosters.
  * Max single `R` = `100*2^51 + ... + 15383` ~= 2.3e17.  Max `sum(R)` over 16
    ~= `1600*2^51` ~= 3.6e18 < 2^63 ~= 9.22e18.  **No overflow, no sign.**
  * `P_s = 2^(18+11*(4-s))` = {2^51, 2^40, 2^29, 2^18} for s=1..4.
    `GM_s = 2047*P_s` (grade-s mask).  `MK_s = GM_s + 16383` (TOP key mask).

### Why this packing makes every operation a ONE-OP-PER-RECORD lap

  * **AVG(s)** — `acc += R & GM_s` gives `acc = (sum g_s)*P_s` with no carry.
    Answer = `floor(floor(acc / P_s) / N)`.  Nested floor division composes
    (`floor(floor(x/a)/b) = floor(x/(ab))`), so either form is exact; grades
    are non-negative so there is no sign case anywhere in AVG.
  * **TOP(s)** — key `= R & MK_s = g_s*P_s + idc`.  `P_s >= 2^18 > 16383`, so
    `g_s` strictly dominates and the tie is broken by LARGEST idc = SMALLEST
    id, which is the spec's rule.  Empty slots hold `R = 0`, and every real
    key is `>= idc >= 6384 > 0`, so **empty slots can never win TOP and
    contribute 0 to AVG** — that is how `N < 16` is handled with no counter.
    Epilogue: `id = 16383 - (best mod 16384)`, both constants are literals.
  * **GET(id,s)** — mask `16383` gives `w = idc`; the compare is `w - TC` with
    `TC = 16383 - id` in B and `X` on the result: **one op, zero constants.**
    Ids are distinct so exactly one record matches, which means B may be
    clobbered the moment it matches.
  * **SET(id,s,v)** — `R' = R + (v - g_s)*P_s`, i.e. one `+` and one `M`, once
    the delta is known.

### The two lap tricks that make it fit in registers

**(1) A NEGATIVE-or-ZERO sentinel is a three-way branch that costs no
register.**  Every record is `> 0` (idc > 0 always).  Put a `0` sentinel in
the ring and the lap terminates on `X` alone — **which frees BP entirely**,
because the loop no longer needs a counter.  A `< 0` value is then a third
tag, free: it is what marks the SET target for the rewrite lap (push `-R` at
the match, and the rewrite lap's `X` sorts sentinel / normal / target in one
op).  `sort` uses `B = SENT` and a subtract for the same job and pays a
register for it; the sign is cheaper and nothing in the tree had noticed.

**(2) The ring is scratch, and the discipline is exact.**  Ring canonical
state `[N, R0..R15, S=0]`.  Reads come off the head, pushes go to the tail, so
**anything pushed before a lap is read AFTER that lap's sentinel** — the ring
is a free stack for per-op constants that must survive a lap.  The trace that
proves canonicity is preserved (this is the part that is easy to get wrong):

    start                 [N, recs, S]
    read N, b (BP=N)      [recs, S]              BP is free: sentinel lap
    push c1,c2            [recs, S, c1, c2]
    push N                [recs, S, c1, c2, N]
    LAP over recs         [S, c1, c2, N, recs']
    read S, push S        [c1, c2, N, recs', S]
    read c1, read c2      [N, recs', S]           <- CANONICAL, constants used

Push order = final order, so the resident `N` must be pushed BEFORE the lap
and the scratch consumed after it.  Getting this backwards is the whole
"lap accounting is the correctness argument" warning from attempt 3, made
concrete.

### The two-sided compare (kept because it is the station escape hatch)

If a future design does need an equality test against a full B, this works and
costs two control words, two `-` and two `X`, with **B preserved throughout**
(`-` does not write B).  With the id field at the TOP of `R` (`R = idc*2^k +
low`, `0 <= low < 2^k`):

    C1 = T*2^k + (2^k - 1)   ->  C1 - R >= 0   iff  T >= idc
    C2 = T*2^k               ->  C2 - R <= 0   iff  T <= idc
    both                     ->  T == idc

This is the only single-B equality test found.  It is why the station design
is *possible* at all; it is not why it is *good*.

## HONEST NEGATIVES (do not re-derive these)

- **Broadcast `S` from a dispatcher to 16 stations**: rejected on
  `sudoku-station`'s measured evidence — the broadcast world was 40x66 vs the
  chain's 31x33, because every station needs its own corridor column, and c4
  (attach cells >= 2 apart) means a 16-way merge room needs 32+ perimeter
  cells.  Chain wins outright; area is squared, latency is not.
- **`#:forwarder 'corner` (the MARK protocol) is unusable with any packing
  wider than 20 bits.**  MARK = 2^20 = 1048576 and `ff-blocks` treats
  "above MARK" as HALT, silently.  The 62-bit record above is 40 orders past
  it.  Gradebook therefore has to be `#:out-src 'C` (tcp's topology, C owns
  the output pipe and carries four pipes) or `#:forwarder 'none`.  This is
  forced, not a preference, and it is why attempt 3's decimal packing was
  capped at 1,009,000.
- **F as a per-op transformer (NOTES' "the cheapest extra room is F") does not
  remove the second lap.**  F can hold the mask in B and echo `[R, R&mask]`,
  which deletes the transform lap from C — but the mask C sends now queues
  BEHIND the records C pushed last lap, so it only takes effect on the
  following lap.  Sending it early costs exactly the lap it saves.  The only
  way out is F echoing the mask too (`[mask, R, w]`), and then C has to
  re-push the mask each iteration from a register it does not have.
- **Two records per station register**: 2 x 42 = 84 bits.  Does not fit, and
  dropping the id to a slot index (2 x 28 = 56 bits, fits) just moves the id
  table into 4 more rooms.
- **`q` as an emptiness test to avoid a lap counter**: not pursued — `q` is
  the one op `kernel/isa.rkt` excludes from the differential test
  ("approximate"), so a lap that depends on it is unverifiable at design time.

## WHAT IS LEFT, AND THE HONEST BLOCKER

The op-side CFG for the design above is roughly: dispatch 6, `P_s` build 3 per
arm x 4 arms = 12, AVG 6, TOP 6, GET 8, SET 12 (three laps: extract, mark,
rewrite), op tail 4 — **call it 50-55 blocks, still over the ~45-block
ceiling**, plus a boot of ~14 (the four K-variants, which normalise `gw` by
multiplying by `128^(4-K)` so field positions are K-independent).

So attempt 5's move is the room split that attempt 3 already named, but now
against a machine that is *half the size* and has no rotation:

  * **boot -> F.**  It is a pass over the ring, it runs once, and F already
    sees every cell of every lap.  ~14 blocks off C.
  * **the four `P_s` builds -> a second room, or replace them with a 4-arm
    literal ladder** (`2^51/2^40/2^29/2^18` are 16/13/9/6 digits, all inside
    the 18-digit paired-span lint limit).  The ladder is one block per arm
    instead of three.
  * That lands C at ~35 blocks, under the ceiling, with `#:out-src 'C`.

**Blocker for this session:** the design above was derived from scratch (the
brief's sketch does not survive contact with the register model) and there was
no budget left to write, cfgsim, lay out and verify a 35-block controller plus
a forwarder.  Nothing was half-written into the repo on purpose.

**Residual risk to check first in attempt 5, before any layout work:** run the
packing through `kernel/check-encoding-range` for the sum bound
(`16*16383 < 2^18` is the tight one) and `kernel/check-sentinel-collision` for
the `0` sentinel against `R > 0` — those two checks are the entire correctness
argument for the encoding, and both are one call each.

## ADDENDUM — the ROOM SPLIT of the validated 95-block CFG, as an executable
## recipe (correctness sprint, score ignored; derived 2026-07-27, NOT built)

The pivot is right and the split is cheaper than it looks, because of one
observation that makes the whole thing verifiable up front:

> **If no register is live across a seam, the multi-room machine is
> behaviourally IDENTICAL to the single-room CFG with a `goto` at the seam.**
> So `kernel/cfgsim.rkt` on the EXISTING 95-block `gb-blocks` is already the
> correctness proof for the split machine — the only new risk is plumbing, and
> the seams below are chosen so that (a) holds.

### Why it is 3 rooms, not 2 (this is forced, do not re-derive)

`in` can be read by exactly ONE room (one input room, one pipe out).  Boot
reads the roster from `in`; the op dispatch reads the opcode and args from
`in`; `oround` reads the next round's `O` from `in`.  So **all `(r in)` ops
must live in the same room**, which pins boot-pass-1 + dispatch + odec
together.  Block counts, exact (I recounted them against the file; the header's
"44" is optimistic):

    boot 31   = boot,bd1,bd2 (3) + bk1-4 + bh1-4 + bb1-4 + xb1-4 (16)
                + bfin,p2h,p2b,p2z,p2d,p3h,p3b,p3z,p3d,nh,nb,nd (12)
    ops  64   = optop,od1,od2,odead (4) + GET 8 + SET 11
                + flush,fk,fz,fd,gpad,gtl (6) + AVG 14 + TOP 18
                + odec,onext,oround (3)
    total 95

No 2-way split satisfies the `in` constraint under ~45 blocks/room once relay
and baton blocks are added.  **Three rooms, and the seam that pays is that
boot passes 2 and 3 touch ONLY the ring** (`bfin`..`nb`, 11 of those 12 blocks
contain no `(r in)`) — so they can leave the `in` room even though pass 1
cannot.  `nd` is the exception (`(r in)` reads the first `O`); keep `nd` in C1.

    C1  (owns `in`)  boot pass1 19 + optop/od1/od2/odead 4 + 4 arg-forward
                     + nd 1 + odec/onext/oround 3 + relay/baton 5   ~= 36
    C2               bfin..nb 11 + GET 8 + SET 11 + flush..gtl 6
                     + relay/baton 5                                ~= 41
    C3               AVG 14 + TOP 18 + relay/baton 5                ~= 37

All three under the measured ceiling, and C1's boot half is the sub-CFG the
bisection already laid at 27x28.

### The ring is ONE loop through everything; output still rides MARK

    C1 -> C2 -> C3 -> F -> C1        F = the stock `ff-blocks/corner` forwarder

Keep the MARK forwarder exactly as-is.  **Any room can emit** by pushing the
MARK doublet (`M MARK (s ring) W (s ring)`) — which is what `grd`, `tfad` and
`tftd` already do, unchanged.  That removes the entire "who owns `out`"
problem: no room needs an output pipe, no `#:out-src 'C`, no `#:col-order`
fight.  This is the single biggest reason to keep the ring design rather than
the packed-station rewrite.

### The baton rides the ring, and the sign structure makes it free

Ring cells are `>= 1`; `S` and `S2` are `-1`; MARK doublets never reach a room
(F eats them).  So **any value `<= -2` is unambiguously a baton**, and the
idle relay tells them apart in three ops:

    rly   (r ring)              X ->  pos: rlyk | neg: rlyn      [0 arm dead]
    rlyk  (s ring)                  goto rly
    rlyn  M 1 +                 X ->  0: rlys (it was S) | neg: rlyb
    rlys  W (s ring)                goto rly           [B=v, so W restores A=v]
    rlyb  ... decode ...

Baton payload, one value, decoded with ONE `/`:

    baton = -(1000*(target+1) + N)        N <= 16 < 1000
    decode:  W N `1000` W /   ->  A = target+1, B = N     (`/` puts rem in B)
    mine?    X-ladder on A - myindex ;  if mine: W b   ->  BP = N

That `W b` is what carries the **`BP = N` invariant across the seam**, which is
the one piece of live state the original CFG assumes between ops ("BP = N IS AN
INVARIANT ACROSS OPS" in the file header).  C3 needs it for `ah`/`th`; C2's
`gget`/`gset` clobber BP anyway and do not care.

C1 holds `BP = N` permanently (its blocks — dispatch, arg forwarding, relay,
odec — never touch BP), and counts it out to build the baton with the two
blocks boot already contains in `nh`/`nb`, then restores with `b`.

### Ordering, which is the one thing that looks wrong and is not

A room's un-forwarded ring cells sit UPSTREAM of it.  So when C1 pushes
`[baton, args...]` downstream before relaying the lap, those values reach C2
**ahead of** the 88 canonical cells — exactly the order C2's code wants.  The
arg reads therefore port with a pure textual substitution:

    in gget/gset/gavg/gtop:   (r in)  ->  (r ring)

and C1 grows one small arm per opcode that reads that op's args from `in` and
`(s ring)`s them: GET 2 args, SET 3, AVG 1, TOP 1.  Nothing else in the 95
blocks changes.  Ring canonicity is untouched because the baton and args are
CONSUMED by the target room, never relayed.

### Cost, and why it is acceptable under a correctness sprint

Two idle rooms relay every cell of every lap at ~2 ops (~10 ticks) each, so a
lap costs ~88*2*10 ~= 1.8k ticks of pure relay on top of the active room's
work.  At <= 80 ops that is ~150k ticks — the same order as memory's shipped
310k worst case, so it is inside the cap with room to spare.  Area will be
awful (four cfg rooms plus two tanks, md ~80-100).  Both are irrelevant:
fractional case points plus eligibility make a slow correct machine worth far
more than a fast absent one.

### Order of work for attempt 5 (do NOT reorder these)

1. **FIX THE CFG.  IT IS WRONG — MEASURED, 2026-07-27.**  See the section
   below; step 1 of this recipe was run and came back 1/7.  Do not split, lay
   out or submit anything until `run-cfg` is 7/7.
2. Only then split the block list three ways, add the five relay/baton blocks
   per room, and re-run each room's sub-CFG through `compile-cfg` alone at a
   few widths to confirm all three lay.  This is the cheap gate.
3. Hand-stack the world with `assemble` (`l2.rkt`) — six rooms, one ring
   cycle, one `in`, one `out` off F.  No `floorplan.rkt` guillotine, no
   gravity, no shape menus; a fixed two-column stack is fine.
4. `verify`, then SUBMIT on any public pass to
   `d1415447-bf8d-49ef-924e-e024b06a504d`, then improve.

### Residual risks, named

- **Tank capacity.** Boot pass 1 bursts ~82 raw values before reading any
  back, and the ring now spans four rooms, so size every tank at `CAP >= 90`
  (the existing file's `CAP 56` is for the two-room world and WILL deadlock).
- **Two men on one ring cycle can deadlock** if a room blocks on `s ring`
  while the downstream tank is full and the upstream room is blocked on `r`.
  The relay loops are 1-in-1-out and never hold a value, so the only room that
  can bloat the ring is the active one — which is why boot's burst is the case
  to size for, and why `q`/`R` must not be used anywhere.
- The `0` arm of every `X` on a ring cell stays dead as before; keep the stub
  blocks (`fz`, `p2z`, `p3z`, `tfaz`, `tftz`) rather than "cleaning them up".

### THE HEADLINE: `gb-blocks` IS NOT CORRECT.  1/7, measured on cfgsim.

`scratchpad/gbsplit-simcheck.rkt` runs the shipped 95-block `gb-blocks`
through `kernel/cfgsim.rkt` (`run-cfg ... 'boot`, stock `mark-relay`, fuel 4M).
This had **never been done** — and it is not what the file's header claims was
validated.  Read that claim carefully:

> "validated against the spec in Racket (scratchpad/gbproto.rkt: 7/7 public
>  cases, 400 tie-heavy fuzz, 300 cross-checks against gb-spec, 0 failures)"

`gbproto.rkt` was a **packed-key interpreter written in Racket** — it validated
the ENCODING (`c = g*10000 + k`, the max/floor arithmetic, the tie rule).  It
did not execute this CFG.  NOTES says the same thing precisely ("Validated in
`scratchpad/gbproto.rkt` against the spec using the machine's own floored `/`")
and it is the packing that is validated there, not the control flow.  The
scratch file is gone, so the distinction was invisible and got compressed, in
the brief and in this file's own header, into "the CFG is validated".  **It is
not.  It has never been run.**

    case                       result   status    blocks
    tiny roster walkthrough    FAIL     blocked   2,075,420
    TOP demotion               FAIL     blocked   2,915,394
    tie-break                  FAIL     fuel      4,000,000
    floor rounding             FAIL     blocked   1,869,411
    mixed batch                FAIL     blocked   2,075,593
    K=1 minimal                PASS     blocked   2,886,077
    N=16 K=4 max               FAIL     fuel      4,000,000

Diffs, verbatim, which localise the bug better than any reading of the code:

    tiny:   got (51 23 2303)          want (51 23 77)
    TOP:    got (6935 6935 6935 3928 3928 6935)  want (3928 45 6935 6935 3928)
    floor:  got (5587279 55)          want (22 22 40)
    mixed:  got (7 1358219 8263 12 8263 52)      want (7 29 8263 12 6439 52)
    N=16:   got (93 65 45 99 3400 51 3400 5231 3400 3400 968801 51)
            want (93 65 45 99 47 21 5538 9975 51 55 88)

**The signature is unambiguous: `K = 1` is the only case that passes, and
`5587279` / `1358219` / `968801` are RAW PACKED CELLS reaching the output.**
`5587279 = 558*10000 + 7279`, i.e. an accumulated sum that never had `SK`
subtracted or never got divided — an AVG epilogue that ran on the wrong cell.
Two independent symptoms point at the same place:

  * **Everything K>=2 is wrong and K=1 is right** ⇒ the fault is in the part
    of the machine that only does work when a record is wider than one grade:
    the four-way K unrolling in boot (`bk*`/`bh*`/`bb*`/`xb*`) and/or the
    rotate-by-`s` variants (`av1..av4`, `tv1..tv4`) that exist to make the
    5-cell stride uniform.  Both are the SAME idea — "pad to 5 so every skip
    is a constant" — and it is the idea that is unvalidated.
  * **Two cases run out of 4M block-steps** (`tie-break`, `N=16 K=4`) rather
    than producing wrong output ⇒ a lap is consuming the wrong number of ring
    cells, so the ring de-synchronises and a later scan never finds its
    sentinel.  That is the lap-accounting invariant the file's own header
    calls "the whole correctness argument", stated but never checked.

So the failure is not a typo — the padding/rotation scheme has a real hole,
and it is exactly the scheme whose cost ("18 blocks, and on this CFG that is
what does not fit") drove the whole layout crisis.  **Attempt 5 should
seriously consider deleting the rotation** rather than debugging it: with the
sentinel-sign trick (see the previous section) BP is free for a rotate
counter, and a counted rotate is 2 blocks instead of the 12 that `av1..av4` +
`tv1..tv4` + their two dispatch ladders cost — which also buys back most of
the room budget that forced the split in the first place.

**Cost of not having run this:** three sessions of layout work, a bisection
study, and a fourth session's split plan were all spent on a machine that does
not compute the right answer.  `kernel/cfgsim.rkt` existed for two of those
sessions and its own header says "reach for it the moment a CFG is longer than
about a dozen blocks".  Ninety-five blocks went unrun.  **Run cfgsim before
`compile-cfg`, every time — a CFG that cannot lay out is a nuisance, a CFG
that lays out and is wrong is a submission spent.**

Repro (kept, 15 lines, no dependencies beyond the two modules):
`scratchpad/gbsplit-simcheck.rkt`.

## RESOLVED, SAME NIGHT: the bug was ONE MISSING `(s ring)`.  7/7. (2026-07-27)

`problems/gradebook-sol.rkt`, block `p3d`, now fixed in place.  Boot pass 3
(`p3h`) consumes `S` to discover the end of the records, and `A` is still `S`
when `p3d` runs — but `p3d` never pushed it back.  So the canonical tail was
SEVEN cells, not the eight the file's own header documents, and the first
negative cell a GET/SET flush meets was `S2`, three cells late.  Every lap
after the first desynchronised.

    (block 'p3d `((r ring) #\b ...))      ->   (block 'p3d `((s ring) (r ring) #\b ...))

Before: 1/7 public, block-steps 1.8M-4M (two cases hit the 4M fuel cap).
After:  **7/7 public**, block-steps **384-2591**.  The million-step counts were
pure spin on a desynchronised ring, not work — so **do not size tick caps off
the pre-fix numbers**.  Independent battery (gbvalidate agent, tiers 1-2):
**12/12 against `gb-spec`**, K=1..4 x N={4,16} mixed ops plus single-op
isolation at N=16 K=4; worst 6,535 block-steps.  The K-shaped signature is gone.

**The diagnosis in the section above was right about WHERE and wrong about
WHAT.**  "K=1 passes, K>=2 fails" pointed at the pad-to-5 / rotate-by-s scheme,
and the fault was indeed in the code that maintains the 5-cell stride — but the
rotation is FINE and does not need deleting.  It was one absent push in boot.
The lesson stands and sharpens: the failure signature localised the bug to the
right dozen blocks, and reading those blocks against the ring layout the header
documents found it in minutes.  **Write the ring layout down, then check every
pass consumes and re-pushes exactly `L` cells** — that is the invariant the
header calls the whole correctness argument, and it was never audited.

### STILL OPEN: the room split, and a WARNING about my own probe

The fixed CFG is still 95 blocks and still does not lay.  The 3-room recipe
above is unchanged and now sits on a machine that actually computes.

**`scratchpad/gbsplit-probe3.rkt` IS BROKEN — DO NOT TRUST ITS VERDICTS.**  It
reports `NO FEASIBLE` for every partition including `BOOT`, which probe1 and
the original bisection both lay at 27x28/28x27.  A control that fails a known-
good case invalidates the whole run.  The bug is in how it rebuilds chains
around the halt stubs it inserts (l1 wants every branch's straight arm to be
its chain's fall-through; filtering a chain list breaks that, and my repair
inserts stubs that change the partition l1 sees).  Fix the harness against the
BOOT control FIRST, and only then believe a partition verdict.  probe1's naive
filter is valid only for near-self-contained subsets like BOOT.

Partition sizes, recounted and reliable (these are just name lists):
`BOOT` 31, `OPS` (dispatch+GET+SET+flush+odec) 32, `RED` (AVG+TOP) 32.
`in`-ownership is the binding constraint on where the seams may go — see the
recipe above; `srd`'s mid-lap `(r in)` is what stops SET leaving the `in` room,
and the fix for that is to have the `in` room push the roster RAW and let the
next room do the K-variant packing (drops boot's 19 `in`-bound blocks to 4).

### MEASURED LAYABILITY TABLE (harness fixed against a control; TRUST THIS ONE)

`scratchpad/gbsplit-probe4.rkt`.  Supersedes probe3 entirely — probe3 appended
a halt stub after EVERY chain including ones ending in `(halt)`, inflating BOOT
from 31 to 43 blocks and failing it; probe4 keeps the original fine chain
partition, redirects out-of-set arms to one shared `xhalt`, and cuts a chain
only where a block's STRAIGHT arm left the set (l1 wants the straight arm to be
the chain's fall-through; the LAST block of a chain may rail).  **BOOT is the
control: 27x26.  A partition harness without a known-good control is worthless
— probe3 cost a run and would have "proved" gradebook unlayable.**

    partition                                    blk  chains  result
    BOOT   (pass1+pass2+pass3)      [control]     32    12    27x26  w=28
    OPS    (dispatch+GET+SET+flush+odec)          33    16    NO FEASIBLE
    RED    (AVG+TOP)                              33    19    NO FEASIBLE
    ---- and the leaves, all of which DO lay ----
    BOOT1  (K-variant pass 1)                     20     9    24x19  w=24
    BOOT23 (passes 2,3 + finalize)                13     4    26x11  w=28
    GETf   (GET + flush/gpad/gtl)                 15     7    32x12  w=34
    SETf   (SET + flush/gpad/gtl)                 18     8    20x17  w=20
    AVG                                           15     8    37x12  w=40
    TOP                                           19    12    54x14  w=58
    DISP   (optop/od1/od2/odead/odec/onext/oround) 8     7    NO FEASIBLE

**CHAINS, NOT BLOCKS, ARE THE BINDING CONSTRAINT.**  `OPS` and `RED` are only
33 blocks — comfortably under the "~45-50 block" ceiling this repo has been
quoting — and neither lays, at 16 and 19 chains.  `BOOT` lays at 32 blocks and
12 chains.  Every leaf that lays is <= 12 chains; both failures are >= 16.  The
ceiling should be restated: **~12-14 chains per room**, and block count is a
proxy that happens to correlate.  This also explains attempt 3's negative
result ("merging chains to cut rails did not help": it went 42 -> 28 chains,
still >> 14).

`DISP` failing at 8 blocks is the same effect in miniature and is a HARNESS
artifact worth understanding: every dispatch block's straight arm leaves the
set, so the cut rule makes seven 1-block chains — all rails, no fall-throughs.
In a real room DISP merges into whatever owns `optop`.  Read it as "a room of
all-rail chains cannot be wired", which is the same lesson.

### Consequence: the split is FIVE-ish rooms, not three

BOOT1 / BOOT23 / GETf+SETf / AVG / TOP, plus the forwarder and I/O.  The
3-room recipe above is therefore optimistic — its C1 (~49 blocks, and far more
than 14 chains) would not have laid.  The baton protocol, the marker encoding,
the `in`-ownership analysis and the ordering argument in that recipe are all
unaffected and still correct; only the room COUNT changes, and each extra room
costs one more relay loop (1 block if it never receives a baton, ~7 if it does)
plus one more hop of ring latency.  Note `flush/gpad/gtl` is shared by GET and
SET, so either they share a room (GETf+SETf = one room, retest it) or the
6-block flush group is duplicated.

Nothing was submitted.  The machine is CORRECT (7/7 public, 265/265 fuzz) and
UNBUILT; what stands between it and a score is a five-room hand-stacked world,
which is now a mechanical job with every measurement it needs already taken.

## Gradebook, the SEQUEL: the CFG bug was ONE OP, and the layable partition
## is now MEASURED (2026-07-27, attempt 4 continued)

### The 1/7 was a single missing `(s ring)` in `p3d`

`p3h` consumes `S` to discover the end of the records, and `A` is still `S`
when control reaches `p3d` — which never pushed it back.  The canonical tail
was therefore SEVEN cells, not eight, so the first negative cell a GET/SET
flush met was `S2`, three cells late; the ring desynchronised and GET started
returning record cells (the `2303` in case 1 is a student id).  One op:

    (block 'p3d `((s ring) (r ring) #\b ...     ; leading (s ring) was MISSING

    before: 1/7, block-steps 1.8M-4M (two cases hit the 4M fuel cap)
    after:  7/7, block-steps 384-2591

The three-orders-of-magnitude drop in block-steps is the tell: the machine was
not "slightly wrong", it was spinning through desynchronised laps.  **A
correct lap costs hundreds of block-steps; if a ring server is burning
millions, suspect lap accounting before arithmetic.**  Independently
stress-checked afterwards: 0/12 failures across all four K values at N=16 and
N=4 plus the single-op-type batteries, K-signature gone, worst 6,535 steps.

### The layable partition, measured — and a WARNING about how to measure it

`scratchpad/gbsplit-probe3.rkt`.  Each sub-CFG compiled ALONE, widths 18..68:

    BOOT  (pass1+pass2+pass3)             31 blocks  ->  26x27 at w=30
    OPS   (dispatch+GET+SET+flush+odec)   32 blocks  ->  61x17 at w=68
    AVG   (rotate+sum+epilogue)           14 blocks  ->  37x11 at w=40
    TOP   (rotate+max+epilogue)           18 blocks  ->  47x15 at w=50
    GETSET (no dispatch/odec)             25 blocks  ->  34x16 at w=34
    RED   (AVG+TOP together)              32 blocks  ->  NO FEASIBLE

**So the split is FOUR cfg rooms, not three: AVG and TOP will not share a
room** even though they are only 32 blocks together — 32 blocks of BOOT lay
fine, so this is rail congestion across many chains, not block count.  That
matches the original bisection's finding that block count alone was never the
binding constraint.

**LANDMINE — two of my three probe harnesses gave FALSE "NO FEASIBLE"
verdicts, and the failure is silent.**  Sub-CFG probes must obey l1's chain
rules or `compile-cfg` refuses for reasons that look exactly like layout
failure:

  * Naively FILTERING `gb-chains` to the subset leaves a block whose straight
    arm now points out of the set with no fall-through — illegal.  (This is
    what made 21-block `OPS-minus-SET` look infeasible.)
  * Rebuilding chains greedily by following straight arms gives LONG chains,
    and chain length is lane length is width — everything looked infeasible.
  * Cutting a chain wherever the straight arm is not the next block is ALSO
    wrong: **a chain's LAST block may `goto` anywhere — that is a legal rail.**
    Only cut when the straight arm leaves the SET.  Getting this wrong made
    BOOT — known-layable at 27x28 — report NO FEASIBLE.

**Always put a known-layable set through the probe as a CONTROL.**  BOOT at
26x27 is the control that caught all three bugs; without it I would have
reported "no partition lays" and been wrong three times over.

### What attempt 5 builds (all the design work is done)

Four cfg rooms + the stock `ff-blocks/corner` forwarder + I + O, one ring
cycle `OPS -> BOOT -> AVG -> TOP -> F -> OPS`, hand-stacked with `assemble`.
The baton protocol, the marker encoding, the seam analysis (BP = N is the only
live cross-seam register) and the ordering argument are in the previous
section.  Two things that section did not know and this one does:

  * `in` is owned by OPS, and **GET and SET must stay in the OPS room** —
    `srd` reads `v` from `(r in)` in the MIDDLE of a lap, and args pushed onto
    the ring arrive only at the HEAD of a lap.  That is why the `in` room is
    OPS and not BOOT.
  * BOOT's pass 1 can be reduced to ~4 blocks in the `in` room (read `N`,`K`,
    compute `M = N*(K+1)` in two ops as `A=K,B=N -> * -> +`, then a counted
    `(r in)(s ring)` relay loop) with the K-variant packing done in the BOOT
    room off the ring.  That is what buys the room for the relay/baton blocks.

**NOT BUILT, NOT SUBMITTED.**  The four-room world plus baton plumbing did not
fit the remaining clock; every input to it is above.

# Pathfinder: the WAVE is VM-GREEN (phase 2 done; descent NOT built, 2026-07-27)

Follow-up to "Pathfinder: the BFS fits in FOUR REGISTERS" and its build
checkpoint.  `problems/pathfinder-wave.rkt` is the wave, written as GENERATED
l1-IR blocks and executed by `pathfinder-machine.rkt`'s VM.  On all 7 publics
it reproduces `pathfinder-proto.rkt`'s `wave` EXACTLY — the distance k, the
visited set V, and the bit1(dist) plane P.  5,357 ops for a k=9 round, 29,197
for k=49.  **tape <= 31, ALU <= 11**: those are the pipe capacities a layout
must provide (phase 1 measured 5 and 3; the wave is what sizes them).

## What the schedule turned out to be

The predecessor's residual risk — "the north carry is a genuine lookahead,
handled by a one-word lag" — is real, and the lag lands in a THIRD pass:

    lap per word j: [V_j O_j hotr_j P_j], tail [pos m]
    PASS 1 pushes [cN_j O_j hotr_j V_j P_j Z_j],  Z_j = smear(V_j) | cS_{j-1}
    PASS 2 reads  [Z_{j-1} | cN_j O_j hotr_j V_j P_j]  and finishes word j-1
    PASS 3 reads  [O_i V'_i hotr_i V'_i V_i P_i], updates P and the reached test

Pass 1 folds the SOUTH carry in (a FIFO delivers it: it is one word LATE).
Pass 2 gets the north carry for free because pass 1 pushes Z_j LAST and cN_j
FIRST, so `Z_{j-1}` and the `cN_j` it needs land ADJACENT in the stream — the
lag costs no park at all.  Pass 3's plane update is UNCONDITIONAL:
`P' = P | ((V'^V) & mask)` with `mask = -bit1(m)`, which is what keeps ONE loop
body instead of one per phase of the mod-4 cycle.

Two mechanisms worth stealing for any tape+ALU machine:

* **A park of queue-sourced values never touches B.**  Send the amount `0`
  FIRST, then read-and-send each value: `0 s | r s | r s`.  The M/W park pattern
  (needed when the value is already in A) costs a register; this one does not.
* **The tape and the ALU are INDEPENDENT FIFOs**, so only the order WITHIN each
  matters.  That is what makes the group orders solvable at all.

## The bug that cost the only debug cycle, and it generalises

The ALU is ONE shared FIFO across all passes.  Priming pass 3's park in the
init block put four values in front of every request pass 1 then issued, so
pass 1's accumulator read `cN_j` where it wanted `cS_{j-1}` and the whole lap
came out shifted by one word — V and P both wrong, k wrong, and on some cases
the reached test never fired at all (op cap).  **Prime a pass's park in the
epilogue of the pass BEFORE it, never earlier.**  `p2-epi` now derives the mask
from `m` on the tape and primes pass 3 there.

## What is left, honestly

Phase 3 (descent + paint) and the round loop are NOT written, so there is no
world and nothing submitted.  The descent design is settled and unbuilt: per
move, `T_j = P_j ^ (V_j & mask)` with `mask = bit1(d-1) - 1`, then ONE lap
computing `S = OR_j align(T_j)` where align shifts word j by `pos-16-64j` in
BOTH directions (two ALU requests per word; the wrong-direction result is
identically 0, which is the whole trick), leaving up/left/self/right/down at
bits 0/15/16/17/32 of S — then four `X`s on the SIGN of `S << (63-bit)` in
preference order, and the 5-value paint `ADDR pos, DATA 0, ADDR q, DATA 10,
SWAP`.  Cost ~280 ops/move, ~84k ops/case: nowhere near the 15M cap.  The
problem remains AREA-bound, and note the new room ceiling (~12-14 CHAINS per
room, not ~45 blocks) — this controller is well past it and must be split
across rooms.

### The plumbing does not fit the rooms it plumbs (measured, attempt 4 close)

The four-room partition lays BARE (previous table) but not once the baton
plumbing is added.  `scratchpad/gbsplit-rooms.rkt` builds the real rooms —
partitioned blocks + an idle relay + marker traps + the return baton:

    room  bare        with plumbing            verdict
    BOOT  31 -> 26x27   36 blk -> 32x31 w=32   LAYS
    OPS   32 -> 61x17   49 blk -> NO FEASIBLE
    AVG   14 -> 37x11   26 blk -> NO FEASIBLE
    TOP   18 -> 47x15   30 blk -> NO FEASIBLE

**AVG is the damning one: 14 blocks lay at 37x11, and adding TWELVE blocks of
plumbing makes it infeasible at every width 20..74.**  So the cost of a room
in a baton world is not its share of the algorithm — it is the algorithm plus
a fixed ~12-block tax, and that tax is what has to shrink.  The tax is:

    idle relay          6   rly / rlyk / rlyn / rlys / rlym0 / rlyr
    return baton        4   marker push + BP count-out loop + push
    marker entry        1   (r ring) b -> goto <phase entry>
    odead stub          1

Two reductions are available and neither was tried (no clock left):

  * **Merge `rlys` and `rlyr`** — both are `W (s ring)` back to `rly`.  `rlyr`
    is only ever a RAIL target, and a rail may point at another chain's block,
    so they can be one block.  -1.
  * **Delete the return baton entirely (-4, and -3 more in OPS).**  It exists
    only to carry `BP = N` back to OPS, but `tfad`/`tftd` ALREADY read `N` off
    the ring (`#\M (r ring) #\b (s ring)`), and so does `gtl`.  If OPS re-reads
    `N` from the ring tail at the top of `odec` instead of being handed it, the
    return baton is a bare marker push and OPS loses `avarm`/`coh`/`cob`/`cot`
    too.  The reason it was not done this way is the "BP = N IS AN INVARIANT
    ACROSS OPS" note in the sol header — which is a property of the ONE-ROOM
    machine and does not have to survive the split.

That plausibly puts AVG at ~20 and OPS at ~42, both inside the range that
lays.  **Attempt 5 should kill the BP=N-across-ops invariant first, before
writing any world** — it is the single assumption that makes the split
expensive, and nothing outside the original single room depends on it.

Also fixed on the way through, both real l1 rules worth knowing: an `x`
zero-arm and a `d` straight-arm must be the block's CHAIN FALL-THROUGH, so a
generated relay/dispatch block must be chained WITH its trap target
(`(rlym0 m5)`, `(od2 avarm)`, `(obt obh obd)`); a generated block whose
straight arm is a phase entry needs a one-cell `goto` stub to land on.


# PLOTTER, REPACKED: 145,939,781 -> 26,034,300 on floorplan alone (2026-07-27)

`problems/plotter-sol.rkt`.  id `27e46a5e-3069-434e-901a-7d42697f7b4d`,
20/20, **56x60, avgTicks 7231.75, score 26,034,300** against the column
world's 56x145 / 145,939,781.  **5.6x, and not one CFG, register assignment
or protocol byte changed.**  The column world is kept verbatim as
`solutions/plotter-column145.man` / `build-plotter-column-grid`.

Local ticks went UP (4548.83 -> 4646.67) while the score fell 5.6x.  On a
footprint-tick problem the area term is quadratic and the tick term is not:
**never trade area for latency here.**

## The three things that made it assemble, all of them display-specific

**(1) A DISPLAY NEEDS THREE FREE WALLS, so pack it OVERSIZED.**  ADDR enters
the TOP wall, DATA the LEFT, SWAP the BOTTOM (sim.rkt's rule, and l2 now
re-checks it against a pinned cell).  A gap-0 guillotine packs the display
flush and there is then no clearance on any of them.  The fix is to enter it
as an `fp-fixed` pseudo-room PADDED with a halo — 2 rows north, 3 columns
west, 2 rows south — and to resolve the halo back to free space only when
choosing the display's own attach cells.  `plan-occupied` (halo occupied)
for every other room; a hand-rolled occupancy (halo free) for these three.

**(2) THE DRIVER MUST SIT OFF THE DISPLAY'S NORTH-WEST CORNER, and the reason
is the CURSOR, not the geometry.**  ADDR sets the cursor, DATA paints there
and ADVANCES it, so for pixel k
    arrive(ADDR_k) <= arrive(DATA_k) < arrive(ADDR_k+1)
i.e. with the driver sending ADDR then DATA d ticks later, once per loop of
period P:  **LA <= LD + d**  and  **LD + d - LA < P**.  Both are about the
DIFFERENCE of the two pipe lengths, and only a driver diagonally off the
NW corner keeps both pipes short and ADDR the shorter one.  A free guillotine
put Z west of the display but eleven rows too low: LA 19, LD 5, every pixel
painted at the previous address, and the world still assembles and still
looks plausible.  So Z, M and the display are packed as ONE COMPOUND
pseudo-room — Z left-aligned at the top-left, M in the pocket beside it, the
display below.  **The pocket is not slack**: M is 17 wide, Z 18, and
HALO-W + DISP-W is 37, so both rooms fit in the width the display already
costs.  Packing M into it is what pays for the compound.
This world lands at ADDR 2 / DATA 4 / SWAP 39 and asserts all four bounds at
build time (`check-display-timing!`).  The column world's 10 / 19 / 66 is
where the SWAP ceiling of `LSW - LA <= 56` for `Z-DELAY 24` comes from — it
is measured, not derived.

**(3) WHICH SIDE OF THE DRIVER EACH PIPE LEAVES FROM IS A HARD CONSTRAINT.**
Verbatim, and it cost the longest debugging pass here:
    `assemble: cannot route channel zsw ((32 . 6) -> (60 . 6))`
The SWAP was being asked to go straight down THROUGH the display.  DATA and
SWAP both descend the west halo, so both must leave the driver WEST of the
display's west edge; ADDR drops straight into the top wall and must leave
EAST of it.  Filtering the candidate cells by column is a three-line change
and it is the difference between zero plans assembling and the first one
assembling.  It also happens to be exactly what `z-col-order` already says.

## Landmines that are NOT display-specific

- **GAP 0 DOES NOT ROUTE ON THIS ROOM SET.**  Notches beat gaps only when the
  widths are RAGGED; plotter's rooms are all 15-27 wide, so flush neighbours
  leave no pocket and the symptom is `cannot route channel xy
  ((9 . 20) -> (9 . 47))` — two flush rooms of similar width whose only clear
  cells are on opposite outsides.  `#:gaps '(2 3)` assembles; `'(0 2 3)` and
  `'(0 2)` did not, at 300 plans x 1 attach variant and 23 usable plans x 6
  variants respectively.  And 60 really is this room set's floor: a widened
  `'(2 3)` sweep over 80 plans found nothing below max-dim 60 (the runners-up
  are 55x61 and 58x61, i.e. narrower and TALLER, which is worse under
  max-dim^2).
- **`plan-attach-cells` IS SOUND ONLY ON A PURE CHAIN.**  Q reads two pipes,
  M writes two, Z writes three; for those the group has to be solved together
  under `targeting-ok?`, which is what l2 does internally and what the packer
  cannot do for you.  Symptom: `room Q: no in-attachment satisfies targeting`.
- **RANK THE PAIR, NOT THE END — again.**  Ranking each end by distance to the
  partner room's ORIGIN gave `cannot route channel rm ((31 . 48) -> (26 . 28))`,
  25 cells apart between two adjacent rooms.  Rank against the partner's own
  CANDIDATE CELLS.  And weight the op-distance term at 1, not 4: on a room
  with one channel of a kind targeting is free, and a heavy op term drags the
  cell to the wrong wall.
- **A COMPOUND HIDES ITS ENTRY POINT FROM THE PACKER.**  The chain enters this
  compound at M, which sits at its top-RIGHT, but the guillotine only sees the
  bounding box and will place R flush against the bottom-left with the display
  in between.  `plan-usable?` rejects those before the expensive assemble.

## Honest negatives

- **Free (non-compound) guillotine reaches 51x47 and never assembles.**  The
  display-legal plans start at max-dim 53 and every one of them puts Z where
  the cursor rule fails.  The compound costs ~4 of max-dim and is what makes
  the problem solvable at all.
- **Gravity is not wired.**  `plotter-movables` is now `'()`: the floorplan is
  a tree and the packing is flush by construction, so there is no single-cell
  slack to take.  A sweep is a fresh idea, not a rebake.
- **Snake was NOT repacked.**  It is hand-assembled with no l2 path at all and
  its tank is a pipe LOOP whose length is its capacity, not an l2 capacity
  region; the tank-as-pseudo-room extension is real work, not a repack.  Snake
  still stands at 57x51 / 48,590,897.


# Targeting-first attach solver (REINTEGRATION item 7), built + measured (2026-07-27 ~04:00)

`scratchpad/targetsolve/solver.rkt` — `solve-cells`: the generalized
`solve-attach` (subset-split) over any plan+links.  Joint per-ROOM combo
search across BOTH kinds (a tight pack can leave a room 4 clear cells;
per-kind greed starves the second kind — measured on room G of the sudoku
front), targeting-ok? FIRST, length minimized inside the satisfying set,
cross-kind cell dedup (the u2/o2 same-cell landmine), `#:avoid` for a
route-repair loop (ban the refused channel's cells, re-solve).

## Measured, so nobody re-spends this

- SUDOKU: NOT the tool's problem class.  All rooms 1-in-1-out, so targeting
  is free and the binding constraint on every md<=32 front plan is the
  ROUTER: 40 tight plans x (8 repair retries + 36 variant restarts of
  plan-attach-cells incl. random skip vectors) = 0 rescues.  31x33 lat 94
  obj 102366 (shipped, 4,966,874) stands as the frontier optimum reachable
  by attach-cell choice alone.  rescue/rescue2/rescue3 in targetsolve/.
- Partner-CENTRE cell ranking loses to plan-attach-cells' PAIR ranking on
  chains: it parks ends 13 cols apart on the shipped tree (d12) and the
  router refuses.  For 1-in-1-out rooms use plan-attach-cells; solve-cells
  is for rooms with two channels of one kind (memory-split SA/SB, subset S).

### THE UNLOCK ATTEMPT 5 SHOULD START FROM: markers go POSITIVE, not negative

The relay tax above is 6 blocks almost entirely because a NEGATIVE marker has
to be told apart from the sentinel `S = -1`, which costs a two-stage sign
discrimination (`rlyn` computes `v+1`, `rlys` restores, `rlym0` compares).
That whole structure is unnecessary.

**There is a free numeric window above every legal ring cell and below MARK:**

    max legal ring cell = c = g*10000 + k  = 1,009,000
    MARK                                   = 1,048,576
    unused, and never produced by the machine:  1,009,001 .. 1,048,575

Put the markers there.  `F` still passes them through untouched (they are
below MARK, so `MARK - v` stays positive and the `fdead` halt arm is never
taken), and the idle relay collapses to THREE blocks with no sign reasoning:

    rly   (r ring) #\M `1009001` #\W #\-     x -> mine | rlyk | rlyk
    rlyk  #\+ (s ring)                       goto rly      ; `+` restores v
    mine  ...phase entry...

`-` leaves `B` holding the constant, so `rlyk`'s `#\+` reconstructs the
original cell in one op — the relay never needs to remember anything.  A room
with ONE marker pays 2 blocks instead of 6; OPS, which traps two (boot-done
and op-done), pays 4.  Combined with deleting the return baton (previous
section) that is roughly:

    AVG  22 -> ~19      TOP  26 -> ~23      OPS  49 -> ~47      BOOT 35 -> ~32

AVG and TOP then sit close to their bare sizes (14 -> 37x11, 18 -> 47x15), and
those are the two rooms that must come down.  **OPS at ~47 is still the room
at risk**, and if it refuses, the cut to make is GET out of OPS into its own
fifth room: `gget` reads `id` and `s` at the TOP of its lap, so it ports on
args pushed ahead of the lap (`(r in)` -> `(r ring)`) — unlike SET, whose
`srd` reads `v` MID-lap and which therefore has to stay with `in`.

Sequence for attempt 5, shortest path to a submission:
  1. positive markers + delete the return baton  (both above, ~30 lines)
  2. re-run `scratchpad/gbsplit-rooms.rkt` — it is the gate and it is written
  3. if OPS refuses, split GET out as a fifth room
  4. only then write the `assemble` world; the CFG itself needs NO further work
     (7/7 public, 265/265 fuzz, worst 6,638 block-steps)

# Subset, the ROOM SPLIT part 2: the layout is IMPOSSIBLE, and three exhaustive sweeps say why (2026-07-27)

Follow-up to "Subset, the ROOM SPLIT" above.  **No submission;
`b5e48adc-317d-480d-88a4-e2edc659453a` is still unspent.**  The protocol is
unchanged and still green (7/7 public + 60 fuzz + back-to-back, `kernel/
mansim.rkt`, `scratchpad/subset-split/check.rkt`).  What follows is about the
FLOORPLAN only, and it is a negative result: with the split's two rooms as they
compile today, **no floorplan exists**, and the reason is topological rather
than spatial.  Do not re-attack this by making the world bigger.

## (1) What was fixed, and is worth keeping

`problems/subset-split-sol.rkt`'s floorplan and channel list were still the DEAD
off-chain EM topology (`split-links` wired `EM i` and `DN i` straight down the S
chain).  They are now the SPLICE topology the block code actually implements --
84 channels, `C -d0-> S_0 -x_i-> E_i -d_(i+1)-> S_(i+1) ... -d20-> TS`, the up
chain `S_(j+1) -u_j-> S_j` bypassing E, and the emit chain `E_i -e_(i+1)->
E_(i+1) ... -e20-> TE`.  Also fixed: both E entries said `'erd0`, which is not a
block (`'erdh` is).  `solve-attach` now takes a per-channel WALL and a per-channel
target OFFSET along that wall, which is what makes it terminate.

With that, **83 of the 84 channels route**, at good lengths: u_j 10 cells, x_i
28, d_i 15-17, on a 615x56 world.  Only the twenty emit links fail.  Two
floorplan facts that cost hours and are worth keeping:

* **Routing ORDER is part of the plan.**  u_j must be listed before x_i/d_i or
  it loses its gap and the whole thing fails at `u0`.
* **TS must be BOTTOM-aligned** with the S row.  Top-aligned it is 7 rows tall,
  u19 leaves its east wall high and hugs the top of the last gap -- exactly
  where x19 has to dive.

## (2) THE WALL, stated once: a PLANAR CROSSING, and it is intrinsic to the rooms

Every candidate floorplan reduces to a rectangular gap with two rooms facing
each other, openings top and bottom, and three or four pipes whose endpoints sit
on that boundary.  Read the endpoints in CYCLIC order and the chords either nest
or interleave; interleaved chords cannot both be drawn, at ANY gap width, in ANY
routing order, because pipes do not cross.  This is the single fact that kills
every arrangement, and it is worth internalising: **a gap is a planar region and
its pipe set is a chord diagram.**  Checking nesting takes a minute on paper and
replaces a day of `cannot route channel` failures.

The two rooms' feasible attachments (measured, `scratchpad/subset-split/
{fam,cells,ecells}.rkt`) are:

    S : reads  (u_i west, d_i east) = (0,2) | (14..17, 11..16)
        sends  (x_i west, u_(i-1) east) = (0..5, 13..17)
    E : the emit channel is ALWAYS BELOW the search channel on a shared wall

So x_i is pinned to the TOP of S's west wall and u_(i-1) to the BOTTOM of S's
east wall, always; and e is pinned below x and d, always.

* **E row BELOW the S row.**  The E rooms are then FINE -- x_i enters the E gap
  from the top, d_i leaves to the top, e_i is a low horizontal chord, and the
  chords nest.  The S gap is what fails: u_i's chord splits the gap into an
  upper and a lower half, x_i must get from S_i's west wall DOWN to the corridor
  and d_(i+1) must come UP from it, and exactly one of them always lands on the
  wrong side.  Fixing it needs u's read above x's send on the west wall AND u's
  send above d's read on the east wall.
* **E row ABOVE the S row.**  Now the S gap nests (this is the 615x56 build that
  routes 83/84).  The E gap fails instead: x_i has to reach E_i's east wall from
  BELOW at an offset ABOVE e_i, and e_i spans the whole gap.

## (3) THREE EXHAUSTIVE SWEEPS, all negative

* `scratchpad/subset-split/ssearch.rkt` -- every l1 chaining of the SEARCH room
  x widths 16..30, asking for u-read-above-x-send and u-send-above-d-read:
  **0 hits.**  Kills the E-below plan.
* `scratchpad/subset-split/esearch.rkt` -- every chaining of the EMIT room x
  widths 14..28, asking for x-below-e and d-below-e: **0 hits.**  Kills the
  E-above plan.
* `scratchpad/subset-split/wprobe.rkt` -- the same room with ALL FOUR channels
  on one wall (`pred=w succ=w`, which fam.rkt says lays), asking for e ABOVE x
  and d: **0 hits.**

A second searcher reached the E result independently and sharpened it: the 24
legal chainings x widths 12..34 are **perfectly anti-correlated** -- layouts that
admit x-below-e reads admit ZERO west-wall send pairs, and every layout with
feasible sends admits only x-above-e.  The crossing is a property of where l1
puts the pipe ops, not of the chaining.

## (4) The only escape, and why it was not taken

The chords can be un-interleaved by routing e the long way round a HOLE, and the
only holes are the rooms.  Worked through: e must leave the gap west of x's leg
and re-enter east of d's leg, but both legs terminate on the S row, so e has to
go around the END of the whole S row -- west along the corridor past TS, into a
bottom margin, east under all twenty stations, and back up past C.  ~1200 cells
x 20 pipes, all nested, all COLD (2-3 words per case, so ticks are noise) and
width-neutral, so the score would still be ~615^2 x avgTicks.  It is a correct
plan.  l2's router will not find it (it was given 34-row corridor and bottom
margins and still failed at `e1`), so it needs hand-laid pipes or a router that
will accept a homotopy hint -- half a day, not half an hour.

## (5) What to do next, in order

1. **Change the ROOM, not the floorplan.**  The cheapest fix is to give E's emit
   channel a wall of its own, e.g. by splitting E again (a tiny relay room that
   owns `e_i`/`e_(i+1)` and talks to E over one private pipe), which turns the
   interleaved 3-chord gap into two 2-chord gaps.  CLASSES' room split is the
   tool and it has now paid twice.
2. Failing that, hand-lay the twenty emit detours over the 615x56 build, which
   is otherwise complete.
3. Do NOT re-run the three sweeps and do NOT widen any gap.

**Honest hole, unchanged:** n=20 dense-random-no-solution and the n=20
big-element trap exceed the tick cap under the bare prune set, so even a laid
world would not have been 7/7 on the hidden set.

## L1 LAYOUT CEILING, MEASURED (llm agent, 04:04 2026-07-27)

A synthetic `cond` ladder (`scratchpad/llm/shape2.rkt`, N arms -> N+1 chains,
each arm `(goto tl)` to a shared tail) laid out or refused as follows, trying
widths 10 14 18 24 32 44 60:

```
arms=2   6 blocks   3 chains  LAYS  w=14 (12x8)
arms=4  10 blocks   5 chains  LAYS  w=18 (15x12)
arms=6  14 blocks   7 chains  LAYS  w=60 (46x6)     <- already straining
arms=8  18 blocks   9 chains  NO LAYOUT
arms=10 22 blocks  11 chains  NO LAYOUT
```

**The practical ceiling is ~7 chains per room, not ~12-14.**  Shape is not the
issue: `scratchpad/llm/shape.rkt` shows a single `case-sign` forwarding loop, two
mutually-`goto`ing loop heads, and a 4-chain ladder all lay fine.  It is a count.

Corollary for anything built on l3: **budget one room per ~6 chains.**  A
`cond` with k arms costs about k+1 chains, so a room may hold roughly one
5-way dispatch and nothing else.  The llm interpreter (24 chains in one room,
12+21 after a two-way split) is 3-4 rooms' worth of dispatch and has to be
decomposed that way, or re-expressed arithmetically to avoid branching at all.

### CORRECTION to the two sections above: the blocker is CHAIN SHATTERING

Measured independently (racer C, `scratchpad/gb-racerC/gate.rkt`) and it
overturns my diagnosis.  I wrote that a room pays a "~12-block plumbing tax"
and that AVG dies from block count.  **Wrong.**  AVG's 15-block reduction body
alone fails at every width 22..74 — with no plumbing at all.

The cause is the partitioning helper, not the rooms: `chains-for` FILTERS the
parent's `gb-chains` to the room's block set, and **a chain that loses a middle
member shatters into singletons.**  A 15-block room therefore reaches l1 as
~12 one-block chains and hits the chain-count wall.  Every "NO FEASIBLE" in the
two tables above is contaminated by this — including, probably, OPS at 49.

FIX: **re-chain each room from scratch** rather than inheriting a slice of the
parent's partition — `l1.rkt`'s `chain-partitions` (see `snake-sol.rkt`'s
`(list-ref (chain-partitions bs chs (hash) entry #:limit 25 #:max-edits 2) i)`
pattern) searches legal partitions for a block set.  Note it REQUIRES a legal
starting partition or it silently degenerates to one candidate.

This is the third time in this session that a probe harness produced a false
"NO FEASIBLE" (see the earlier LANDMINE on filtered chains, greedy chains, and
legal end-of-chain rails).  **A sub-CFG extracted from a parent CFG needs its
chains REBUILT, never inherited — and every probe needs a known-layable
control set.**  The positive-marker relay and the return-baton deletion in the
sections above are still worth doing (they are real block savings), but they
are optimisations, not the unlock.  The unlock is re-chaining.

# Small-world repack endgame: TEMPLATE SHAPE MENUS ARE THE BINDING CONSTRAINT (2026-07-27 ~04:00)

Files: scratchpad/repack-final/ (brk-pack3.rkt, rev-pack.rkt, verify-man.rkt);
solutions/brackets-packed.man (26x26, judge 842,270, was 922,381),
solutions/reverse-rr-packed.man (19x19, judge 806,113, was 958,580).

- **The guillotine packer on a template's own menus reproduces the shipped
  world and nothing better** — brackets' define-pipeline menu had 3 D shapes /
  2 C shapes, and all 5 feasible plans landed at/above 27x25.  The packer is
  only as good as its shape menu.
- **The fix is one loop: sweep `chain-partitions` x `chain-order-variants` x
  width, dedupe by (w,h) keeping lowest ticks, feed ALL of it to `fp-cfg`.**
  Brackets: 3 -> 32 D shapes, 6 C shapes -> 26x26 (order variants, not
  partitions, unlocked it).  reverse-rr: the shipped `#:accept?` row-veto menu
  contains ONE layout (17x9); the partition x order sweep finds 13 that pass
  the same veto, and a 16-wide C turns 20x20 into 19x19 @ judge x1.544.
- **Tank worlds stay out of the guillotine model but the SAME shape sweep
  applies** — reverse-rr was repacked by re-running its hand floorplan formula
  over the new C shapes plus its baked delta neighbourhood, no packer at all.
- Both winners are NOT builder-reproducible from their sol files (the bakes
  still build the old worlds); repro scripts are in scratchpad/repack-final/.
  Maintenance item: bake the winning chains lists into the sol files — note
  the sweep scripts dedupe by (w,h) and DROP the chains provenance, so baking
  means re-finding the chains for the winning (w,h) (cheap, the sweep is
  minutes).
- MEMORY-SPLIT, the item-7 demo itself, measured tonight (targetsolve/mpack.rkt,
  5 shards x 21 slots — the set the "55x55 packable" claim names): the packer's
  front DOES hold 30 plans at md 55-58, and the targeting solver + strict-margin
  check + route-repair loop got PAST the old SA0 targeting death — but no flush
  (gap 0/2) plan assembles: mid-chain SA rooms (3 ends, two `r`) are CORNER-
  STARVED at gap 0 (no targeting-safe cell set exists at all — solve-fail, not
  mis-targeting), and the rest die in ROUTING after 6 cell-ban retries
  (route-exhaust).  Two solver lessons baked into solver.rkt: (a) targeting-ok?
  ALONE is not enough for #:fixed cells — assemble re-checks against the
  committed cell and a TIE can resolve against you; require strictly positive
  margin (measured: SB refused at assemble after passing targeting-ok?);
  (b) 3-end rooms need the top cap (combos are a cross product; top 400 on
  3 ends = 64M combos).
- SCORE VERDICT unchanged from the architecture entry above: even a realized
  55x55 split is a LOCAL-metric tie with the 33x33 ring (~50-67M vs 66.5M) and
  the judge is round-gated — a 12-room pipeline's latency ratio would sink it.
  The tool's real future target was always a NEW station world, not memory.

# SUDOKU-STATION latency re-attack v4: three op moves, one unsound protocol,
# and a sweep exhaustion certificate (2026-07-27 ~04:15, reattack agent)

Files: scratchpad/sudoku-reattack-0727/{sweep.rkt,sweep2.rkt,sweep3.rkt},
solutions/sudoku-station-v4.man (banked copy of the scratchpad .man).
Judge line: 20/20 31x33 avgTicks 4089.3 SCORE 4,453,247.7 (ids e13e1a85-2268-
4d3a…/bbf7b1b7-b775-4ed2-b545-c39ce4bd1be0, byte-identical submissions), from
4,966,874 this morning: -10.3% in three sim-green steps (d2cut 4,922,716 ->
earlyv 4,699,362 -> v4 4,453,248), ALL floorplan-identical 31x33 on the SAME
baked guillotine tree — every point came from LATENCY, none from packing.
48.5-x-latency law re-confirmed: mean 1-round latency 95.4 -> 85.7 over the
line, 4089.3/85.7 = 47.7 (the fit uses v=1 latency; within noise).

## The op moves that paid (sweep3.rkt has the final ops, commented)
- 32*h by SHIFT, not doubling: `W M 5 W {` (5 ops) replaces the shipped
  `W M + M + M + M + M +` (11).  `{` is A<<B and digits SET A, so the "no
  backtick literal" reason for the doubling chain never applied to a shift
  whose COUNT is a digit.
- REKEY the bitboard: station k = v/2, half h = v%2 (station k holds v=2k
  low, v=2k+1 high; S0's low half is permanently 0 since v=0 does not exist).
  Deletes the whole v-1 computation; stations/N unchanged — dispatch still
  sees k in 0..4.  Constant-into-B first (`3 M (r d1) /`) saves 1 more.
- LATENCY SHAPING, worth more than op count: D1 sends r RAW (D2 shifts it in
  head slack), sends v EARLY (stash c in B across the v read: `M (r in) (s)
  W`), D2 sends k BEFORE t2 so k ripples S0->S4 while G still builds w.
  D1 32->30 ops but its serial prefix to the v send fell 31->18 slots; D2's
  post-v tail fell 21->12.  Local throughput barely moved (2144 -> 2137);
  the judge moved 9.5%.  Rank by the emit tick of (run-program g '(0 0 v)),
  mean over v=1..9 — max-dim^2 x that mean tracked every judge result.

## LANDMINE: single-w station protocol is UNSOUND (do not re-derive)
The tempting cut — G sends w ONCE, station does `~ W - (s n)` (B keeps
old^w, A = old-new), N splits on SIGN — passes ALL single-round probes and
ALL valid streams, and fails every conflict-bearing fuzz stream: old-new =
2c-w where c = old&w, and w has THREE bits, so a partial overlap on low bits
gives 2c-w < 0 = reads as clean.  `|` instead of `~` has the same hole
(old-new = c-w <= 0 always).  With A,B only and a write-only backpack there
is no 5-op way to get both the verdict and the state update out of one w;
the double-send IS the protocol.  Fuzz signature to recognize it by: even
(valid) cases all green, odd (random) cases all WRONG.

## Sweep exhaustion (do not re-run on a hunch)
guillotine-front #:pareto? #f, max-dim 33-34, gaps (0 1 2), keep 2, attach
variants (0)(1)(2), on the v4 room set: 31 trees x 3 variants -> only THREE
build+route at all (the baked tree at lat 85.7, two cousins at lat 100.7);
every other candidate dies in plan-attach-cells/assemble.  The shipped tree
is the packer's optimum for this room family for the third design in a row;
floorplan search on this problem is DONE, further points are op-level or a
new architecture.

# TCP endgame re-attack: 30x30 CONFIRMED OPTIMAL for this machine (2026-07-27 ~04:10)

Layout-only pass per brief; the lazy-realign redesign stayed closed.  Files:
scratchpad/tcp-reattack/{tcp-band-sol.rkt,tcp-nof-sol.rkt,tcp-band28x30.man}.
Verdict: the banked 30x30 / 6,062,760 stands.  Three findings, all measured:

1. **30x30 is structurally optimal for the shipped topology.**  World =
   C box (WxH) + north band (7 rows: F box 4 + corridors) + 4-col east I/O
   strip; minimizing max(Cw+6, Ch+7) over the shape menu (24x23 / 26x21 /
   29x20 / 30x18) lands exactly on the shipped 24x23 at 30x30.  Merging the
   strips (I/O into the band, cshape 1) closes 28-wide but the band floor is
   7 rows (F box 4 + I/O pipe bends + tank melt), so height stays 30:
   28x30, max-dim unchanged.  Every CY=5 variant (F flush at row 0, band
   delta 0, attach-tries 6, 54 combos) is attachment-infeasible.

2. **tcp's judge is THROUGHPUT-dominated — the latency rule does NOT
   transfer.**  The 28x30 world has 1-round latency 237 vs the shipped 258
   (-8.1%) and local avg 3955.7 vs 3968.5, and the judge returned avgTicks
   6752.6 vs 6736.4 (+0.24%), score 6,077,340 (id 1e3f2150-4659-43a2-a493-
   24ef2b20edf7, 20/20).  Rank tcp floorplans by local suite avg (ratio held
   x1.707 / x1.697); max-dim^2 x latency is a sudoku-station rule, and
   round-gating alone does not imply it — tcp overlaps rounds inside the
   window, so the gated chain rarely sits on the critical path.

3. **`#:forwarder 'none` (C->C single-tank ring) is BROKEN in l2, do not
   reach for it.**  Every build renders a tank whose glue flows into C's NW
   corner and dies at load: `parse-pipes: stray pipe glyph at (band . 0)`,
   invariant across band 0-3 x roc 0-9 x rec -2..3.  Root cause (read, not
   guessed): both ring ends land in ONE (C, ring) attach group — l2 keeps
   one assignment per (room, kind) group, so src and dst get one cell
   between them (landmine 1 of the floorplan section, sharpened: same-room
   same-channel is the degenerate case).  A C->C ring would delete the
   4-row F box and open 28x28 (-13% area) + a shorter lap; the fix is an l2
   attach-group split keyed by pipe END, not room — queued as a maintenance
   item, NOT attempted under the endgame layout-only rule.

Gravity re-run from the baked point (--rounds 6): zero movement.  Floorplan
search on tcp is DONE at this partition; further points are op-level (the
refused realign redesign) or the l2 fix above.

# Subset, the FLOORPLAN: the obstruction is PLANAR, and where each escape dies (2026-07-27)

Follow-up to "Subset, the ROOM SPLIT" above.  The protocol is unchanged and
still green; everything here is geometry.  `b5e48adc-...` is STILL UNSPENT.
Files: `problems/subset-split-sol.rkt` (floorplan + `solve-attach` rewritten),
`scratchpad/subset-split/{fam,ssearch,esearch,eeast,cells,ecells,ov}.rkt`.

## (1) The predecessor's next move does not exist

It asked for a second orientable family for S and E so a serpentine could turn.
Swept exhaustively (`fam.rkt`, every (pred-side x succ-side) x every l1 width):

    S : pred=e succ=w  (the known RTL)  |  pred=e succ=n  |  pred=s succ=w
    E : all four of {e,w} x {e,w}, and NOTHING on n or s

S's two extra families are both TURNS THAT GO UP.  There is no southward and no
LTR family, so the search chain can only ever step west or north: a staircase,
never a serpentine.  **E has no vertical family at all**, which kills every plan
that wanted E above or below its own S.

## (2) The real wall is a PLANAR CROSSING, not congestion

`targeting-ok?` pins the wall OFFSETS, and the pinned offsets make two pipes
interleave on the boundary of a gap.  Read the gap's boundary clockwise and list
each pipe's two endpoints; if the two chords interleave, no gap width, no margin,
no routing order and no amount of detour can help, because the region's other
exits lead back to the same outer face.  Three floorplans, three deaths:

* **Two rows, E above** — 83 of 84 channels route.  The emit chord e_i spans the
  E-row gap BELOW x_i's arrival, while x_i climbs from the S row below: x_i is
  cut off from the corridor.
* **Two rows, E below** — the mirror.  u_i runs bottom-left to top-right of the
  S-row gap while d_(i+1) needs the top-left.
* **One alternating row** (C S0 E0 S1 E1 ...) — u_i must hop over E_i and e_i
  over S_i, in opposite directions, from adjacent points: they must swap sides.

## (3) Every cheap escape, measured and refused

* **E chaining** (`esearch.rkt`, 3920 decompositions): 0 layouts put x_i BELOW
  e_i on the east wall with d below e on the west.  A second, independent sweep
  found the same and named the dichotomy: reads-right and sends-right are
  disjoint classes.
* **WHY the dichotomy is total (E-side closure, second sweep)**: a channel's
  wall target must sit near ALL of that channel's pipe-ops, and l1's FORCED
  fall-throughs couple the two orders — erdh(x3-read)->erdb(d4-send) pins a d4
  op 3 rows below an x3 op, and ewait(e3-read)->etok->enotin(e4-send) pins an
  e4 op 6 rows below the e3 op.  Flipping the read order (x below e) drags
  erdb's d4 op down with it, scattering the d4/e4 ops so sends die on ALL FOUR
  walls (class-R layouts: 0 send pairs anywhere, not just west).  Verified over
  the full LEGAL space — x/d-block fall-throughs are forced by
  `chain-partitions`, only goto links toggle, so E has exactly 24 chainings —
  x widths 12..34 x 5 chain orderings: 0 hits, definitive.  Escaping needs
  something outside l1 chaining (band-splitting a send channel's blocks, a
  floorplan-level mirror, or accepting the crossing).  Consolation if the
  floorplan can flex: c14 w=29 (box 27x13, forced + eend->esta + erel2->ewait)
  gives the send half perfectly (west d@0 / e@6..8, 24/24 pairs) with reads
  feasible on both walls but always x-above-e.  Files:
  `scratchpad/subset-split/eorient{3,4,5,6}.rkt` + `.out`.  DO NOT RE-SEARCH
  the E side under l1 chaining.
* **S chaining** (`ssearch.rkt`, all chainings x 8 widths): 0 hits for the
  E-below strip.
* **All four E channels on the east wall** (`eeast.rkt`, all 24 orderings):
  feasible orders exist, but the emit pair is ALWAYS below the search pair.
* **The relay room** (built, 20 forwarders, 124 channels, all attach): a SHELL
  GAME.  Splitting e_i at F_i deletes the left-to-right chord, but F_i east makes
  e^a cross x_i and F_i west makes e^b cross x_i.  Routed 65/84 and no further.

## (4) Two bugs worth keeping

* **The mandatory seg cell.**  Each attach cell forces the cell immediately
  outward.  Two channels on the SAME wall approached from the SAME side have
  their segs in the same column, and the far one must traverse the near one's
  seg -- presenting as "cannot route" on a channel whose corridor is visibly
  empty.  The fix is to make the near channel climb one column out and jog along
  its own attach row; ordering alone only swaps which of the two fails.
* **Cross-kind cell collision in `solve-attach`.**  Reads and sends are solved in
  separate passes, so a small room would put a read and a send on the SAME cell
  and l2 then died with a contract violation on an empty route rather than an
  honest message.  Fixed with a per-room committed-cell set at distance >= 2
  across both passes.  Worth copying into any other targeting-first solver.

## (5) What to do next

Separate the two chord families into different passages instead of fighting for
one gap -- split the E row by PARITY into two interleaved rows so e_i and
x_i/d_i never share a gap.  That was in flight at the deadline and had reached
84/84 on attach.  Routing order IS part of the plan and belongs in the links
list; emit-before-x-before-d was worth +2 channels here.
- FINAL state of the item-7 demo at contest close: gap-2/3 fronts (md 63-68)
  get every room past solve-cells, but `assemble` STILL refuses SA/SB rooms
  ("no in/out-attachment satisfies targeting") even when the picked cells win
  by strictly positive margin in BOTH frames (seg AND committed cell).  So
  assemble's #:fixed re-check disagrees with a plain nearest-segment model in
  some third way — next session: read l2.rkt's in/out-attachment verification
  path itself and diff it against solver.rkt's margin-ok?* on one refused SB
  instance (cells are deterministic, the repro is `mpack.rkt` at gaps '(2 3)).
  NOT submitted: no assembled world, and the architecture loses regardless.


# GRADEBOOK: four measured negatives from the layout side (2026-07-27)

Written from the packing/wiring seat during the endgame race, so that none of
these is re-run on a hunch.  `scratchpad/gb-a11/`, `scratchpad/gbsplit-*.rkt`.

**(1) THE SPLIT IS MANDATORY — single-room re-chaining is dead.**  The one path
that would have kept gradebook's fully-verified single-room protocol is cutting
the CHAIN COUNT, not the block count.  A maximum path cover over the
straight-arm graph takes `gb-chains` from **42 chains to 25, longest 11** —
and the room still lays at NO width in `range(24,132,4)`
(`scratchpad/gbsplit-merge.rkt`).  l1's ~12-14 chain ceiling is per ROOM and
25 is still over it.  Do not re-attempt single-room gradebook.

**(2) DELETING THE RETURN BATON DOES NOT MAKE AVG/TOP LAY.**  The obvious
suspect, and it is innocent.  With `retbaton` removed and both reduction rooms'
tails going straight to their relay, plus `chain-partitions` re-chaining at
limit 40 / max-edits 3 over widths 20..86:

    BOOT (control): 36 blk, 14 chains, 40 cands -> LAYS 32x31 w=32
    AVG (no baton): 22 blk, 12 chains, 20 cands -> NO FEASIBLE
    TOP (no baton): 26 blk, 16 chains, 40 cands -> NO FEASIBLE
    OPS           : 49 blk, 24 chains,  0 cands -> NO FEASIBLE

The cost is the RELAY machinery, not the baton: a bare 14-block AVG body lays
at 37x11, and 22 blocks with the relay does not.

**(3) A PROBE HARNESS NEEDS A KNOWN-LAYABLE CONTROL.**  This is the reusable
one.  Two independent gradebook probes produced blanket NO FEASIBLE verdicts
that were harness bugs, and the way both were caught was adding a room that is
SUPPOSED to pass — BOOT above.  A probe that fails everything is
indistinguishable from a hard problem.  Put the control in from the start.

**(4) SPLITTING THE RELAY INTO ITS OWN ROOM IS NOT DRAWABLE.**  Proposed as the
fix for (2); it is refused by geometry, not by the protocol.  A relay room that
can DIVERT is 1-in-2-out, its body is 1-in-1-out, and wherever that body
re-enters the ring THAT room has two incoming ring pipes read in ALTERNATION —
l2's `room X: no in-attachment satisfies targeting`, which is structural and no
gap width fixes (proved again on plotter this session).  The only 1-in-1-out
arrangement is `relay_i -> body_i -> relay_i+1` with the body passing
non-work values through — but a pipe carries VALUES, not B/BP, so the relay
cannot hand the body a register and must forward the marker for the body to
re-test.  That is exactly what a co-resident relay already does, so the relay
room is redundant.  **Shrink the relay (wider marker window), never move it.**

**The floorplan is not the bottleneck, and here is the number so nobody has to
ask.**  `scratchpad/gb-a11/floorplan-skeleton.rkt` packs I + the four rooms at
their measured dims (BOOT 26x27, OPS 61x17, AVG 37x11, TOP 47x15) with
`#:gaps '(2 3)`: **79x53, max-dim 79**, tree
`(h 2 (v 3 (leaf 0 0) (leaf 1 0)) (v 2 (h 2 (leaf 2 0) (leaf 3 0)) (leaf 4 0)))`,
filtered so BOOT lands adjacent to OPS — the ring is a CYCLE and the closing
BOOT->OPS leg is the one link a chain packer does not choose for, so it is
checked geometrically instead of hoped for.  Nothing fits under max-dim 78
(area floor 58 with two CAP-56 tanks).  Swap `fp-fixed` for `fp-cfg` with the
real shape menus and it re-derives in seconds.

Note for whoever picks OPS up: it returns **zero** partition candidates —
`chain-partitions` raises on it rather than returning a short list.  That is a
different failure from AVG/TOP and the exception itself is the lead.


================================================================================
LLM PIPE-FREE LANE — CLOSING RECORD (04:25 07-27, agent: llm-pipefree)
================================================================================

Nothing submitted from this lane; no .man exists.  What exists, where, and what
it proves — everything under scratchpad/llm-pipefree/ unless noted:

- cfg-frozen.rkt — GREEN snapshot of the UNBIASED lllm-cfg machine (loader with
  the Ldig fix + chain-legal twins).  machine.rkt drives it: 10/10 lllm publics
  END-TO-END from raw judge input in cfgsim, and vs problems/llm.rkt (the LLM
  reference) "first steps" PASSES; pileup/bounce house paint frame 0 correctly
  and diverge at frame 1 (multi-man stepper is the missing increment, design in
  llm-build.md §5).  So the pipe-free LLM subset = 1 known public + any 1-room
  1-man privates, from THIS exact block set, the moment it can be laid out.
- THE LAYOUT REFUSAL IS DIAGNOSED, NOT MYSTERIOUS.  compile-cfg #:verbose
  'trace prints the exceptions the width loop swallows into "no feasible
  layout" (l1.rkt:1498).  Two distinct modes, seen directly: (1) a goto-merged
  chain lays as ONE h=1 shelf — a 27-block chain wants width ~160+ ("shelf:
  boot (w=160 h=1) does not fit"); (2) many short chains fit their shelves but
  branch-arm RAIL WIRING fails ("shelf: wire arm (r . c) -> X failed").
  budgetchains.rkt (op-budget chain cutter) explores the middle; both modes
  coexist there too.  The author's closure count (31 branchers vs ~3-5 wired
  arms/room) says no chain partition fixes it — the fix is either folding h=1
  shelves or fewer branchers (table-driven everything), post-contest.
- ceilprobe.rkt — the refusal data: S/L/ALL, shelf+melt, widths 30-300, all
  REFUSED.  Width and melt are refuted as unlocks; measurements in the file's
  output (and this session's transcript).
- worldtest.rkt — THE l2 WORLD TEMPLATE, ASSEMBLED AND SIM-GREEN with dummy
  rooms (48x50, 3 frames committed, zero errors): I -> L -(feed)-> M <-> F
  ring cycle with the 280-cap tank as an EXPLICIT SERPENTINE REGION
  (chan-spec cap = (list 280 (list r0 c0 r1 c1)) — a bump-formed 280 tank eats
  the floor and blocks its own return leg; the reserved region is the fix),
  data on D's WEST wall + swap on SOUTH wall, NO ADDR pipe, NO output room,
  display-judged.  Targeting laws re-learned: one pipe max out of 'in
  (sim.rkt:709) so k's must relay through the loader room; self-loop tanks are
  legal (memory-station pattern) but the two ends need disjoint wall hints and
  #:near pins; in/out attach groups are solved separately per room.
- Next agent's fastest path to LLM points: make the rooms lay (fold or
  de-branch), drop them into worldtest.rkt's chan-spec skeleton, verify with
  scratchpad/llm/verify-man.rkt (streaming judge-exact compare, exits nonzero),
  submit the SAME .man to BOTH ids: llm 383158cc-1891-46b2-9a9f-d9ed2661c85d,
  lllm d91edb43-4e94-4541-b8f7-9c79ba8c8331.
