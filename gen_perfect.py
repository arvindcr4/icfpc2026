import sys
from sim import run
import json

# Let us construct the full .man grid cleanly with precise pipe glyphs
grid = [
    "+-+                                 +-+",
    "|I|                                 |O|",
    "+-+                                 +-+",
    " v                                   ^ ",
    " v                                   ^ ",
    "+-------------------------------------+",
    "|@rMb>............................sWXv|",
    "|....v............................^..v|",
    "|....r............................^..v|",
    "|....s............................^..v|",
    "|....m............................^..v|",
    "|....v............................^..v|",
    "|....<d..W1MW-Mb<d......<r<s......m<<s|",
    "+-------------------------------------+",
    "     ^                             v   ",
    "     ^                             v   ",
    "+-------------------------------------+",
    "|@rs>v................................|",
    "|^<<<v................................|",
    "+-------------------------------------+"
]

# Let us check and fix pipes in grid
man_code = "\n".join(grid)

with open("reverse.man", "w") as f:
    f.write(man_code)

with open("reverse_spec.json") as f:
    spec = json.load(f)

test_cases = spec["publicTestData"]
for t_idx, test_case in enumerate(test_cases, 1):
    name = test_case["name"]
    rounds = test_case["rounds"]
    all_inputs = []
    all_expected = []
    for r in rounds:
        all_inputs.extend([int(x) for x in r["in"]])
        all_expected.extend([int(x) for x in r["out"]])
        
    try:
        out, ticks, w, h = run(man_code, all_inputs, max_ticks=100000)
        print(f"Case {t_idx} '{name}': out={out}, expected={all_expected}, ticks={ticks}")
    except Exception as e:
        print(f"Case {t_idx} '{name}': ERROR {e}")
