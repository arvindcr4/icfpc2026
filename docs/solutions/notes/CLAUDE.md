# POST-COMPACTION BOOTSTRAP (contest endgame)

DEADLINE: 05:00 PDT 2026-07-27. Check `date` FIRST and often — do not
estimate time. Limit reset ~03:40; lead is asleep; an automated
"continue" prompt = GO SIGNAL: no token limits, RACE.

## Immediate actions on resume
1. `date`. Then read task list (#16 = endgame protocol) + CURRENTSCORES.txt.
2. Resume EVERY killed agent via SendMessage (ids in transcript/task
   notifications; a resume message with "continue from transcript +
   file state" suffices). All agents have submission authority.
3. Sweep solutions/*.man for unsubmitted greens: verify via sim, submit
   per SUBMIT.txt (jq -Rs + curl; ids in CURRENTSCORES/problem .md files).
4. By 04:45: final sweep — direct all agents to submit partial states NOW.

## Who was racing at compaction (~02:05)
- gradebook: NAIVE PIVOT running (split 95-block CFG, baton pipeline,
  submit on any pass; id d1415447…)
- subset-final: serpentine orientation fix (2 pts, id b5e48adc… unspent)
- lllm relay: stepper agent (resolution (a), problems/lllm-cfg.rkt) →
  guillotine agent does layout+submit (id d91edb43…)
- llm: building on lllm core (problems/llm-recon.md; id 383158cc…)
- guillotine agent: plotter repack (~7.5x, submit) → then lllm layout
- snake-repack (sonnet): guillotine over snake, submit < 57 max-dim
- sort-relay: hand-lay C hot circuits, submit < 4,193,459
- pathfinder: VM phases 2-4 as GENERATED blocks → layout → submit (2 pts)

## Standing rules (full text in PLAYBOOK.md — trust it)
- Naive pivot on any new-problem failure: ship ANY correct machine.
- Submit early, resubmit per improvement; submissions never lower scores.
- Terse output (64k cap kills agents); generate CFGs, never type them.
- Files are truth; transcripts die. NOTES.md = institutional memory.

## Scoreboard at compaction (judge, best per problem)
triangular 832* · memory 66.5M · reverse 958K · sort 4.19M · tcp 6.06M ·
sudoku 4.97M · brackets 922K · history 8281 · matmul 47.5M · snake 48.6M ·
plotter 145.9M (repack in flight) · subset/gradebook/pathfinder/llm/lllm: 0, in flight.
