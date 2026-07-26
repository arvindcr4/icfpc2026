import sim

man_code = """
+-+ +-+
|I| |O|
+-+ +-+
 v   ^
 v   ^
+---------------------------------------+           +-----+
|@`27`b v                               |           |@r s |
|>0 s m d v                             |>--------->|v^  <|
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
with open('sudoku.man', 'w') as f:
    f.write(man_code + '\n')

import build_and_verify_sudoku
build_and_verify_sudoku.test_all()
