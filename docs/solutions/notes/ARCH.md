# ARCH — the streaming/belt + register-resident architecture study (living doc)

Owner: beltarch agent, 2026-07-26.  Files owned: this file,
`probes/belt-*.man`, `scratchpad/beltarch/*`.  Everything else read-only.
Measured on the judge-exact `sim.rkt` (`sim-pipe-moves` diagnostic for
steady-state flux).  Context: top-10 leaderboard numbers imply a uniform
13-17x lead on every ring problem (memory top ~5.05M vs our 66.5M, sort
~250K vs 4.25M, sudoku ~1.05M vs 14.56M); this doc measures the candidate
architecture family "men as memory, pipes as network" bottom-up.

---

## Milestone 1 — belt microbench: the relay-station primitive (MEASURED)

**Setup.** K station rooms (interior Wi x 2) in a pipe loop; station 0
injects N values from the input room via `R`, everything then circulates
forever.  A station is one man on a cyclic walk `> ... v / ^ ... <` whose
pattern cells tile `rs` (dense relay), `r~s` (relay + 1 op of work), or one
`r` + one `s` on a 12-cell walk (sparse = emulation of the compiled tight
circuit that every shipped ring server runs, NOTES' ~8-12 ticks/cell).
Throughput measured as pipe-move rate / loop-pipe-cells = values crossing a
fixed point per tick ("flux"); 1/flux = effective ticks per value streamed
past a station — the number that multiplies every seek/lap.  Two-horizon
measurement (4k/8k ticks) so fill transients cancel.  Generator + runner:
`scratchpad/beltarch/belt-bench.rkt` (`--emit` writes `probes/belt-*.man`).

**Key rule found while building: a pipe cannot return to its own source
room** (reference.md pipe rule 4: terminates only on a border of a room
*other than the source*), so every loop needs >= 2 rooms.  Corners of the
walk cost direction ops; `@` is a nop when walked over (verified in
sim.rkt exec), so the man parks inside the cycle.

**Saturated steady-state throughput (ticks per value past a station):**

| config | K | Wi | t/v saturated | predicted 2Wi/(Wi-3) | notes |
|---|---|---|---|---|---|
| sparse (tight-circuit emulation) | 2 | 6 | **12.23** | 2Wi=12 | matches NOTES' 8-12 t/cell shipped reality |
| dense `rs` | 2 | 6 | 4.08 | 4.0 | |
| dense `rs` | 2 | 14 | 2.59 | 2.55 | |
| dense `rs` | 2 | 30 | **2.26** | 2.22 | asymptote; floor is 2.0 (r+s) |
| dense `rs` | 4 | 6 | 4.15 | 4.0 | K does not change throughput |
| dense `rs` | 8 | 6 | 4.23 | 4.0 | ditto (pipelines cleanly, no degradation) |
| `r~s` (1 op work/value) | 2 | 8 | 5.43 | 16/3=5.33 | work adds ~1.3 t/v per op here |
| `r~s` | 4 | 8 | 5.51 | 5.33 | |

**Speedup: dense relay is 3.0-5.4x the compiled tight circuit** (12.23 →
4.08 narrow / 2.26 wide).  The mechanism is not "more men" — it is **many
r/s sites per walk cycle** amortizing the walk: all r's in a 1-in-1-out room
target the same pipe regardless of position, so a 2-row room tiled `rsrs...`
relays (Wi-3) values per 2Wi-tick lap.  A single man gets the same 2.26 t/v;
K stations only matter for (a) closing the loop (>=2 rooms forced), (b)
splitting per-value *work* across stages, (c) geometry/area.

**Fill latency is the catch.**  Below saturation, flux = N / (P + ~10):
lap time is pipe-transit-bound (~1 tick/cell + ~2-5 per station), so a belt
only beats the tight circuit when **N is a large fraction of loop pipe cells
P** (measured knee: N/P >~ 0.35-0.5).  Population lap time, N=48 on P~122:
dense 128 ticks vs sparse 587.  A belt sized for capacity C that usually
holds << C values runs latency-bound and pays nothing.

**Activity (step-cap) check at this scale.**  Saturated dense: ~59 pipe
moves/tick + K men ~ 61 activity/tick vs sparse ~10.7.  Per unit of WORK
(one value past a station) both cost the same pipe moves (each value-lap =
P moves regardless of speed), so belts do not inflate activity per op — they
compress the same activity into fewer ticks.  Judge-scale check deferred to
the memory/sort application milestone.

**Man-cycle variants.**  `U` (receive-and-turn-away) buys nothing on a
1-in-1-out relay: it forces a return walk past the send cell and re-executes
it (duplicate send) or needs the same corner budget; the dense 2-row tile is
strictly better.  `x`-cornering = same 4-corner cost.  Verdict: **the dense
2-row `rsrs` tile is the canonical station**; corners cost 6/(Wi-3) t/v of
overhead, i.e. go wide, not clever.

**What this kills already:** a belt CANNOT explain a 13-17x lead on its own.
Streaming state past compare stations caps at ~(2.3 + work) t/v vs ~10 —
a 3-5x, and O(ring) per op remains O(ring).  The 13-17x needs the state to
stop traversing pipes at all: register-resident stations (milestone 2).

---

## Milestone 2 — register-resident sudoku core, 2-station prototype (MEASURED)

`scratchpad/beltarch/sudoku-station.rkt`; grid saved as
`probes/belt-sudoku-station.man` (43x10, 6 rooms: I -> D router -> S1/S2
state stations -> M merge -> O).  **Correct: 45/45 random + handcrafted
cases match `sudoku-spec`** (row/col/box conflicts, conflict-terminated and
fully-valid streams).

**The architecture.**  No ring.  The 27-unit x value bitboard lives in the
station men's **B registers, 2 values packed per register** (54 bits used;
prototype restricted to v in 1..4 = 2 stations; full scale is 5 stations).
Per round the dispatcher routes a pre-shifted test word w = mask3 << 27h to
the owning station, twice.  Station cycle is **6 ops, B never leaves
residence**:

    r (A=w)  & (A = w AND state = conflict word)  s (-> merge)
    r (w again)  ~ (A = w XOR state = updated state)  M (B = it)

