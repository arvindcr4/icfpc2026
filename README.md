# ICFP Programming Contest 2026 — team `arvindcr4`

Solutions to the Littleman (`.man`) problem sets.

## Solved

### Triangle — 19/19 cases, score 5819
```
+-+  +-----------+  +-+
|I|>>|@rM*+W1W}sH|>>|O|
+-+  +-----------+  +-+
```

`T(n) = n(n+1)/2`, computed as `(n² + n) >> 1` so no division is needed:

| op | effect | A | B |
|----|--------|---|---|
| `r` | receive n from the input pipe | n | 0 |
| `M` | copy main → off | n | n |
| `*` | A = A×B | n² | n |
| `+` | A = A+B | n²+n | n |
| `W` | swap | n | n²+n |
| `1` | load literal | 1 | n²+n |
| `W` | swap | n²+n | 1 |
| `}` | A = A >> B (arithmetic) | (n²+n)/2 | 1 |
| `s` | send to the output pipe | | |
| `H` | halt | | |

Grid is 23×3, so `area² = 23² = 529` and `avgTicks = 11` → **529 × 11 = 5819**.

## Notes on the language that cost us time

- A pipe **must begin with an arrowhead** whose backward cell sits on the source
  room's border — `--->` fails to parse as a pipe at all. `>>` is the shortest
  legal pipe (both ends need arrowheads; minimum length 2). Getting this wrong
  gives a clean load but `no-pipe` errors on every case.
- Score is `max(width, height)² × avgTicks`, so the bounding box dominates:
  trimming the pipes from `--->` to `>>` alone took `area²` from 729 to 529.
- The submission API sits behind Cloudflare and rejects plain scripted clients
  with `403 error code: 1010`; submit from a real browser session.
