PROBLEM ID: 15982f19-7465-4902-b7ef-c592e2b0150b

---
title: "ICFP Programming Contest 2026"
description: "The 29th ICFP Programming Contest runs July 24–27, 2026. An online programming competition for teams of any size, anywhere."
url: "https://icfpcontest2026.com/"
publisher: "ICFP Programming Contest 2026"
lang: "en"
date: "2026-07-27T02:37:57.000Z"
word_count: 1092
reading_time: "5 min read"
---

## Table of Contents

- [Format](#format)
- [Constraints](#constraints)
- [Examples](#examples)
- [Submit](#submit)

---

[← Problem Sets](https://icfpcontest2026.com/problem-sets)

Semester 4

[Solve in editor →](https://icfpcontest2026.com/problems/snake/editor)

**Scoring: footprint-tick.** **Tick cap: 15,000,000 per test case.** See [scoring](https://icfpcontest2026.com/grading#program-scoring), [rounds](https://icfpcontest2026.com/grading#round-based), and [displays](https://icfpcontest2026.com/grading#displays) for help.

Simulate a game of ["Snake"](https://en.wikipedia.org/wiki/Snake_%28video_game_genre%29) and draw it on a display.

In Snake, a player steers a line (the snake) as it grows and turns. The game runs on a 16x16 grid: the top-left corner is `0,0`, x grows right, y grows down.

Data is provided in [rounds](https://icfpcontest2026.com/grading#round-based). The first round is `sx sy`, the snake's starting position: a single cell, moving *right*. Commit a frame showing it. Every later round is one of:

- **Fruit spawn:** `1 fx fy`. A fruit spawns at `fx fy`; the game does not tick. Commit a new frame.
- **Direction change:** `2/3/4/5`. The snake's direction is set to `up/right/down/left` respectively from the next tick on. The game does not tick. Do not commit a new frame.
- **Tick:** `0`. Advance the game one tick (explained below). Commit a new frame.

On each tick the head advances one cell in the snake's current direction:

- Landing on a fruit **grows** the snake — the tail stays put, the fruit disappears.
- Otherwise the tail moves **before** the head (moving to where the tail just was is legal).
- If the head would land off the grid or on a cell the snake still occupies, the player loses and the test case ends. The snake does not move (draw it where it was before the tick).

At most one fruit is on the board at a time; fruit always appears in an empty cell. You will receive at most one direction change between consecutive ticks, and a direction change never reverses the snake (you will not receive `down` while the snake moves `up`).

**To draw this game to the [display](https://icfpcontest2026.com/grading#displays):**

- If the game is ongoing, draw the snake in **green (color 10)**
- If the game has ended, draw the snake in **red (color 9)**
- Draw fruit in **red (color 9)**
- Other cells should be left **black (color 0)**.

## Format

**Input.** A run of integers, until it ends.

the first round is the starting head position sx sy; every later round is a fruit spawn `1 fx fy`, a direction change `2` / `3` / `4` / `5` (up/right/down/left), or a clock tick `0`

```
input ⟶ int*

e.g.
  round 1:  12 3
  round 2:  0
  round 3:  0
```

**Output.** Your program must contain exactly one **16×16 display**; your solution must commit the expected frames for each round in order — they're pictured in the examples. Each round expects a single frame. [How display judging works →](https://icfpcontest2026.com/grading#displays)

## Constraints

- `0 ≤ x < 16`, `0 ≤ y < 16`
- At most 100 rounds per test case (including the starting round).

## Examples

**first bites** 13 rounds

Round 1

4 8

Round 2

0

Round 3

1 8 8

Round 4

3

no output

Round 5

0

Round 6

0

Round 7

0

Round 8

1 8 12

Round 9

4

no output

Round 10

0

Round 11

0

Round 12

0

Round 13

0

**game over at the wall** 5 rounds

Round 1

12 3

Round 2

0

Round 3

0

Round 4

0

Round 5

0

**full circle** 23 rounds

Round 1

3 5

Round 2

1 4 5

Round 3

0

Round 4

1 5 5

Round 5

0

Round 6

1 6 5

Round 7

0

Round 8

4

no output

Round 9

0

Round 10

5

no output

Round 11

0

Round 12

2

no output

Round 13

0

Round 14

3

no output

Round 15

0

Round 16

1 7 5

Round 17

0

Round 18

4

no output

Round 19

0

Round 20

5

no output

Round 21

0

Round 22

2

no output

Round 23

0

**second course** 22 rounds

Round 1

2 11

Round 2

1 3 7

Round 3

2

no output

Round 4

0

Round 5

0

Round 6

0

Round 7

0

Round 8

3

no output

Round 9

0

Round 10

1 1 4

Round 11

2

no output

Round 12

0

Round 13

0

Round 14

0

Round 15

5

no output

Round 16

0

Round 17

0

Round 18

1 13 11

Round 19

4

no output

Round 20

0

Round 21

0

Round 22

0

**the long game** 92 rounds

Round 1

9 2

Round 2

4

no output

Round 3

0

Round 4

0

Round 5

0

Round 6

1 0 1

Round 7

5

no output

Round 8

0

Round 9

2

no output

Round 10

0

Round 11

0

Round 12

0

Round 13

0

Round 14

5

no output

Round 15

0

Round 16

0

Round 17

0

Round 18

0

Round 19

0

Round 20

0

Round 21

0

Round 22

0

Round 23

1 0 4

Round 24

4

no output

Round 25

0

Round 26

0

Round 27

0

Round 28

1 15 3

Round 29

3

no output

Round 30

0

Round 31

2

no output

Round 32

0

Round 33

3

no output

Round 34

0

Round 35

0

Round 36

0

Round 37

0

Round 38

0

Round 39

0

Round 40

0

Round 41

0

Round 42

0

Round 43

0

Round 44

0

Round 45

0

Round 46

0

Round 47

0

Round 48

1 2 1

Round 49

2

no output

Round 50

0

Round 51

0

Round 52

5

no output

Round 53

0

Round 54

0

Round 55

0

Round 56

0

Round 57

0

Round 58

0

Round 59

0

Round 60

0

Round 61

0

Round 62

0

Round 63

0

Round 64

0

Round 65

0

Round 66

1 13 13

Round 67

4

no output

Round 68

0

Round 69

0

Round 70

0

Round 71

0

Round 72

0

Round 73

0

Round 74

0

Round 75

0

Round 76

0

Round 77

0

Round 78

0

Round 79

0

Round 80

3

no output

Round 81

0

Round 82

0

Round 83

0

Round 84

0

Round 85

0

Round 86

0

Round 87

0

Round 88

0

Round 89

0

Round 90

0

Round 91

0

Round 92

1 14 8

## Submit

Sign in to submit solutions. [Sign in](https://icfpcontest2026.com/login)
