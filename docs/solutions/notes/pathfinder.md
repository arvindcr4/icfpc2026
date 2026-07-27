PROBLEM ID: c778ba35-4918-415b-83d0-37dc8f6f68c9

---
title: "ICFP Programming Contest 2026"
description: "The 29th ICFP Programming Contest runs July 24–27, 2026. An online programming competition for teams of any size, anywhere."
url: "https://icfpcontest2026.com/"
publisher: "ICFP Programming Contest 2026"
lang: "en"
date: "2026-07-27T02:39:04.000Z"
word_count: 3118
reading_time: "12 min read"
---

## Table of Contents

- [Rounds](#rounds)
  - [Output](#output)
- [Format](#format)
- [Constraints](#constraints)
- [Examples](#examples)
- [Submit](#submit)

---

[← Problem Sets](https://icfpcontest2026.com/problem-sets)

Semester 4

[Solve in editor →](https://icfpcontest2026.com/problems/pathfinder/editor)

**Scoring: footprint-tick.** **Tick cap: 15,000,000 per test case.** See [scoring](https://icfpcontest2026.com/grading#program-scoring), [rounds](https://icfpcontest2026.com/grading#round-based), and [displays](https://icfpcontest2026.com/grading#displays) for help.

Guide a robot through a maze to find a flag and draw the robot's path on a display.

This problem takes place on a 16x16 board. The board's top-left corner is `0,0`. Every cell on the board is either a `wall` or a `path`. `path` cells are traversable, `wall` cells are not.

### Rounds

The first [round](https://icfpcontest2026.com/grading#round-based) is a *setup round*. It supplies the board's state and the robot's starting position. The board is supplied as 256 values in row-major order (row 0, then row 1, etc). A `0` represents a path and a `1` represents a wall. Every cell on the board's border is always a wall. The robot's position `rx ry` is an x,y coordinate pair that is always on a path.

Each subsequent round is a *pathfinding round*. It supplies a flag `fx fy`. The flag is on a path and is reachable from (and different to) the robot's current position. The robot's starting position at pathfinding round `N` is equivalent to its ending position at round `N-1`.

### Output

To complete the setup round, commit **one** frame to your [display](https://icfpcontest2026.com/grading#displays) showing the walls, paths, and robot.

To complete a pathfinding round, commit **one frame after each move** — `k` frames in total, where `k` is the length of the shortest path from the robot to the flag. The robot may not move through walls.

**If multiple paths are tied for shortest** the robot should prefer moving up (`y-1`), then right (`x+1`), then down (`y+1`), then left (`x-1`).

**To draw the state of the board** draw paths in color 0, walls in color 7, the flag in color 9, and the robot in color 10. The flag is not drawn on the last frame of each round because the robot is on top of it.

## Format

**Input.** A run of integers, until it ends.

the first round is the 16×16 board (256 cells, row-major, 1 = wall) plus the robot's starting position rx ry; every later round is one flag fx fy

```
input ⟶ int*

e.g.
  round 1:  1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 0 0 0 0 0 0 0 0 0 1 0 0 0 0 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 1 0 0 0 1 0 0 0 0 0 0 0 0 0 0 1 1 0 0 0 0 0 0 0 0 0 0 0 0 1 0 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 1 0 0 0 0 0 0 0 0 1 0 0 0 0 1 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 1 0 1 0 0 1 0 0 0 0 0 0 0 1 0 1 1 0 0 0 0 1 0 0 0 0 0 0 0 0 0 1 1 0 0 0 0 0 0 1 0 0 0 0 0 0 0 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 7 5
```

**Output.** Your program must contain exactly one **16×16 display**; your solution must commit the expected frames for each round in order — they're pictured in the examples. [How display judging works →](https://icfpcontest2026.com/grading#displays)

## Constraints

- `0 ≤ x < 16`, `0 ≤ y < 16`
- the shortest path to each flag is at most 64 moves

## Examples

**a straight shot** Round 1

in: 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 0 0 0 0 0 0 0 0 0 1 0 0 0 0 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 1 0 0 0 1 0 0 0 0 0 0 0 0 0 0 1 1 0 0 0 0 0 0 0 0 0 0 0 0 1 0 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 1 0 0 0 0 0 0 0 0 1 0 0 0 0 1 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 1 0 1 0 0 1 0 0 0 0 0 0 0 1 0 1 1 0 0 0 0 1 0 0 0 0 0 0 0 0 0 1 1 0 0 0 0 0 0 1 0 0 0 0 0 0 0 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 7 5

screen:

Round 2

in: 13 8

screen:

1

2

3

4

5

6

7

8

9

Round 3

in: 4 5

screen:

1

2

3

4

5

6

7

8

9

10

11

12

Round 4

in: 5 5

screen:

**around the pillars** Round 1

in: 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 1 0 1 0 0 1 0 0 1 0 0 1 0 0 0 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 1 0 1 0 0 1 0 0 1 0 0 1 0 0 0 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 1 0 1 0 0 1 0 0 1 0 0 1 0 0 0 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 1 0 1 0 0 1 0 0 1 0 0 1 0 0 0 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 2 4

screen:

Round 2

in: 8 1

screen:

1

2

3

4

5

6

7

8

9

Round 3

in: 13 6

screen:

1

2

3

4

5

6

7

8

9

10

Round 4

in: 4 14

screen:

1

2

3

4

5

6

7

8

9

10

11

12

13

14

15

16

17

**the long way** Round 1

in: 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 0 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 1 0 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 0 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 1 0 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 0 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 1 0 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 7 13

screen:

Round 2

in: 12 7

screen:

1

2

3

4

5

6

7

8

9

10

11

12

13

14

15

16

17

18

19

20

21

22

23

24

25

26

27

28

29

30

31

32

33

34

35

36

37

38

39

40

41

42

43

44

45

46

47

48

49

Round 3

in: 2 11

screen:

1

2

3

4

5

6

7

8

9

10

11

12

13

14

15

16

17

18

19

20

21

22

23

24

25

26

27

28

29

30

31

32

33

34

35

36

37

38

39

40

**rooms and doors** Round 1

in: 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 0 0 0 0 0 0 0 0 1 0 0 0 0 0 1 1 0 0 0 0 0 0 0 0 1 0 0 0 0 0 1 1 0 0 0 0 0 0 0 0 1 0 0 0 0 0 1 1 0 0 0 0 0 0 0 0 0 1 1 0 1 1 1 1 0 0 0 0 0 0 0 0 1 0 0 0 0 0 1 1 1 1 1 1 0 1 1 1 1 0 0 0 0 0 1 1 0 0 0 0 0 0 0 0 1 0 0 0 0 0 1 1 0 0 0 0 0 0 0 0 1 1 0 1 1 1 1 1 0 0 0 0 0 0 0 0 1 0 0 0 0 0 1 1 0 0 0 0 0 0 0 0 1 0 0 0 0 0 1 1 0 0 0 0 0 0 0 0 1 0 0 0 0 0 1 1 1 1 0 1 1 1 1 1 1 1 0 1 1 1 1 1 0 0 0 0 0 0 0 0 1 0 0 0 0 0 1 1 0 0 0 0 0 0 0 0 1 0 0 0 0 0 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 12 3

screen:

Round 2

in: 14 9

screen:

1

2

3

4

5

6

7

8

9

10

Round 3

in: 10 3

screen:

1

2

3

4

5

6

7

8

9

10

11

12

Round 4

in: 14 14

screen:

1

2

3

4

5

6

7

8

9

10

11

12

13

14

15

16

17

Round 5

in: 10 3

screen:

1

2

3

4

5

6

7

8

9

10

11

12

13

14

15

16

17

**a cluttered field** Round 1

in: 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 0 0 1 0 0 0 0 0 0 0 0 0 0 0 1 1 1 0 0 0 0 0 0 0 1 0 0 0 1 1 1 1 0 0 0 1 1 0 1 0 0 0 1 0 1 1 1 1 0 0 0 0 0 1 0 0 0 0 1 0 1 1 1 1 1 1 0 0 0 0 1 1 1 0 0 1 1 0 1 1 1 0 0 0 0 0 1 1 1 0 0 0 0 0 1 1 0 0 0 0 0 1 0 0 0 0 0 1 0 0 1 1 0 0 0 0 0 0 0 0 0 1 1 1 1 1 1 1 0 0 0 1 1 0 0 0 0 0 0 1 0 0 1 1 1 1 0 0 1 0 0 0 0 0 0 0 0 0 1 1 0 0 1 1 1 1 1 0 1 1 0 1 0 0 1 1 0 0 0 0 0 0 0 0 0 1 0 0 0 1 1 1 0 1 0 1 0 1 0 0 0 0 0 0 0 0 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 11 2

screen:

Round 2

in: 10 9

screen:

1

2

3

4

5

6

7

8

9

10

Round 3

in: 1 12

screen:

1

2

3

4

5

6

7

8

9

10

11

12

Round 4

in: 11 9

screen:

1

2

3

4

5

6

7

8

9

10

11

12

13

Round 5

in: 7 14

screen:

1

2

3

4

5

6

7

8

9

**running errands** Round 1

in: 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 0 0 0 0 0 0 0 1 0 0 0 0 0 0 1 1 0 0 0 0 0 0 0 1 0 0 0 0 0 0 1 1 1 1 1 1 1 0 1 0 0 0 0 0 0 0 1 1 0 0 0 0 0 0 0 1 1 1 1 0 1 1 1 1 0 0 0 0 0 0 0 1 0 0 0 0 0 0 1 1 0 0 0 0 0 0 0 1 0 0 0 0 0 0 1 1 0 0 0 0 0 0 0 1 0 0 0 0 0 0 1 1 0 0 0 0 0 0 0 1 0 0 0 0 0 0 1 1 0 0 0 0 0 0 0 1 0 0 0 0 0 0 1 1 1 1 1 1 0 1 1 1 1 1 1 1 0 1 1 1 0 0 0 0 0 0 0 1 0 0 0 0 0 0 1 1 0 0 0 0 0 0 0 1 0 0 0 0 0 0 1 1 0 0 0 0 0 0 0 1 0 0 0 0 0 0 1 1 0 0 0 0 0 0 0 1 0 0 0 0 0 0 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 10 13

screen:

Round 2

in: 12 7

screen:

1

2

3

4

5

6

7

8

9

10

Round 3

in: 9 1

screen:

1

2

3

4

5

6

7

8

9

Round 4

in: 9 8

screen:

1

2

3

4

5

6

7

8

9

10

11

12

13

Round 5

in: 14 11

screen:

1

2

3

4

5

6

7

8

Round 6

in: 11 7

screen:

1

2

3

4

5

6

7

Round 7

in: 8 3

screen:

1

2

3

4

5

6

7

8

9

**there and back again** Round 1

in: 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 0 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 1 0 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 0 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 1 0 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 0 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 1 0 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 2 11

screen:

Round 2

in: 7 7

screen:

1

2

3

4

5

6

7

8

9

10

11

12

13

14

15

16

17

18

19

20

21

22

23

24

25

26

27

28

29

30

31

32

33

34

35

Round 3

in: 11 1

screen:

1

2

3

4

5

6

7

8

9

10

11

12

13

14

15

16

17

18

19

20

21

22

23

24

25

26

27

28

29

30

31

32

33

34

35

36

37

38

39

40

41

42

## Submit

Sign in to submit solutions. [Sign in](https://icfpcontest2026.com/login)