The xor IS the update because a conflict ends the case (post-conflict state
is dont-care) — same insight as shipped sudoku's ring handle, minus the
ring.  S2 relays S1's conflict word; M does `r M r + X` (sum of conflict
words is >= 0, zero iff valid): ok arm `1 s`, conflict arm `0 s H` (halting
M after the final 0 is free; other men keep pipes draining).

**Measured, same rounds fed to both programs:**

| | first-round latency | marginal ticks/round | pipe-moves/round | dims |
|---|---|---|---|---|
| prototype | **45** | **20.0** | 46 | 43x10 (unpacked) |
| shipped sudoku.man | 285 | **211** | 573 | 32x32 |

**10.5x on throughput, 6.3x on latency, 12x less activity.**  The 20-tick
marginal is M's 20-cell walk cycle (current bottleneck; D is 14).  Of the
45-tick latency ~26 ticks are pipe transit through deliberately sprawled
prototype pipes (8-18 cells); a packed layout cuts that to ~8.

**Honest deltas to a real solution:**
- Input here is synthetic pre-split words; the real front end (r c v ->
  mask3, v-decode routing) is NOT included.  Shipped pays that same work
  inside its 211, so add its measured cost — the shipped arithmetic room's
  round work is ~15-25 ops — to the prototype's path: ~+20 ticks.
- Full scale = 5 stations (9 values x 27 bits at 2 values/register): D
  grows a v-decode X-ladder, and the conflict-word merge chain relays
  through up to 4 stations: ~+10-20 latency worst case (chain), less as a
  2-level tree.
- Round gating puts LATENCY, not marginal, on the judge's critical path
  (NOTES: sudoku judge ratio is a floorplan function, x1.41 on shipped) —
  which is exactly where this architecture wins: packed full-scale gated
  estimate **~55-70 ticks/round vs shipped's effective ~300**.

**Projection.**  ~4-5x on judge ticks, plus area: the register-resident
build has no tanks and no 27-cell ring — rough packed footprint ~24x24 vs
32x32.  Score estimate: 14.56M -> **~2-3M** (top-10 sudoku is 1.05M, so
this closes most but likely not all of the gap without further front-end
work).  The architecture family is CONFIRMED as the field's lever: state in
registers, pipes only for per-round messages, verdict by arithmetic merge.

---
