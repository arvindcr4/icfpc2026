# littleman — project overview

A compiler-and-optimization stack for ICFP Contest 2026's "littleman"
esolang: programs are ASCII grids where little men walk over instructions,
rooms connect via value-carrying pipes, and solutions are scored by
`max(width, height)² × avg ticks-to-final-output` across public test
cases. Lower is better; correctness on private tests gates eligibility.

The stack turned out to be one idea applied recursively: **a few rigid
blocks plus fluid flows, packed by search, with a judge-exact simulator
as the ground-truth oracle at every level.**

## Architecture (bottom up)

- **L0 — `sim.rkt`**: the simulator, calibrated to reproduce the real
  judge byte-for-byte on every probe and submission to date. Implements
  the authoritative tick order (pipes shift → output emits/input feeds →
  men execute → men move), emission-time scoring, the formal pipe
  grammar, static literal validation, 64-bit wraparound, and (post-merge)
  the `Y` split instruction with judge-confirmed strict-die collisions.
  Also the **LM-75 display**: `+`/`=`/`:` rooms parsed as pipe
  destinations, pipes classified by the side they attach to (top ADDR,
  left DATA, bottom SWAP; right/corner/duplicate = load error), ADDR →
  DATA → SWAP processed once per tick during stage 3, and a **frame log**
  of every SWAP. Display results ride parameter+box channels
  (`sim-frame-log`, `sim-displays`, `sim-error-reason`) because
  `sim-result` is positional and destructured everywhere.
  **Never change its semantics without a judge probe proving the change.**
- **L1 — `l1.rkt`**: compiles a CFG of basic blocks (ops + structured
  `goto` / 3-way `X` / backpack-`d` terminators) into a room interior.
  Chains become flows; hot loops (`#:tight`) become rigid 2-row circuits;
  transfers route via Dijkstra over (position, heading) with arrow-merging;
  `#:max-width` gives aspect budgets; empty-line compaction shrinks the
  result. Rooms come out with a static tick estimate and a pipe-op list
  for targeting.
- **L2 — `l2.rkt`**: assembles compiled rooms + 3×3 I/O rooms into a
  world. Routes every pipe per the grammar; **melted tanks** (capacity =
  bare number) grow boustrophedon snakes through actual free space;
  **attachment auto-solving** (`attach-at`) picks walls/cells so hook
  pipes emerge for flush rooms; **shape menus** expose each room's
  Pareto front (width × height × ticks) to the search;
  **`gravity-optimize`** hill-climbs placement + shape with
  multi-magnitude moves ({1,2,4,8}-cell jumps) and plateau tolerance.
- **L3 — `idioms.rkt` + per-problem files**: reusable process idioms —
  the MARK output protocol (outputs ride the ring behind a 2^20 marker;
  the forwarder diverts them, keeping every controller single-outgoing),
  the fast forwarder (register-invariant compare, ~10 ticks/value),
  counter-in-the-ring loop bookkeeping, sentinel-terminated tight scans.
- **L4 — `harness/`**: the problem harness, so a new problem is mostly
  "write the CFG and the constants". `templates.rkt` has the two world
  shapes every solution here has used — `define-ring-server` (controller
  + forwarder + two melted tanks + I/O; memory/reverse/sort/tcp) and
  `define-pipeline` (an ordered chain of one-in-one-out rooms; brackets)
  — deriving the menus, the band floorplan, the channels, the manifest
  and the gravity movables from a declaration. **Display-judged problems**
  (grading.md) are an ordinary registry row plus an entry in
  `display-problems`: `run-suite` then compares FRAME SEQUENCES by
  streaming match instead of output lists, scores by the tick of the final
  matching frame, and runs the sim with `display-judged?` on (exactly one
  display at the stated resolution; emitting output is an error).
  `fragments.rkt` is an
  optional CFG-fragment library (counted loops, sentinel scans, the MARK
  emit, counter-in-the-ring rotate) with the register contracts written
  down. `problems.rkt` is the registry and `driver.rkt` the single entry
  point for verify / stress / optimize / score / submit.

## File map

