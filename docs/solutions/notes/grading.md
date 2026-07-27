[\> @ H](https://icfpcontest2026.com/)

[Textbook](https://icfpcontest2026.com/textbook) [Problem Sets](https://icfpcontest2026.com/problem-sets) [Standings](https://icfpcontest2026.com/standings) [Rules](https://icfpcontest2026.com/rules)

Tools & Docs

[Sign in](https://icfpcontest2026.com/login)

**New:** Semester 4 problems and the [split instruction](https://icfpcontest2026.com/split) have been released! See the [problem sets](https://icfpcontest2026.com/problem-sets) page for the new problems.Don't show again ✕

# Grading

**Contents**

1. [Problems Sets](https://icfpcontest2026.com/grading#assignments)
2. [Public & private test cases](https://icfpcontest2026.com/grading#test-cases)
3. [Submitting your work](https://icfpcontest2026.com/grading#submitting)
4. [Program Scoring](https://icfpcontest2026.com/grading#program-scoring)
5. [Ranking, Scoring, and Winning](https://icfpcontest2026.com/grading#grading)
6. [Uber-strict problems](https://icfpcontest2026.com/grading#uber-strict)
7. [Rounds](https://icfpcontest2026.com/grading#round-based)
8. [Display assignments](https://icfpcontest2026.com/grading#displays)
9. [ASCII](https://icfpcontest2026.com/grading#ascii)
10. [Limits](https://icfpcontest2026.com/grading#limits)

## Problems Sets

Teams are ranked by their performance across all _graded_ problem sets on the [problem sets page](https://icfpcontest2026.com/problem-sets). The problems in the "Ungraded Practice Problems" section are not graded and do not count towards your team's performance.

[↑ contents](https://icfpcontest2026.com/grading#top)

## Public & private test cases

Your programs are tested using a problem's test cases. Some test cases are public and some are private. Each test describes output that your program must produce given some (or no) input.

Your program passes a test case as soon as it emits the correct output; it doesn't have to halt.

Submissions are graded against both public and private test cases. Public cases are shown in full in two places: on the problem page, and in the editor's **test cases** tab (on the right edge of the editor). The tab also runs your program against them and [submits your work](https://icfpcontest2026.com/grading#submitting).

Private cases are never shown, but are intended to exercise the same behavior as the public cases - no hidden tricks. They exist to make it difficult to hardcode output for each test case.

[↑ contents](https://icfpcontest2026.com/grading#top)

## Submitting your work

The simplest way to submit a solution is to open the problem in the editor and press **submit program** in the **test cases** tab.

Each problem page also lists other ways to submit (uploading a file, using the API, etc).

Grading is done asynchronously. Your submission may be rejected if your team has many pending submissions (if this happens, wait a bit and try again). Track your team's submissions and their results on the [submissions page](https://icfpcontest2026.com/submissions).

You are graded only on your best submission for each problem. Submitting will never lower your score.

[↑ contents](https://icfpcontest2026.com/grading#top)

## Program Scoring

Each program is given a _score_. A lower score is always better.

The vast majority of problems use **footprint-tick scoring**, which is computed as:

```
max(width, height)² × (average ticks across all test cases)
```

A test case's tick count is the number of ticks until your final correct output value is emitted (for display assignments, until your final frame matches). Your program does not need to halt; ticks after that point are not counted.

A small number of problems use **footprint** scoring - that is, the score does not depend on the speed of the program.

```
max(width, height)²
```

Width and height are defined as the bounding box of your **entire** program.

Each problem page specifies how the problem is scored.

[↑ contents](https://icfpcontest2026.com/grading#top)

## Ranking, Scoring, and Winning

Your team may receive up to _2 points_ for each graded problem. To prevent hardcoding the public test case answers, you are only eligible to score points if you pass at least one private test case. On a problem with no private test cases, passing any test case makes you eligible.

Up to one point is granted based on the fraction of test cases you pass:

```
test-case points = passing test cases / total test cases
```

Up to one additional point is granted based on your ranking against the other eligible teams. First, teams are ranked by the number of test cases they pass. Teams which pass all test cases are additionally ranked by their [program's score](https://icfpcontest2026.com/grading#program-scoring) (lower is better). Ties are allowed. On an [uber-strict](https://icfpcontest2026.com/grading#uber-strict) problem, a full pass ranks above other full passes only if it also passes the uber-strict check.

```
ranking points = (other eligible teams you rank above or tie) / (other eligible teams)
```

If you are the only eligible team, you receive the full ranking point.

Your team's total score is the sum of your highest score on every problem.

[↑ contents](https://icfpcontest2026.com/grading#top)

## Uber-strict problems

Some problems have private test cases simple enough that a determined team could potentially reverse-engineer them to create a program that hardcodes the answers instead of implementing the intended algorithm.

These problems are marked as **uber-strict** and have an additional corpus of test cases that are run against programs that pass all public and private test cases. You are only told whether you passed the uber-strict corpus, not how many tests there are or how many you passed.

Tests in the uber-strict corpus are straightforward - they exercise the same functionality as the public and private test cases.

The uber-strict test corpus is _not_ used to compute tick counts for scoring purposes; it is a pass-fail check only. A submission that passes all public and private test cases but fails the uber-strict corpus is ranked below every submission that passes the uber-strict corpus.

[↑ contents](https://icfpcontest2026.com/grading#top)

## Rounds

A test case contains one or more **rounds**. A round is an input/expected-output pair. All rounds run against a single run of your program (there is no reset between rounds).

The input for round `N+1` is not available until all output for round `N` has been received.

Some rounds expect no output; the input for the following round is then unlocked immediately.

In the editor, `/` separates rounds in the input and expected output boxes. For example `1 42 / 2 41 42` represents two rounds.

[↑ contents](https://icfpcontest2026.com/grading#top)

## Display assignments

Some assignments are judged on the [LM-75 display](https://icfpcontest2026.com/textbook#the-display) instead of on your program's output. The problem page will tell you this, and will show you pictures for expected output instead of text.

Judging is still a streaming compare; every frame your display commits (each SWAP, routed through the bottom of the display) must equal the next expected frame in order.

Your program must contain exactly one display at the resolution that the assignment states. It is an error to emit any output in a display-judged program.

Display problems may be [round based](https://icfpcontest2026.com/grading#round-based); if they are, frames gate the next round of input exactly like regular output does.

[↑ contents](https://icfpcontest2026.com/grading#top)

## ASCII

Some problems may ask you to read or write _ASCII_. ASCII is a mapping from an integer between 0 and 127 to a character. For example, since `104` is the ASCII-encoding of `h` and `105` is the ASCII-encoding of `i`, `hi` would be encoded in ASCII as `104 105`.

All values in Littleman are ultimately decimal integers, and that is still true when working with ASCII - the letter "h" is transmitted as `104`.

To make working with ASCII easier, the editor automatically enables ASCII-mode when working on ASCII problems. ASCII mode decodes numbers into characters in test cases automatically. This can be disabled using the program menu in the top bar.

For your reference, a full ASCII table is [available here](https://icfpcontest2026.com/ascii.txt).

[↑ contents](https://icfpcontest2026.com/grading#top)

## Limits

Programs are limited to **10 MB**.

Every program is run with a step-count limit. Hitting the step limit ends your program. For most problems the limit is **5 million steps**. A few problems may have smaller or larger limits - this will be mentioned on the problem page.

Our internal grading infrastructure has a few more internal limits (e.g. on the amount of time spent executing a program). Most well-behaved programs should never see these limits. Feel free to reach out if you hit one of these limits and think something is wrong.

[↑ contents](https://icfpcontest2026.com/grading#top)

\> @ <
