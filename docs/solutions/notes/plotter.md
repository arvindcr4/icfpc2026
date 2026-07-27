PROBLEM ID: 0c3e3d4d-2901-45f1-81cf-5704d49c9139

---
title: "ICFP Programming Contest 2026"
description: "The 29th ICFP Programming Contest runs July 24–27, 2026. An online programming competition for teams of any size, anywhere."
url: "https://icfpcontest2026.com/"
publisher: "ICFP Programming Contest 2026"
lang: "en"
date: "2026-07-27T02:36:37.000Z"
word_count: 500
reading_time: "2 min read"
---

## Table of Contents

- [Format](#format)
- [Constraints](#constraints)
- [Examples](#examples)
- [Submit](#submit)

---

[← Problem Sets](https://icfpcontest2026.com/problem-sets)

Semester 2

[Solve in editor →](https://icfpcontest2026.com/problems/plotter/editor)

**Scoring: footprint-tick.** See [scoring](https://icfpcontest2026.com/grading#program-scoring), [rounds](https://icfpcontest2026.com/grading#round-based), and [displays](https://icfpcontest2026.com/grading#displays) for help.

Graph line segments on a display.

A line segment is composed of two coordinate pairs `x0 y0` and `x1 y1` that define its start and end points.

Each [round](https://icfpcontest2026.com/grading#round-based) supplies one line segment. Draw the segment on the [display](https://icfpcontest2026.com/grading#displays) in **bright white (color 15)**; every other pixel stays black. Commit the segment only when it is finished. Lines do not persist between rounds.

Your line must consist of *exactly* the pixels produced by Bresenham's line drawing algorithm (in its symmetric error form). In pseudocode:

```
dx = abs(x1 - x0);  sx = (x0 < x1) ? 1 : -1
dy = -abs(y1 - y0); sy = (y0 < y1) ? 1 : -1
err = dx + dy
loop forever:
    plot(x0, y0)
    if x0 == x1 and y0 == y1: stop
    e2 = 2 * err
    if e2 >= dy: err = err + dy; x0 = x0 + sx
    if e2 <= dx: err = err + dx; y0 = y0 + sy
```

The algorithm is direction-sensitive: A→B may select different pixels than B→A, so draw from `(x0, y0)` to `(x1, y1)` as given.

## Format

**Input.** The integers `x0`, `y0`, `x1`, `y1`.

```
input ⟶ x0 y0 x1 y1

e.g.
  round 1:  4 20 27 3
  round 2:  2 2 29 2
  round 3:  16 0 16 23
```

**Output.** Your program must contain exactly one **32×24 display**; your solution must commit the expected frames for each round in order — they're pictured in the examples. Each round expects a single frame. [How display judging works →](https://icfpcontest2026.com/grading#displays)

## Constraints

- `0 ≤ x0, x1 < 32`, `0 ≤ y0, y1 < 24` — endpoints are always on the display
- at most 20 rounds per test case

## Examples

**main diagonal**

in: 0 0 31 23

screen:

**three rounds** 3 rounds

Round 1

4 20 27 3

Round 2

2 2 29 2

Round 3

16 0 16 23

**one pixel**

in: 9 5 9 5

screen:

**both ways** 4 rounds

Round 1

0 0 8 4

Round 2

8 4 0 0

Round 3

20 3 21 15

Round 4

21 15 20 3

**around the border** 4 rounds

Round 1

0 0 31 0

Round 2

31 0 31 23

Round 3

31 23 0 23

Round 4

0 23 0 0

**octant fan** 8 rounds

Round 1

15 11 29 16

Round 2

15 11 20 22

Round 3

15 11 10 22

Round 4

15 11 1 16

Round 5

15 11 1 6

Round 6

15 11 10 0

Round 7

15 11 20 0

Round 8

15 11 29 6

## Submit

Sign in to submit solutions. [Sign in](https://icfpcontest2026.com/login)
