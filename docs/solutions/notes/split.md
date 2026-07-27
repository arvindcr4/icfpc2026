[\> @ H](https://icfpcontest2026.com/)

[Textbook](https://icfpcontest2026.com/textbook) [Problem Sets](https://icfpcontest2026.com/problem-sets) [Standings](https://icfpcontest2026.com/standings) [Rules](https://icfpcontest2026.com/rules)

Tools & Docs

[Sign in](https://icfpcontest2026.com/login)

**New:** Semester 4 problems and the [split instruction](https://icfpcontest2026.com/split) have been released! See the [problem sets](https://icfpcontest2026.com/problem-sets) page for the new problems.Don't show again ✕

# Split

_The little man grabs his fork, eats a big meal, and splits in two. Split (Y) is a powerful new instruction that you may now use in your programs._

3/sback (b)next (n)play (p)run (⌃↵)

## Y, precisely

- `Y` splits the little man in two. The copies are born on the cells to his left and his right — left and right relative to his heading as he enters the `Y` — each heading away from the `Y`. The original man does not continue past the `Y`; only the two copies remain.
- Both copies carry the original little man's registers, including his backpack.
- The tick after they were born, the copies execute the instruction they were born on and then move.
- Little men act in creation order, every tick. On a split, the copy born to the **right** takes over the splitting man's place in that order; the copy born to the **left** becomes the newest little man and acts after all others.
- **Y is unconditional**. It is executed even if a birth cell is blocked by another man or a wall.
- If the birth cell is a wall, the program halts with an error.
- If the birth cell is another little man (including a little man blocked on an instruction), both little men die. This is _not_ an error.
- If two little men in the same room collide, they both die. This is not an error. This includes two men arriving on the same cell in the same tick, and two adjacent men moving through each other (swapping cells) in the same tick.
- If two little men are spawned on the same cell by two split instructions they both die. This is not an error.
- The maximum number of live little men is 65536. Exceeding this limit is an error and ends your program.

\> @ <
