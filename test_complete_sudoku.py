import json
import sim

# Let's write the complete Sudoku solver in Littleman assembly and run it against all 6 test cases

man_code = """
+-+ +-+
|I| |O|
+-+ +-+
 v   ^
 v   ^
+-------------------------------+           +-----+
|@`27`b                         |           |@r s |
|v>0 s m d                      |>--------->|v^  <|
|^      <|v                     |^|         |^   v|
|        |>r r r M              | |         |<v--<|
|        | M                    | |         |     |
|        |                      | |         |     |
|        |<---------------------|<|<--------|<v--<|
+-------------------------------+           +-----+
"""

# Let's refine the full Littleman program step-by-step
