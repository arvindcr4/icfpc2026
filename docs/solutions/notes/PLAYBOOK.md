# PLAYBOOK — the implementation agent's SOP

**What this is.** Every solution in this repo was built by roughly the same
sequence of moves, and the ones that went wrong went wrong at the same places.
This file is that sequence, distilled from what actually happened; nothing here
is invented. `OVERVIEW.md` is the architecture, `CLASSES.md` says which shape
to build, `NOTES.md` is the evidence and the scar tissue. **This file is the
order of operations**, so that a brief can say "solve X, it's a ring server,
playbook applies" instead of re-deriving the process every time.

Read this once, then read `CLASSES.md`'s row for your problem class, then the
NOTES sections that row points at. NOTES is ~1900 lines and is *not* meant to
be read front to back — it has a reading guide at "Where to look in this file".

---

## The standard flow

### 1. Transcribe, and assert

`problems/<name>.rkt`: a spec function that folds the round structure, **all**
public tests transcribed exactly, and a **load-time assertion that the spec
reproduces the published outputs**.

- Rounds concatenate within a test case, and some rounds expect no output.
- Name the **spec maximum** as constants at the top (`gb-MAXN` / `gb-MAXK` /
  `gb-CAP` in `problems/gradebook.rkt` is the model). Everything downstream —
  ring capacity, stress cases, the cost estimate — is sized off those numbers,
  and if they only exist in your head they will drift.
- If the problem has natural stress material, keep it in this file next to the
  spec (`tcp.rkt`, `subset.rkt` both do) with a load-time assertion that every
  case is **inside the spec box**.

That assertion is the transcription's only guarantee. A silent typo in a test
list is indistinguishable from a bug in the solution, and you will chase the
wrong one.

### 2. The measurement gate — when the algorithm is risky, prototype in Racket first

Do this when the algorithm is a **search**, when the state might not fit, or
when you cannot say in one sentence what the per-operation cost is. Skip it
when the cost is obviously affordable (a pipeline over ≤ 64 characters).

