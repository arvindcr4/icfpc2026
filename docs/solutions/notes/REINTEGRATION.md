# REINTEGRATION — cross-applications from tonight's findings (03:55, 2026-07-27)

Ranked by (expected gain / effort) for the remaining hour. Items 1-4 were
messaged to main at 03:52. Sources: NOTES.md tonight's sections, lllm-triage.md,
llm-recon.md, gradebook-sol.rkt banner + scratchpad/gbsplit-simcheck.rkt,
scratchpad/lllm-handoff.md.

## 1. snake (and every round-gated repack) <- sudoku's latency law
Tactic: rank floorplans by max-dim^2 x SINGLE-ROUND LATENCY (emit tick of a
one-round run), never local avgTicks. Sudoku measured judge = 48.5 x latency
(predicted a submission to 0.04%); local avg picked the WRONG sudoku floorplan.
Snake judge/local x2.67 = same signature. Gain: protects the in-flight repack
pick, worth up to the 5-10% between candidate plans. Effort: nil (ranking rule).

## 2. gradebook <- sentinel-sign + counted rotate (from its own postmortem)
STATUS 03:57: EXECUTED — gradebook agent reports 7/7 on cfgsim via the counted
rotate (per coordinator). Remaining risk is layout/tank sizing only; item kept
for the record.
Tactic: 0-sentinel ends a lap on X alone -> BP freed -> counted rotate is
2 blocks, replacing the 12-block av*/tv* rotation ladders — which are exactly
where the 1/7 failure localises (only K=1 passes; raw packed cells reach
output). Deleting the rotation fixes the suspect code AND buys back the room
budget that forced the 3-way split. Gain: 0 -> ~2 pts. Effort: redirects the
in-flight pivot, no new lane.

## 3. lllm layout <- plotter's linter + snake's pipe rule
Tactic: judge-lint! from problems/plotter-sol.rkt (l2's check-literals! is
backwards on columns — plotter was REJECTED AT LOAD); ring tank >= 262 (cfgsim
channels are unbounded, a green cfgsim run does not size tanks); |nD-nS| <= 3;
painter<->stepper is the only register-dead seam. All in
scratchpad/lllm-handoff.md. Gain: protects 2 pts in flight. Effort: nil.

## 4. lllm <- llm, one-way drop-in backstop
Tactic: if the LLM world assembles, submit the SAME .man to the lllm id
(d91edb43-...) — an LLM machine is automatically a correct LLLM machine
(lllm-triage.md §2). Converse is FALSE. Gain: free insurance on 2 pts.
Effort: one curl.

## 5. matmul <- floorplan.rkt guillotine packer
Tactic: pack matmul-sol.rkt's rooms (55x63 builder world exists). Precedent:
packer beat sudoku's hand-drawn manual by 5% and the hand-stack by 42.5%.
Current winner is a hand 48x45 @ 47.5M, NOT builder-reproducible — packer win
would also restore reproducibility. Gain: ~5% of 47.5M if it beats 48x45,
uncertain. Effort: ~30 min if rooms feed the packer cleanly.

## 6. sort <- reverse-rr's two moves (94.5 -> ~55 ticks/value, 2.24x there)
Tactics, separable: (a) pass counter leaves the ring into B (`0 +` reads B
without disturbing it) — sort pays B=SENT+subtract where reverse now pays a
sign test; (b) direct C->O emission `(r ring)(s out)`, F = tcp's 2-op bouncer,
deletes the 9-cell MARK literal walked per emitted value; (c) CAP audit: both
tanks get #:capacity each, reverse's CAP 18->9 bought a max-dim (tcp's
"caps 6..20 identical" is NOT general). Gain: reverse got 2.24x; sort's emit
path is the same MARK shape. Effort: (c) is <20 min and worth handing
sort-relay; (a)+(b) is an hours-scale rebuild — too late tonight, top of the
post-contest queue.

## 7. Any future station world <- guillotine packer + targeting-ok? solver
Tactic: the packer's plan-attach-cells ranks by pipe length and fails any room
with two channels of one kind; solve-attach (subset-split-sol.rkt) / solve-pair
(memory-station-split-sol.rkt) satisfy targeting-ok? FIRST, then minimise
length. Combining them is "the missing tool", measured worth ~1.9x on
memory-split (55x55 packable vs 80x70 shipped) and it is what refused subset.
Gain: ~2x on station worlds. Effort: too big tonight; the ONE named next tool.

## 8. Not reached / explicitly deferred
- history table-dispatch decoder (~8281 -> ~7569): still blocked on placement
  tooling; the guillotine packer might be that tooling — untested.
- reverse's auto-terminating unpack cycle (U1/U2/U3, q=0 self-stop): good
  idiom, no target tonight.
- subset serpentine second orientable family: already the in-flight agent's
  exact task, nothing to add from here.
- brackets/tcp/memory CAP audits beyond sort: same move as 6(c), lower stakes
  (tcp measured insensitive; memory's floorplan is hand-tuned around its caps).
