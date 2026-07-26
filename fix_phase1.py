import sys
from sim import run

# Let us build a clean, exact reverse.man program where:
# Phase 1:
# - Read n from Input Pipe into A
# - M (B=n), b (BP=n)
# - Loop n times:
#     - Read x_i from Input Pipe (near top-left)
#     - Send x_i to Pipe A->B (near bottom-right)
#     - m (BP -= 1)
#     - d (if BP > 0, loop back to read next x_i; if BP == 0, proceed to Phase 2)

# Phase 2:
# Outer loop (k = B):
# - W M 1 W - M b (set BP = k-1, B = k-1)
# - Inner rotation loop (BP times):
#     - d (if BP > 0, read from Ring B->A, send to Ring A->B, m, loop)
#     - if BP == 0, proceed to Output
# - Output step:
#     - Read target item from Ring B->A
#     - Send to Output Pipe (near top-right)
# - Outer termination check:
#     - W (A = B = k-1)
#     - X (if A > 0, loop back to Outer loop; if A == 0, loop back to Phase 1 for next round!)

man_code = """+-+                                 +-+
|I|                                 |O|
+-+                                 +-+
 v                                   ^
 v                                   ^
+-------------------------------------+
|@rMb>............................sWXv|
|....v............................^.v|
|....r............................^.v|
|....s............................^.v|
|....m............................^.v|
|....v............................^.v|
|....<d..W1MW-Mb<d......<r<s......m<s|
+-------------------------------------+
     ^                           v
     ^                           v
+-------------------------------------+
|@rs>v................................|
|^<<v.................................|
+-------------------------------------+
"""