| file | role |
|---|---|
| `sim.rkt` | judge-exact simulator (L0). `sim-debug-pipes` for diagnosis |
| `sim-y.rkt` | Y-instruction development clone (merged into sim.rkt by the consolidation pass) |
| `l1.rkt` | CFG → room compiler (L1) |
| `l2.rkt` | world assembler, pipe router, tanks, shape menus, gravity (L2) |
| `idioms.rkt` | shared forwarder CFG + MARK protocol constants |
| `place.rkt` | exhaustive placement search for tiny straight-line programs (used for triangular's optimal 8×8) |
| `search8.rkt` | the original triangular-specific searcher (historical; superseded by place.rkt) |
| `synth.rkt` | Rosette synthesis of op sequences from test cases (small programs; idiom vocabulary, finite bitwidth) |
| `layout.rkt` `main.rkt` `process.rkt` | earlier-generation straight-line layout + driver (still used by synth/place path) |
| `harness/templates.rkt` | `define-ring-server` / `define-pipeline` (L4): world declaration → builder, menus, channels, manifest, movables |
| `harness/fragments.rkt` | optional CFG fragments with documented register contracts (counted loop, sentinel scan/drain, MARK emit, ring rotate) |
| `harness/problems.rkt` | the registry: name → tests, spec, builder, movables, stress generators, submission id, tick caps |
| `harness/driver.rkt` | `racket harness/driver.rkt <verify\|stress\|optimize\|score\|submit> <problem…>` |
| `problems/<name>.rkt` | per-problem spec + transcribed public tests + validator |
| `problems/<name>-sol.rkt` | per-problem CFG + world declaration + `build-<name>-grid` |
| `solutions/*.man` | submission files; a plain `build-…` call must reproduce them byte-identically (modulo a trailing newline some saved files carry — `driver verify` normalizes it) |
| `tests-display.rkt` | the LM-75 battery: every display rule, the load errors, the frame log, and the harness's streaming frame compare |
| `probes/` | judge-probe programs + docs (semantics questions only the real judge can answer). `probes/display-probes.md` + `d*.man` are the LM-75 kit — EDITOR probes (the observable is the screen widget), not submittable until a display problem exists |
| `NOTES.md` | **the institutional memory**: judge-calibrated facts, reusable idioms, landmines. Read before touching anything |
| `*.md` (textbook, reference, grading, split, …) | contest documentation snapshots |

## Judge model (see NOTES.md for the full list)

- Score ticks = tick of the final correct emission. Halting is never
  required; servers block forever on exhausted input for free. Errors
  are fatal only before the final emission.
- Rounds gate input on completed output; a server that never reads
  ahead is correct under continuous-feed simulation (local ticks
  slightly underestimate judge ticks on multi-round tests).
- Step cap 5M (default). Values are signed 64-bit, wrapping.
- Pipe grammar, literal statics, collision semantics: all in NOTES.md,
  each entry tagged by the probe or submission that confirmed it.
- **Display problems** are judged by a streaming compare of the frames
  the display commits (one per SWAP), scored by the tick of the final
  matching frame. Every LM-75 semantic we implement is spec-derived and
  UNCONFIRMED — no display problem has reached us — so read NOTES.md's
  "The LM-75 display" open-questions list before writing one.

## The playbook layer (start here for a new problem)

Three artifacts distil what every successful agent on this project has
actually done, so a new problem starts from a short brief instead of a
re-derivation:

| file | role |
|---|---|
| `PLAYBOOK.md` | the impl-agent **SOP**: the standard flow (transcribe+assert → measurement gate → implement → declare → verify → stress at spec max → optimize → bake → lint → submit → record), the operational survival rules (timeouts, 64k output cap, batching into few processes, tick caps), coexistence etiquette for a shared tree, and the report format that works |
| `CLASSES.md` | the problem-class **casebook**: seven classes (pure function, pipeline, ring server, heavy-state server, bounded search, fixed-output/footprint, display), each with the smell that identifies it, its template + exemplar files, which score term dominates, its judge multiplier, and its own landmine list — closing with a decision tree that extends the recipe below |
| `harness/estimate.rkt` | the **cost oracle**: `(estimate-problem …)` → ballpark local ticks, which term binds (controller vs forwarder), a judge-tick range from the calibrated multipliers, the activity-cap load, and a *comfortable / tight / redesign* verdict. `racket harness/estimate.rkt` prints its calibration against the shipped problems' actuals; `raco test` asserts the fit has not drifted |

Read `PLAYBOOK.md` once, `CLASSES.md`'s row for your class, then only the
NOTES sections that row points at.

## How to solve a new problem

The harness owns the plumbing, so the work is steps 1–3; everything
after that is a driver command.

1. **Transcribe** the problem page into `problems/<name>.rkt`: a spec
   function (fold the round structure), all public tests exactly, and a
   load-time assertion that the spec reproduces the published outputs.
   Rounds concatenate within a test case, and some rounds expect no
   output. That assertion is the transcription's only guarantee — keep
   it, because a typo in a test list is indistinguishable from a bug in
   the solution and you will chase the wrong one.
2. **Pick a template.** Does the state fit in registers (A, B, and a
   write-only backpack per room)?
   - **Yes → `define-pipeline`.** An ordered chain of one-in-one-out
     rooms, I at the front, O at the back. One pipe per direction makes
     `r`/`s` targeting trivially correct: no `#:col-order`, no
     `#:accept?` veto, no MARK, no tanks. Control flow in a second room
     is the cheap third register. Brackets is 27×25 this way, *smaller*
     than the ring family despite doing more arithmetic.
   - **No → `define-ring-server`.** The ring exists to hold STATE, not
     to move values. Controller + forwarder + two melted tanks + I/O.
     `#:out-src 'C` gives the direct-output variant (tcp) where C owns
     the output pipe instead of riding MARK through F.
   - Small pure function (≤ ~14 cells) and no state at all → skip the
     templates: synthesize ops with `synth.rkt` and let `place.rkt` find
     the optimal packing (this found triangular's leader-tying 832).
3. **Write the CFG** against the register model: A/B hands, write-only
   backpack (b/m/d/x/]), `~`/`-` + `X` as free 3-way compares, counters
   ride the ring when registers run out. Mark hot loops `#:tight`.
   Constants outside the value domain (MARK=2^20, sentinels) are your
   friends. Keep the server never-halting. `harness/fragments.rkt` has
   the recurring shapes with their register contracts written down —
   they are optional helpers, and the templates take raw blocks.
4. **Fill in the template's constants**: the CFG, the width sweeps, the
   ring capacity (sized by the SPEC maximum), the band formula, the F/O
   seeds, and — where the floorplan genuinely needs them — the
   `#:accept?` vetoes and `#:near` tank hints. These stay per-problem on
   purpose: they are where the shipped ring servers actually disagree,
   and each has a NOTES scar behind it.
5. **Register it** in `harness/problems.rkt`: tests, spec, builder,
   movables, stress generators, tick caps, and the submission id if you
   have one. Stress cases must be built at the spec maximum *and stay
   inside the spec box* — a generator that leaves it manufactures red
   that costs a real investigation.
6. **Run the driver** — one process per command, because the first build
   of a problem pays a ~70s shape-menu sweep and every later build in
   the same process is milliseconds:

   ```
   racket harness/driver.rkt verify   <problem…>   # tests + repro + literal lint
   racket harness/driver.rkt stress   <problem…>   # spec-maximum cases
   racket harness/driver.rkt optimize <problem> [--rounds N]
   racket harness/driver.rkt score    [problem…]   # local score table
   racket harness/driver.rkt submit   <problem>    # dry run; --confirm to POST
   ```

   `verify` passes when the public tests are correct (status `timeout`
   with correct outputs IS a pass — a correct server blocks forever),
   the plain build reproduces `solutions/<name>.man`, and the literal
   lint is clean. `optimize` measures the suite first and caps the
   search just above the worst observed emit; bake its deltas into the
   sol file's `BASE-DELTAS` and re-verify, so a plain build still
   reproduces the saved file.
7. **Record**: append genuinely new landmines and judge facts to
   NOTES.md. If a semantics question can't be answered locally, write a
   probe whose judge-visible *outputs differ* under each interpretation
   and hand it to the human to run.

## Working style that got us here

- The sim is the only truth. Every layout trick, every optimization,
  every semantics guess gets validated through it — and the sim itself
  gets validated against the judge via probes with discriminating
  outputs.
- Scores are `area² × ticks`: know which term binds before optimizing.
  Area wins compound (compaction, melting, shape menus, hooks); tick
  wins live in hot loops and forwarder throughput; the two couple
  through tank geometry.
- Search beats cleverness for geometry (hand analysis missed the 8×8
  triangular twice), but *structure* beats search: the biggest wins came
  from architectural moves — lazy storage, the MARK protocol,
  counter-in-the-ring — that no optimizer would find.
- Preserve best-known solutions: overwrite `solutions/*.man` only when
  strictly better, and keep builds reproducible.
