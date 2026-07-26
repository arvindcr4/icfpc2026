import sys
sys.path.append('/home/claude/icfpc2026')
import sim, json

prog_text = '''
+-+ +-+
|I| |O|
+-+ +-+
 v   ^
 v   ^
+------------------------+         +-------+
|@r                      |>>>>>>>>>|r s   v|
|                        |<<<<<<<<<|^ < < <|
+------------------------+         +-------+
'''
print("Testing layout construction...")