`problems/subset.rkt` is the worked example and the standard to hit. Before a
single grid existed it produced: node counts under each prune set (public n=20
case 112k → 25k nodes; adversaries 1.5M → 1), a measured **5.7 ring index-steps
per node**, a per-node cell budget derived from register pressure ("packing is
blocked by the off hand → one field per ring cell"), four *rejected*
architectures each killed with a number, and an **honest residual risk**
("n≥19, dense random, no solution will exceed the 15M cap; if casesPassed <
casesTotal that is the case to blame").

`harness/estimate.rkt` turns those counts into a verdict:

```racket
(require "harness/estimate.rkt")
(print-estimate (estimate-problem #:state-cells 80 #:ops-per-round 8 #:rounds 10
                                  #:ring-resident 80 #:walk-fraction 1.0
                                  #:circulating-fraction 0.2
                                  #:emit-protocol 'mark #:judge-class 'heavy-hidden))
```

It prints local ticks, **which term binds** (controller vs forwarder), a judge
tick range, the activity-cap load, and one of *comfortable / tight / redesign*.
It is a fitted estimator, ±20% on the five shipped server problems and useless
below ~100 ticks — its honest use is **comparing two designs for one problem**,
where the constants cancel.

The gate's output is a number and a verdict, not a feeling. If it says
*redesign*, redesign now: no layout work has been wasted yet.

### 3. Implement — littlelang first, hand-CFG as the fallback

**Try `l3/` first** when the room is register choreography. It reproduces hand
code op-for-op where the hand code was already optimal (the forwarder
`ff-blocks/corner` block-for-block, reverse's `rhead` including the `+` that
recovers `n`), and its **infeasibility diagnostic arrives before any layout
work** — the one-room brackets attempt prints `want A = c-1, B = 4; have A = c,
B = s.1` and proposes the ring spill, the room split, or backpack-and-count-out.

**Record refusals verbatim.** If littlelang cannot express your room, that
refusal is the compiler's specification and belongs in your report and in
`l3/RESULTS.md`'s roadmap — that is how items 1–5 of that roadmap got written.
Then hand-write the CFG; it is a fallback, not a failure.

Writing the CFG by hand, against the register model (A, B, write-only backpack;
`~`/`-` then `X` as a free 3-way compare; counters ride the ring when registers
run out; `harness/fragments.rkt` has the recurring shapes with their register
contracts):

- Mark hot loops `#:tight`. A tight body must be **plain ops ending in
  `(goto head)`** and must be the branch's **cw arm**; it can never be
  rail-entered from two arms; and it can **never hold a backtick literal**
  (the body lane is walked backwards — a compile error in both engines now).
- Build small constants by digit arithmetic, not literals. Brackets contains
  **no backtick literal at all**, which is why its width is set by its chains.
- Never write a mid-chain `goto` to a non-successor (a compile error now, but
  it was a silent walk into the wrong code for weeks).
- Design the **message** around the receiver's branch instruction: brackets' D
  sends `+t / -t / 0` so C's entire dispatch is one `X`. That is worth more
  than any optimization inside either room.
- Keep the server **never-halting**: blocking on exhausted input is free under
  emission-time scoring, and `H` is never needed.

### 4. Declare the world

Pick the template from `CLASSES.md`, then fill in only what is genuinely
per-problem: the CFG, the width sweeps, the **ring capacity sized by the SPEC
maximum**, the band formula, the F/O seeds, the `#:accept?` vetoes, the
`#:near` tank hints, and the channel order. The template deliberately does not
guess at these — each one has a NOTES scar behind it.

Register the problem in `harness/problems.rkt`: tests, spec, builder, movables,
stress generators, tick caps, submission id (or `#f`, and `submit` will refuse).
A problem still in flight goes in through `try-dynamic` so a half-written sol
file costs exactly one registry row.

### 5. Verify

```
racket harness/driver.rkt verify <problem…>
```

A **PASS is**: correct outputs with `status = timeout` (a correct server blocks
forever — that is what right looks like), the spec agreeing with the transcribed
outputs, the plain build reproducing `solutions/<name>.man` byte for byte
(modulo one trailing newline, which the driver normalizes and names), and a
clean literal lint. Anything less is RED.

### 6. Stress at the SPEC maximum, never at the public maximum

The public cases are not where the hidden set lives — memory's biggest public
case touches 41 distinct addresses against a spec maximum of 100, and that gap
*is* the 5.85× judge multiplier.

- Every stress case must be built at the spec maximum **and stay inside the
  spec box**. A case outside the box is worse than no case: it manufactures red
  against an input the judge will never send (brackets nested 63 deep against a
  spec depth of 32 cost a real investigation).
- Caps are **per case** (`stress-case-ticks`), because a suite is not uniform:
  memory's four cases emit at 311k / 24k / 7.3k / 2.2k.
- Learn to read the two failure messages. `CAP ARTIFACT` means a correct prefix
  ran out of ticks — raise that case's cap. `WRONG OUTPUT` means no cap will
  fix it, and the driver prints the index of the first difference.

### 7. Optimize

```
racket harness/driver.rkt optimize <problem> [--rounds N]
```

It measures the suite once and caps the search just above the worst observed
emit (this is a ~7× speedup on a sweep, not a nicety), then runs gravity with
multi-magnitude moves `(1 2 4 8)` and `#:clusters 'pairs`. Cluster moves exist
because greedy single moves provably park where the win is joint — memory's
F+O `(2 . -2)` shift is 37→35 as a pair and rejected as either half alone.

**When the search parks, suspect the declarations, not the search.** Sort's
last 13% was three declarations (which walls `ring-out` may use, where F is
seeded, where O is seeded), not more search. Reverse's remaining 7.9% is a
floorplan *structure* (I/O rooms inside the band) that no search over the
current structure can reach — an exhaustive 289-position I/O insertion sweep
confirmed it and is recorded so it is not re-run on a hunch.

### 8. Bake via OFFSET deltas — bytes are the fingerprint

`optimize` prints deltas **relative** to the sol file's `BASE-DELTAS`. Add them
componentwise into `BASE-DELTAS`, then re-verify: a plain `(build-…-grid)` must
still reproduce the saved `.man` byte for byte. That is the entire point of
baking.

- **Dimensions are not a fingerprint.** Two different delta sums both build
  memory at 34×34 and only one reproduces the saved grid. The repro check is
  what caught it; the "34 vs 36 mystery" was a stale hand-summed constant, and
  the whole error was summing against a comment instead of against the code.
- **The former is part of the bake.** `#:tank-former` is a property of the
  shipped world, in the same class as the deltas. Evaluating a former at a
  floorplan fitted to a different former measures nothing (the same bump former
  is 34×34 at its own floorplan and 36×36 at the melt's).
- Overwrite `solutions/*.man` only when **strictly better**, and keep the
  previous best (`memory-melt.man`, `tcp-prev31x32.man` are kept with the exact
  `#:deltas` call that rebuilds them).

### 9. Lint, submit, record

The literal lint runs inside `verify`. Backticks pair consecutively **per row
and per column** within a room, every cell between a pair must be a digit or a
space, and a clean paired column span *is* a vertical literal whose value is
range-checked in both directions — keep paired spans ≤ 18 digits.

```
racket harness/driver.rkt submit <problem>            # dry run, prints the curl
racket harness/driver.rkt submit <problem> --confirm  # actually POSTs
```

`submit` refuses without a registered problem id (a guessed id spends a
submission against the wrong test set) and refuses a build that does not pass
its own public tests. `SUBMIT.txt` has the raw `jq -Rs | curl` form, the poll
command, and the batch-check loop. Grading takes ~10s; a null id is a transient
failure — just resubmit.

Then **record the row in `CURRENTSCORES.txt`**, in the existing format:

```
PROBLEM (problem-id)
  file.man            cases  WxH    avgTicks N       score N       <- WINNER
    id <submission-id>  (date; local avg N, judge xM — one-line why)
```

Include the judge/local ratio. Those ratios are the calibration table the next
agent estimates from, and they are the only place they exist.

---

## Operational survival rules

These are about *the agent*, not the compiler, and each one has cost somebody a
session.

- **`timeout`-wrap every racket run**, 300s as the default budget. Racket
  builds and long sims do not fail fast on their own.
- **Foreground-sized chunks.** Backgrounded long commands silently restart, so
  a 20-minute sweep in the background is a 20-minute sweep that never finishes.
  Scope every command to complete in minutes; `optimize` takes an explicit
  `--rounds` budget for exactly this reason.
- **Never emit a large blob in one response.** There is a 64k output cap and
  hitting it kills the agent. Do not print a grid, a 100-value output list, or
  a whole file back; print the dimensions, the first difference, the diff.
- **Batch racket work into few processes.** The first build of a problem pays a
  ~70s shape-menu sweep and every later build *in the same process* is
  milliseconds (`compile-cfg` is memoized). `verify` and `stress` take a LIST
  of problems for this reason — `verify a b c` is one sweep each, three
  invocations is three sweeps each.
- **Cap ticks just above the observed emit in any sweep.** A correct server
  never halts, so the sim runs to the cap on every test even though scoring
  stopped at the emit tick; a 60000 cap on a 4k-tick program spends 93% of its
  time simulating a blocked man.
- **Measure caps, do not inherit them.** Worst stress emits on record: memory
  310844, sort 25814, tcp 17649, reverse 9030, brackets 4034.
- **Profile with a scratch COPY of `sim.rkt`** (a per-cell visit/blocked
  counter in stage 3) and run it with `#:max-ticks` at the emit tick, or
  post-completion blocking swamps the histogram 50:1 and every cell looks like
  a stall.
- **Local ticks are a ranking signal, not a score estimate.** The judge runs
  ~1.53× local on reverse/sort, 1.71× on tcp, 2.05× on brackets and 5.85× on
  memory. The *ratio between two programs on one problem* survives intact, so
  local scoring ranks correctly even where it mis-levels.

---

## Coexistence etiquette (several agents share this tree)

- **Declare ownership up front** and touch nothing outside it. State in your
  first message which files you will create and which you will edit.
- **New files over edits.** A new `problems/<name>-sol.rkt` collides with
  nobody; a new field on a positional struct collides with everybody. That is
  why `display-problems` and `stress-case-ticks` are *side tables* keyed by
  problem name rather than fields on `problem`.
- **Append last, and re-read first.** For `NOTES.md`, `CURRENTSCORES.txt` and
  `harness/problems.rkt`, do your append at the very end of your session, after
  re-reading the current file. Do not reorganize a file another agent is
  appending to — NOTES was deliberately *not* reorganized for exactly this
  reason, and got a reading guide instead.
- **Write atomically.** Build the whole new content and write once; never leave
  a file half-written between tool calls.
- **A transient load failure is transient.** Wait 60s and retry before
  investigating; another agent's file may be mid-write, and
  `harness/problems.rkt` loads in-flight sol files through `dynamic-require`
  inside a handler so that costs exactly one registry row.
- **Never `git commit`.** Stage or edit as asked; committing is the human's.

---

## The report format that works

Five sections, in this order. It is short on purpose: the caller reads the
report, not the files.

1. **What was built** — files created/edited, one line each, absolute paths.
2. **Measured numbers, before and after.** Dimensions, avg emit, local score,
   and the delta as a percentage. Never a number without its baseline.
3. **GRADER result + submission id** if it was submitted: `cases`, `WxH`,
   `avgTicks`, `score`, the id, and the judge/local ratio. If it was not
   submitted, say why (no problem id registered is the usual reason).
4. **Landmines, VERBATIM.** The exact judge message, the exact error text, the
   exact deltas. Paraphrased landmines are worthless — "a pipe flows out of the
   output room — the output room's pipe must flow into it at (21, 7)" is what
   let the next agent learn that judge coordinates are (col, row).
5. **Honest negatives.** What you tried that did not pay, with the number.
   "I/O pocket insertion: exhaustive, 289 positions per room, no improvement"
   is one of the most valuable entries in NOTES, because it stops the next
   agent re-running it on a hunch. Record refusals, rejected designs, and
   residual risks the same way.

---

## Command card

```
racket harness/driver.rkt verify   <problem…>   # tests + spec + repro + lint
racket harness/driver.rkt stress   <problem…>   # spec-maximum cases, per-case caps
racket harness/driver.rkt optimize <problem> [--rounds N]
racket harness/driver.rkt score    [problem…]   # local score table
racket harness/driver.rkt submit   <problem> [--confirm]
racket harness/estimate.rkt                     # the cost oracle's calibration table
raco test harness/estimate.rkt                  # asserts the fit has not drifted
```

`verify`/`stress` accept `all`. Flags work anywhere on the line (the driver
hand-rolls its argument scan because `parse-command-line` stops at the first
positional and silently ignored `--rounds`).

## Submission economics (a stopping-decision rule)

Submissions NEVER lower your score; test-case points are FRACTIONAL; and
eligibility requires passing at least one private case. Therefore: a
machine that passes most cases but predictably fails some (cap
shortfalls, adversary shapes) should be SUBMITTED, with the shortfall
documented — never withheld to "avoid burning a submission". Withholding
a working partial machine costs real points; submitting it costs
nothing. A later redesign supersedes it for free.

## Scratch hygiene

The session scratchpad is SHARED across all concurrent agents. Use a
unique subdirectory (scratchpad/<your-task-name>/) for everything;
never write to bare scratchpad/ filenames (dbg.rkt and notes-draft.md
have both been clobbered mid-run). When your job depends on another
agent's in-flight file (e.g. l3 demos), load it LAZILY per
harness/problems.rkt's dynamic-require pattern so their mid-save
doesn't kill your batch.

## Kernel tools (call BEFORE hand-deriving choreography)

See kernel/README.md. `find-kernels` before hand-writing any
register-choreography block or arguing for a room split — a refusal
certificate replaces hours of hand-proof (subset's hcap: 2.6s).
`check-encoding-range`/`check-sentinel-collision` before fixing any
encoding base or marker (would have caught the base-4 bracket bug and
the gradebook MARK-overflow). `check-ring-balance` before changing
which arm pushes back. `check-offset-protocol` before porting
MARK/sign-divert/bouncer to a new value domain. Kernel answers "does
the choreography exist"; l1/l2 answer "can it be drawn" — cells are
not room ticks.

## Re-attack discipline (coordinator practice)

Shipped is never finished. After each major infrastructure landing
(new architecture family, new search dimension, new protocol), re-score
every shipped solution against the new stack (harness/estimate + the
known field gaps in CURRENTSCORES) and queue a re-attack wherever the
projected improvement exceeds ~1.5x. Small-percentage rebakes ride
existing waves; architecture-class gaps (10x+) get fresh design agents.
A solution's judge/local ratio is re-earned on every rebuild — never
carried across a protocol or architecture change.

## Standing rule: no new problem fails silently

When an agent on a NEW (zero-points) problem reports its architecture
unbuildable, the automatic follow-up is the NAIVE PIVOT: forget score
entirely and ship ANY correct machine — however huge, slow, or ugly.
Fractional test-case points + eligibility (one private case) make a
passing md-100 monstrosity worth ~a full point. Full license under the
pivot: as many rooms as needed (the l1 ceiling is per-room — split
known-correct CFGs across sub-ceiling rooms with baton/relay
pipelines), hand-stacked floorplans, no optimization of any kind,
validate the multi-room protocol on mansim/mcfgsim first, submit on
the first passing case. Score is a later agent's problem; points are
now.

## Landmines added 2026-07-27 (endgame reintegration)

- **cfgsim-first is LAW.** Run `kernel/cfgsim.rkt` (or `mcfgsim`/`netsim` for
  multi-room) to a full public pass BEFORE `compile-cfg`, layout, or any split
  planning — every time, whatever the file's header claims. Gradebook's
  95-block CFG carried "validated" through three layout sessions and a split
  plan, then measured 1/7 on its first-ever cfgsim run. A CFG that cannot lay
  out is a nuisance; a CFG that lays out and is wrong is a submission spent.
- **Provenance compresses — scope every "validated" claim.** gbproto.rkt
  validated the PACKING (encoding arithmetic), not the CFG; when the scratch
  file died, that distinction compressed into "the CFG is validated" in both
  the brief and the sol-file banner. Rule: a validation claim names the
  ARTIFACT that ran and WHAT it exercised ("cfgsim 7/7 on gb-blocks", not
  "validated in Racket"). Claims without a live repro file decay to false.
- **Round-gated problems score LATENCY, not throughput.** The judge withholds
  round N+1 until round N answers; local avg measures the slowest man's cycle.
  Sudoku fit: judge avgTicks = 48.5 x single-round latency (0.04% on a blind
  prediction). Rank pipelined/station floorplans by max-dim^2 x latency (emit
  tick of a one-round run); local avg has already picked a wrong floorplan
  once. Signature of gating: judge/local ratio ~2x+ (sudoku x2.03, snake
  x2.67).
- **Multi-channel rooms: enumerate wall assignments against `targeting-ok?`
  BEFORE any assemble/pack work.** Seconds of pre-flight replaces a day of
  `no in-attachment satisfies targeting`. Cells must satisfy targeting first
  and minimise pipe length second (solve-attach in subset-split-sol.rkt,
  solve-pair in memory-station-split-sol.rkt); floorplan.rkt's
  plan-attach-cells does it backwards and fails any room with two channels of
  one kind. Also: l2 ranks by MANHATTAN distance, so a column band proves
  nothing (rows count equally), and a targeting split BY ROW is legal and
  sometimes the only one (reverse-rr).
- **A green cfgsim run does not size tanks.** cfgsim channels are unbounded;
  size every tank from the SPEC-maximum token count (lllm ring: 262), or the
  room deadlocks where the sim was green.
