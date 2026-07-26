import json
import sim

# Let's test the complete Sudoku solver in sim.py to verify 100% correctness on all 6 public test cases!

man_code = """
+-+ +-+
|I| |O|
+-+ +-+
 v   ^
 v   ^
+---------------------------------------+           +-----+
|@`27`b v                               |           |@r s |
|>0 s m d                               |>--------->|v^  <|
|^      <|v                             |^|         |^   v|
|        |>r M r M r W `1` W { M        |<---------<|<v--<|
|        | M W `9` + M W                |           +-----+
|        | M `3` / * M W `3` / + `18` + |
|        | M                            |
|        |                              |
|        |                              |
|        |                              |
|        |                              |
+---------------------------------------+
"""

# Let's write a python test script that loads spec_sudoku.json and runs sim.py
