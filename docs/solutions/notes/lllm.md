PROBLEM ID IS d91edb43-4e94-4541-b8f7-9c79ba8c8331

---
title: "ICFP Programming Contest 2026"
description: "The 29th ICFP Programming Contest runs July 24–27, 2026. An online programming competition for teams of any size, anywhere."
url: "https://icfpcontest2026.com/"
publisher: "ICFP Programming Contest 2026"
lang: "en"
date: "2026-07-27T02:42:38.000Z"
word_count: 2159
reading_time: "9 min read"
---

## Table of Contents

- [The LLLM Language](#the-lllm-language)
- [Drawing](#drawing)
- [Input and output](#input-and-output)
- [Format](#format)
- [Constraints](#constraints)
- [Examples](#examples)
- [Submit](#submit)

---

[← Problem Sets](https://icfpcontest2026.com/problem-sets)

Semester 4

[Solve in editor →](https://icfpcontest2026.com/problems/little-little-little-man/editor)

**Scoring: footprint-tick.** **Tick cap: 15,000,000 per test case.** See [scoring](https://icfpcontest2026.com/grading#program-scoring), [rounds](https://icfpcontest2026.com/grading#round-based), and [displays](https://icfpcontest2026.com/grading#displays) for help.

Interpret an LLLM program and show its state on a display.

## The LLLM Language

Little little littleman (LLLM) is a simple subset of the [little littleman (LLM)](https://icfpcontest2026.com/problems/little-little-man) language, which is a simple subset of the language that you have learned during the course. *All valid LLLM programs are valid LLM programs, which are valid littleman programs*. This problem will not recap the basics of littleman programs; consult the [textbook](https://icfpcontest2026.com/textbook), [language reference](https://icfpcontest2026.com/language-reference), and [editor](https://icfpcontest2026.com/editor) if you're confused.

LLLM programs run in a single room and have a single `@` designating the little man's starting position. The `@` moves with the man: the cell where he started is ordinary empty space, and walking back over it does nothing.

The full set of operations in the LLLM language is:

- `^` `>` `v` `<` — set heading to N / E / S / W
- `0` – `9` — `A = n`
- `M` — `B = A`
- `+` — `A = A + B`
- `-` — `A = A - B`
- `X` — turn clockwise if `A > 0`, counterclockwise if `A < 0`, don't turn if `A = 0`
- `H` — halt: the man stays on the `H` forever

On each tick the little man executes the operation he is standing on (if applicable) and *then* advances in his current direction. The little man halts if he hits a wall: he stays put on the wall cell forever, and frames committed after that show him drawn on the wall cell. (This differs from littleman, where hitting a wall is an error.)

**The programs you receive will be well-formed:** every program will have a single room with a single `@` inside. Other characters will either be spaces or valid operations.

## Drawing

Draw the LLLM program with its top-left corner at the top-left corner of your [display](https://icfpcontest2026.com/grading#displays). Your display will be 16x16; if your LLLM program is smaller than that leave the pixels outside of the program black.

You should use color `9` (bright red) to represent the current position of the little man. When the little man is on top of an instruction or a wall, draw *him*, not the thing he is on top of.

Other cells have fixed colors similar to what you see in the editor:

- room walls — 4 (blue)
- `<` `>` `^` `v` `X` `H` — 3 (yellow)
- `0` – `9` — 8 (gray)
- `M` — 12 (bright blue)
- `+` `-` — 10 (bright green)
- space — 0 (black)

## Input and output

The first [round](https://icfpcontest2026.com/grading#round-based) supplies two integers `W H` and then `W*H` [ASCII](https://icfpcontest2026.com/grading#ascii) values that comprise a valid LLLM program, in row-major order (top row first, left to right). Commit a single frame showing the starting state.

Subsequent rounds supply one integer `k`. Step the program forward `k` ticks or until it halts, whichever comes first. Then commit a single frame showing the state of the program.

Test cases end after the round where the LLLM program halts.

## Format

**Input.** A run of integers, until it ends.

the first round is the LLLM program: W H, then W·H ASCII codes (row-major); every later round is one step command k

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
- at most 30 rounds and at most 200 ticks per test case
- no step commands arrive after the program halts

## Examples

**one tick at a time** 26 rounds

Round 1

11 7 43 45 45 45 45 45 45 45 45 45 43 124 32 32 32 32 32 32 32 32 32 124 124 64 49 77 51 62 45 88 32 72 124 124 32 32 32 32 32 32 32 32 32 124 124 32 32 32 32 94 32 60 32 32 124 124 32 32 32 32 32 32 32 32 32 124 43 45 45 45 45 45 45 45 45 45 43

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

Round 16

1

Round 17

1

Round 18

1

Round 19

1

Round 20

1

Round 21

1

Round 22

1

Round 23

1

Round 24

1

Round 25

1

Round 26

1

**first steps** 4 rounds

Round 1

4 4 43 45 45 43 124 64 118 124 124 32 72 124 43 45 45 43

Round 2

1

Round 3

1

Round 4

1

**around the block** 12 rounds

Round 1

16 16 43 45 45 45 45 45 45 45 45 45 45 45 45 45 45 43 124 32 32 32 32 32 32 32 32 32 32 32 32 32 32 124 124 64 49 77 57 62 45 32 32 88 32 32 72 32 32 124 124 32 32 32 32 32 32 32 32 32 32 32 32 32 32 124 124 32 32 32 32 32 32 32 32 32 32 32 32 32 32 124 124 32 32 32 32 94 32 32 32 60 32 32 32 32 32 124 124 32 32 32 32 32 32 32 32 32 32 32 32 32 32 124 124 32 32 32 32 32 32 32 32 32 32 32 32 32 32 124 124 32 32 32 32 32 32 32 32 32 32 32 32 32 32 124 124 32 32 32 32 32 32 32 32 32 32 32 32 32 32 124 124 32 32 32 32 32 32 32 32 32 32 32 32 32 32 124 124 32 32 32 32 32 32 32 32 32 32 32 32 32 32 124 124 32 32 32 32 32 32 32 32 32 32 32 32 32 32 124 124 32 32 32 32 32 32 32 32 32 32 32 32 32 32 124 124 32 32 32 32 32 32 32 32 32 32 32 32 32 32 124 43 45 45 45 45 45 45 45 45 45 45 45 45 45 45 43

Round 2

17

Round 3

18

Round 4

2

Round 5

5

Round 6

6

Round 7

6

Round 8

28

Round 9

22

Round 10

4

Round 11

10

Round 12

24

**off the edge** 15 rounds

Round 1

16 5 43 45 45 45 45 45 45 45 45 45 45 45 45 45 45 43 124 64 32 32 32 62 32 32 32 32 32 32 32 118 32 124 124 32 32 32 32 32 32 32 32 32 32 32 32 32 32 124 124 32 94 32 32 32 32 32 60 32 32 32 32 60 32 124 43 45 45 45 45 45 45 45 45 45 45 45 45 45 45 43

Round 2

3

Round 3

5

Round 4

1

Round 5

1

Round 6

3

Round 7

2

Round 8

1

Round 9

2

Round 10

1

Round 11

2

Round 12

1

Round 13

1

Round 14

2

Round 15

3

**widdershins** 10 rounds

Round 1

7 16 43 45 45 45 45 45 43 124 64 49 77 48 118 124 124 32 32 32 32 45 124 124 32 32 32 32 45 124 124 32 32 32 32 45 124 124 32 88 32 43 60 124 124 32 32 32 32 32 124 124 32 32 32 32 32 124 124 32 32 32 32 32 124 124 32 118 32 32 94 124 124 32 32 32 32 32 124 124 32 32 32 32 32 124 124 32 32 32 32 32 124 124 32 62 32 32 94 124 124 32 32 32 32 32 124 43 45 45 45 45 45 43

Round 2

3

Round 3

7

Round 4

5

Round 5

7

Round 6

8

Round 7

5

Round 8

4

Round 9

3

Round 10

28

**crossroads** 3 rounds

Round 1

13 9 43 45 45 45 45 45 45 45 45 45 45 45 43 124 32 32 32 32 32 32 32 32 32 32 32 124 124 32 32 32 32 32 32 32 32 32 32 32 124 124 64 32 32 32 50 88 32 32 32 32 32 124 124 32 32 32 32 32 32 32 32 32 32 32 124 124 32 62 32 32 32 32 32 32 48 88 72 124 124 32 32 32 32 32 32 32 32 32 32 32 124 124 32 94 32 32 32 60 32 32 32 32 32 124 43 45 45 45 45 45 45 45 45 45 45 45 43

Round 2

3

Round 3

41

**revolving door** 6 rounds

Round 1

5 5 43 45 45 45 43 124 64 32 118 124 124 32 32 32 124 124 94 32 60 124 43 45 45 45 43

Round 2

1

Round 3

2

Round 4

1

Round 5

3

Round 6

2

**swan dive** 9 rounds

Round 1

10 5 43 45 45 45 45 45 45 45 45 43 124 64 56 45 43 50 77 88 32 124 124 32 32 32 32 32 32 32 32 124 124 32 32 32 32 32 32 32 32 124 43 45 45 45 45 45 45 45 45 43

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

3

**hall of mirrors** 26 rounds

Round 1

14 10 43 45 45 45 45 45 45 45 45 45 45 45 45 43 124 32 32 32 32 32 32 32 32 32 32 32 32 124 124 64 49 77 118 32 62 43 43 43 118 32 32 124 124 32 32 32 32 32 32 32 32 32 32 32 32 124 124 32 32 32 62 45 88 60 32 32 118 32 32 124 124 32 32 32 32 32 32 32 32 32 45 32 32 124 124 32 32 32 32 32 32 32 32 32 88 32 72 124 124 32 32 32 32 32 32 32 32 32 94 32 32 124 124 32 32 32 32 32 32 32 32 32 32 32 32 124 43 45 45 45 45 45 45 45 45 45 45 45 45 43

Round 2

1

Round 3

1

Round 4

1

Round 5

1

Round 6

2

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

2

Round 13

1

Round 14

2

Round 15

1

Round 16

1

Round 17

1

Round 18

1

Round 19

1

Round 20

1

Round 21

2

Round 22

1

Round 23

2

Round 24

3

Round 25

1

Round 26

1

**victory lap** 5 rounds

Round 1

16 10 43 45 45 45 45 45 45 45 45 45 45 45 45 45 45 43 124 32 32 32 32 32 32 32 32 32 32 32 32 32 32 124 124 64 49 77 55 62 45 32 32 32 32 32 32 88 32 124 124 32 32 32 32 32 32 32 32 32 32 32 32 32 32 124 124 32 32 32 32 32 32 32 32 32 32 32 32 32 32 124 124 32 32 32 32 32 32 32 32 32 32 32 32 32 32 124 124 32 32 32 32 32 32 32 32 32 32 32 32 32 32 124 124 32 32 32 32 32 32 32 32 32 32 32 32 32 32 124 124 32 32 32 32 94 32 32 32 32 32 32 32 60 32 124 43 45 45 45 45 45 45 45 45 45 45 45 45 45 45 43

Round 2

64

Round 3

64

Round 4

30

Round 5

64

## Submit

Sign in to submit solutions. [Sign in](https://icfpcontest2026.com/login)
