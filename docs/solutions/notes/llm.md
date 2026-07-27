PROBLEM ID IS 383158cc-1891-46b2-9a9f-d9ed2661c85d

---
title: "ICFP Programming Contest 2026"
description: "The 29th ICFP Programming Contest runs July 24–27, 2026. An online programming competition for teams of any size, anywhere."
url: "https://icfpcontest2026.com/"
publisher: "ICFP Programming Contest 2026"
lang: "en"
date: "2026-07-27T02:50:12.000Z"
word_count: 3323
reading_time: "13 min read"
---

## Table of Contents

- [The LLM Language](#the-llm-language)
- [Ticks and halting](#ticks-and-halting)
- [Pipes](#pipes)
- [Drawing](#drawing)
- [Input and output](#input-and-output)
- [Format](#format)
- [Constraints](#constraints)
- [Examples](#examples)
- [Submit](#submit)

---

[← Problem Sets](https://icfpcontest2026.com/problem-sets)

Semester 4

[Solve in editor →](https://icfpcontest2026.com/problems/little-little-man/editor)

**Scoring: footprint-tick.** **Tick cap: 50,000,000 per test case.** See [scoring](https://icfpcontest2026.com/grading#program-scoring), [rounds](https://icfpcontest2026.com/grading#round-based), and [displays](https://icfpcontest2026.com/grading#displays) for help.

Interpret an LLM program and show its state on a display.

## The LLM Language

Little little man (LLM) is a simple subset of the littleman language that you have learned during this course. *All valid LLM programs are valid littleman programs*. This problem will not recap the basics of littleman programs; consult the [textbook](https://icfpcontest2026.com/textbook), [language reference](https://icfpcontest2026.com/language-reference), and [editor](https://icfpcontest2026.com/editor) if you're confused.

An LLM program is a grid containing one or more rooms potentially connected with pipes. Each room holds a single `@` representing a little man. The `@` moves with the man: the cell where he started is ordinary empty space, and walking back over it does nothing. Rooms and pipes are drawn exactly as in littleman.

The full set of operations in the LLM language is:

- `^` `>` `v` `<` — set heading to N / E / S / W
- `0` – `9` — `A = n`
- `M` — `B = A`
- `+` — `A = A + B`
- `-` — `A = A - B`
- `X` — turn clockwise if `A > 0`, counterclockwise if `A < 0`, don't turn if `A = 0`
- `s` — send `A` into the nearest outgoing pipe
- `r` — receive a value into `A` from the nearest incoming pipe
- `H` — halt: the man stays on the `H` forever while the other men keep running

## Ticks and halting

On each tick every man executes the operation he is standing on (if applicable) and *then* advances in his current direction. All men act on every tick.

The program halts when every man has halted on an `H` — or the moment any man hits a wall: the whole program stops and every man freezes where he stands, including the man on the wall cell. The tick in which a man steps onto a wall completes in full — every other man still executes and moves on that tick — and then everything freezes. (This differs from littleman, where hitting a wall is an error.)

**The programs you receive will be well-formed:** rooms and pipes parse, every room has a single `@` inside, and `s` and `r` are only ever executed in a room that has a pipe in the required direction. Other characters will either be spaces or valid operations.

## Pipes

Each pipe cell holds at most one value. On every tick, before the men act, every value in a pipe advances one cell toward its destination if the next cell is free.

**Every value sent into a pipe is between `-9` and `9`.**

- `s` writes `A` into the pipe's first cell (the arrowhead leaving the sender's room). If that cell is occupied, the man **blocks**: he stays on the `s`, retrying every tick, and only moves on once the send succeeds.
- `r` takes the value in the pipe's last cell (the arrowhead entering the receiver's room). If no value has arrived yet, the man blocks on the `r` the same way.
- When a room has more than one pipe in the relevant direction, `s` and `r` use the **nearest** pipe: the one whose arrowhead at this room is closest to the man's current cell by Manhattan distance. On an exact tie, the arrowhead earliest in reading order (top-to-bottom, then left-to-right) wins.

Because pipes move before the men act, a value that arrives at the pipe's last cell on some tick can be received by an `r` that same tick — and a man blocked on `s` against a full pipe sends on the tick *after* the receiver's pop makes room.

## Drawing

Draw the LLM program with its top-left corner at the top-left corner of your [display](https://icfpcontest2026.com/grading#displays). Your display will be 16x16; if your LLM program is smaller than that leave the pixels outside of the program black.

You should use color `9` (bright red) to represent the current position of every little man. When a little man is on top of an instruction or a wall, draw *him*, not the thing he is on top of.

**Values in pipes are animated.** A pipe cell holding a value is drawn `14` (bright cyan); an empty pipe cell is drawn `6` (cyan). Your frames must show every value at the exact cell it occupies, step by step, as it moves toward its destination.

Other cells have fixed colors similar to what you see in the editor:

- room walls — 4 (blue)
- `<` `>` `^` `v` `X` `H` — 3 (yellow)
- `0` – `9` — 8 (gray)
- `M` — 12 (bright blue)
- `+` `-` — 10 (bright green)
- `s` `r` — 13 (bright magenta)
- pipe cells (bodies and arrowheads) — 6 (cyan)
- a pipe cell currently holding a value — 14 (bright cyan)
- space — 0 (black)

## Input and output

The first [round](https://icfpcontest2026.com/grading#round-based) supplies two integers `W H` and then `W*H` [ASCII](https://icfpcontest2026.com/grading#ascii) values that comprise a valid LLM program, in row-major order (top row first, left to right). Commit a single frame showing the starting state.

Subsequent rounds supply one integer `k`. Step the program forward `k` ticks or until it halts, whichever comes first. Then commit a single frame showing the state of the program.

Test cases end after the round where the LLM program halts.

## Format

**Input.** A run of integers, until it ends.

the first round is the LLM program: W H, then W·H ASCII codes (row-major); every later round is one step command k

```
input ⟶ int*

e.g.
  round 1:  4 4 43 45 45 43 124 64 118 124 124 32 72 124 43 45 45 43
  round 2:  1
  round 3:  1
```

**Output.** Your program must contain exactly one **16×16 display**; your solution must commit the expected frames for each round in order — they're pictured in the examples. Each round expects a single frame. [How display judging works →](https://icfpcontest2026.com/grading#displays)

## Constraints

- `4 ≤ W, H ≤ 16`
- `1 ≤ k ≤ 64`
- at most 3 rooms and at most 2 pipes per program
- at most 20 total pipe cells per program
- at most 30 rounds and at most 100 ticks per test case
- no step commands arrive after the program halts
- every value sent into a pipe is between `-9` and `9`

## Examples

**first steps** 4 rounds

Round 1

4 4 43 45 45 43 124 64 118 124 124 32 72 124 43 45 45 43

Round 2

1

Round 3

1

Round 4

1

**countdown relay** 16 rounds

Round 1

13 11 43 45 45 45 45 45 45 45 45 45 45 45 43 124 64 49 77 52 62 45 115 88 57 72 32 124 124 32 32 32 32 32 32 32 32 32 32 32 124 124 32 32 32 32 94 32 32 60 32 32 32 124 43 45 45 45 45 45 45 45 45 45 45 45 43 32 32 32 32 32 32 32 118 32 32 32 32 32 32 32 32 32 32 32 32 118 32 32 32 32 32 43 45 45 45 45 45 45 45 45 45 45 45 43 124 64 114 77 114 43 114 45 114 48 88 72 124 124 32 32 32 32 32 32 32 32 32 32 32 124 43 45 45 45 45 45 45 45 45 45 45 45 43

Round 2

2

Round 3

5

Round 4

5

Round 5

2

Round 6

1

Round 7

5

Round 8

2

Round 9

1

Round 10

1

Round 11

6

Round 12

3

Round 13

3

Round 14

3

Round 15

1

Round 16

42

**hello neighbor** 8 rounds

Round 1

16 5 43 45 45 45 45 45 43 32 32 32 43 45 45 45 45 43 124 64 51 115 72 32 124 32 32 32 124 64 114 88 32 124 124 32 32 32 32 32 124 62 45 62 124 32 32 72 32 124 124 32 32 32 32 32 124 32 32 32 124 32 32 32 32 124 43 45 45 45 45 45 43 32 32 32 43 45 45 45 45 43

Round 2

1

Round 3

1

Round 4

1

Round 5

1

Round 6

1

Round 7

1

Round 8

1

**bucket brigade** 5 rounds

Round 1

9 13 43 45 45 45 45 45 45 45 43 124 64 55 115 50 115 72 32 124 43 45 45 45 45 45 45 45 43 32 32 32 32 118 32 32 32 32 32 32 32 32 118 32 32 32 32 43 45 45 45 45 45 45 45 43 124 64 114 115 114 115 72 32 124 43 45 45 45 45 45 45 45 43 32 32 32 118 32 32 32 32 32 32 32 32 118 32 32 32 32 32 43 45 45 45 45 45 45 45 43 124 64 32 32 114 32 114 72 124 43 45 45 45 45 45 45 45 43

Round 2

3

Round 3

1

Round 4

4

Round 5

1

**ping pong** 11 rounds

Round 1

16 5 43 45 45 45 45 45 45 43 32 32 43 45 45 45 45 43 124 64 53 115 32 114 72 124 62 62 124 64 114 115 72 124 43 45 45 45 45 45 45 43 32 32 43 45 45 45 45 43 32 32 32 32 94 32 32 32 32 32 32 32 118 32 32 32 32 32 32 32 94 45 45 45 45 45 45 45 60 32 32 32

Round 2

1

Round 3

1

Round 4

1

Round 5

2

Round 6

4

Round 7

2

Round 8

1

Round 9

2

Round 10

1

Round 11

30

**switchboard** 9 rounds

Round 1

16 16 43 45 45 45 45 43 32 32 32 43 45 45 45 45 45 43 124 64 49 115 72 124 32 32 32 124 64 50 115 72 32 124 43 45 45 45 45 43 32 32 32 43 45 45 45 45 45 43 32 32 118 32 32 32 32 32 32 32 32 32 118 32 32 32 32 32 118 32 32 32 32 32 32 32 32 32 118 32 32 32 32 32 118 32 32 32 32 32 32 32 32 32 118 32 32 32 43 45 45 45 45 45 45 45 45 45 45 45 45 45 45 43 124 64 32 32 32 32 32 114 32 32 114 32 72 32 32 124 124 32 32 32 32 32 32 32 32 32 32 32 32 32 32 124 124 32 32 32 32 32 32 32 32 32 32 32 32 32 32 124 43 45 45 45 45 45 45 45 45 45 45 45 45 45 45 43 32 32 32 32 32 32 32 32 32 32 32 32 32 32 32 32 32 32 32 32 32 32 32 32 32 32 32 32 32 32 32 32 32 32 32 32 32 32 32 32 32 32 32 32 32 32 32 32 32 32 32 32 32 32 32 32 32 32 32 32 32 32 32 32 32 32 32 32 32 32 32 32 32 32 32 32 32 32 32 32

Round 2

1

Round 3

1

Round 4

3

Round 5

1

Round 6

1

Round 7

1

Round 8

3

Round 9

1

**traffic jam** 15 rounds

Round 1

16 8 43 45 45 45 45 45 45 45 45 43 32 32 32 32 32 32 124 64 49 115 50 115 51 115 72 124 32 32 32 32 32 32 43 45 45 45 45 45 45 45 45 43 32 32 32 32 32 32 32 32 32 118 32 32 32 32 32 32 32 32 32 32 32 32 32 32 32 118 32 32 32 32 32 32 32 32 32 32 32 32 43 45 45 45 45 45 45 45 45 45 45 45 45 45 45 43 124 64 32 32 32 32 32 32 32 32 114 114 32 114 72 124 43 45 45 45 45 45 45 45 45 45 45 45 45 45 45 43

Round 2

1

Round 3

1

Round 4

1

Round 5

1

Round 6

1

Round 7

1

Round 8

1

Round 9

1

Round 10

1

Round 11

1

Round 12

1

Round 13

1

Round 14

1

Round 15

1

**coin toss** 5 rounds

Round 1

11 15 32 32 43 45 45 45 45 45 45 45 43 32 32 124 64 32 32 32 32 114 32 124 32 32 43 45 45 45 45 45 45 45 43 32 32 32 32 32 32 94 32 32 32 32 32 32 32 32 32 32 94 32 32 32 32 32 32 43 45 45 45 45 45 45 45 43 32 32 124 32 32 64 118 32 32 32 124 32 32 124 32 32 32 115 32 32 32 124 32 32 124 32 32 32 115 32 32 32 124 32 32 43 45 45 45 45 45 45 45 43 32 32 32 32 32 32 118 32 32 32 32 32 32 32 32 32 32 118 32 32 32 32 32 32 43 45 45 45 45 45 43 32 32 32 32 124 64 114 32 32 32 124 32 32 32 32 43 45 45 45 45 45 43 32 32

Round 2

1

Round 3

1

Round 4

1

Round 5

45

**pileup** 7 rounds

Round 1

16 5 43 45 45 45 45 45 45 43 32 43 45 45 45 45 45 43 124 64 32 32 32 32 94 124 32 124 62 64 118 32 32 124 124 32 32 32 32 32 32 124 32 124 94 32 60 32 32 124 124 32 32 32 32 32 32 124 32 124 32 32 32 32 32 124 43 45 45 45 45 45 45 43 32 43 45 45 45 45 45 43

Round 2

1

Round 3

1

Round 4

1

Round 5

1

Round 6

1

Round 7

47

**long haul** 13 rounds

Round 1

11 10 43 45 45 45 45 45 45 45 45 43 32 124 64 49 115 50 115 51 115 72 124 32 43 45 45 45 45 45 45 45 45 43 32 32 32 32 32 32 118 32 32 32 32 32 32 32 32 32 32 62 45 45 45 45 118 43 45 45 45 45 45 45 43 32 32 124 124 64 114 114 114 118 32 124 32 32 124 124 32 32 32 32 72 32 124 60 45 60 124 32 32 32 32 32 32 124 32 32 32 43 45 45 45 45 45 45 43 32 32 32

Round 2

1

Round 3

2

Round 4

2

Round 5

1

Round 6

1

Round 7

1

Round 8

3

Round 9

4

Round 10

1

Round 11

1

Round 12

2

Round 13

29

**cliffhanger** 4 rounds

Round 1

9 10 43 45 45 45 45 45 45 45 43 124 64 49 43 115 51 115 60 124 124 32 32 32 32 32 32 32 124 43 45 45 45 45 45 45 45 43 32 32 118 32 32 32 32 32 32 32 32 62 45 45 45 45 118 32 32 32 32 32 32 32 32 118 32 43 45 45 45 45 45 45 45 43 124 64 114 32 32 72 32 32 124 43 45 45 45 45 45 45 45 43

Round 2

1

Round 3

8

Round 4

51

**bounce house** 9 rounds

Round 1

14 16 43 45 45 45 45 45 45 45 45 45 45 45 45 43 124 64 49 77 118 32 62 43 43 43 118 32 32 124 124 32 32 32 32 32 32 32 32 32 32 32 32 124 124 32 32 32 62 45 88 60 32 32 118 32 32 124 124 32 32 32 32 32 32 32 32 32 45 32 32 124 124 32 32 32 32 32 32 32 32 32 88 32 72 124 124 32 32 32 32 32 32 32 32 32 94 32 32 124 124 32 32 32 32 32 32 32 32 32 32 32 32 124 43 45 45 45 45 45 45 45 45 45 45 45 45 43 43 45 45 45 45 45 45 45 45 45 45 45 45 43 124 64 45 43 118 32 32 32 32 32 32 32 32 124 124 32 32 32 32 32 32 32 32 32 32 32 32 124 124 32 72 60 32 32 60 32 32 32 32 32 32 124 124 32 32 32 32 32 94 32 32 32 32 32 32 124 124 32 32 32 62 32 94 32 32 32 32 32 32 124 43 45 45 45 45 45 45 45 45 45 45 45 45 43

Round 2

5

Round 3

6

Round 4

6

Round 5

1

Round 6

4

Round 7

7

Round 8

2

Round 9

1

**grand tour** 24 rounds

Round 1

10 12 43 45 45 45 45 45 45 45 45 43 124 64 49 77 54 62 45 115 88 124 124 32 32 32 32 32 32 32 32 124 124 32 32 32 32 94 32 32 60 124 124 32 32 32 32 32 32 32 32 124 43 45 45 45 45 45 45 45 45 43 32 32 32 32 32 32 32 118 32 32 32 32 32 32 32 32 32 62 118 32 43 45 45 45 45 45 45 45 45 43 124 64 62 114 53 88 32 32 32 124 124 32 94 32 32 60 32 32 32 124 43 45 45 45 45 45 45 45 45 43

Round 2

3

Round 3

2

Round 4

1

Round 5

6

Round 6

3

Round 7

1

Round 8

1

Round 9

5

Round 10

2

Round 11

1

Round 12

2

Round 13

3

Round 14

1

Round 15

5

Round 16

2

Round 17

4

Round 18

1

Round 19

7

Round 20

2

Round 21

1

Round 22

1

Round 23

2

Round 24

64

**below zero** 5 rounds

Round 1

10 10 43 45 45 45 45 45 45 45 45 43 124 64 57 77 48 45 115 72 32 124 124 32 32 32 32 32 32 32 32 124 43 45 45 45 45 45 45 45 45 43 32 32 32 32 32 32 118 32 32 32 32 32 32 32 32 32 118 32 32 32 43 45 45 45 45 45 45 45 45 43 124 32 32 32 72 32 32 32 32 124 124 64 32 114 88 32 32 32 32 124 43 45 45 45 45 45 45 45 45 43

Round 2

4

Round 3

2

Round 4

2

Round 5

41

## Submit

Sign in to submit solutions. [Sign in](https://icfpcontest2026.com/login)
