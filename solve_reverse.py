import json, sys
from sim import run

def make_row(spec_dict):
    chars = ['.'] * 39
    chars[0] = '|'
    chars[38] = '|'
    for pos, ch in spec_dict.items():
        chars[pos] = ch
    return "".join(chars)

# Room A (rows 6..12):
# Inside Room A is x=1..37! x=0 and x=38 are '|' walls!
# r12 has 36:'1' so 1 W - M b executes in full!
# r11 has 36:'<' so Phase 2 Output path goes left on row 11 to Round Reset!

r6  = make_row({2:'>', 3:'@', 4:'r', 5:'M', 6:'b', 7:'v', 34:'>', 36:'v'})
r7  = make_row({1:'v', 7:'<', 33:'v', 34:'a', 35:'<', 36:'s', 37:'v'}) # 36:'s' Output Pipe!
r8  = make_row({1:'r', 31:'>', 34:'r', 35:'^', 36:'>', 37:'v'}) # 37:'v' turns Phase 1 finish DOWN col 37!
r9  = make_row({1:'>', 33:'s', 34:'m', 35:'a', 36:'^', 37:'W'}) # 37:'W' start of W b W!
r10 = make_row({1:'^', 31:'^', 33:'<', 34:'^', 36:'v', 37:'b'}) # 37:'b' middle of W b W!
r11 = make_row({2:'^', 31:'^', 36:'<', 37:'W'}) # 36:'<' goes left to Round Reset! 37:'W' end of W b W!
r12 = make_row({2:'^', 31:'^', 32:'b', 33:'M', 34:'-', 35:'W', 36:'1', 37:'d'}) # 36:'1' for 1 W - M b!

room_A = [r6, r7, r8, r9, r10, r11, r12]

# Room B (rows 17..18):
r17_B = make_row({31:'@', 32:'>', 33:'r', 34:'s', 35:'>', 36:'v'})
r18_B = make_row({4:'^', 5:'<', 6:'<', 33:'<', 34:'<'})

grid = [
    "+-+                                 +-+",
    "|I|                                 |O|",
    "+-+                                 +-+",
    " v                                   ^ ",
    " v                                   ^ ",
    "+-------------------------------------+"
] + room_A + [
    "+-------------------------------------+",
    "                                   ^ v ",
    "                                   ^ v ",
    "+-------------------------------------+",
    r17_B,
    r18_B,
    "+-------------------------------------+",
]

man_code = "\n".join(grid)
with open("reverse.man", "w") as f:
    f.write(man_code)

with open("reverse_spec.json") as f:
    spec = json.load(f)

test_cases = spec["publicTestData"]
passed = 0

for t_idx, test_case in enumerate(test_cases, 1):
    name = test_case["name"]
    rounds = test_case["rounds"]
    all_inputs = []
    all_expected = []
    for r in rounds:
        all_inputs.extend([int(x) for x in r["in"]])
        all_expected.extend([int(x) for x in r["out"]])
        
    try:
        out, ticks, w, h = run(man_code, all_inputs, max_ticks=500000)
        if out == all_expected:
            passed += 1
            print(f"PASS: Case {t_idx} '{name}' ({ticks} ticks, {w}x{h})")
        else:
            print(f"FAIL: Case {t_idx} '{name}': got {out}, expected {all_expected}")
    except Exception as e:
        print(f"ERROR: Case {t_idx} '{name}': {e}")

print(f"\nPassed {passed}/{len(test_cases)} public test cases.")
