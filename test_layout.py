import sys
from sim import run

def test_program(man_code, verbose=False):
    test_cases = [
        ("1 42", [42]),
        ("2 100 -100", [-100, 100]),
        ("3 10 20 30", [30, 20, 10]),
        ("7 8 6 7 5 3 0 9", [9, 0, 3, 5, 7, 6, 8]),
        ("5 1 2 3 4 5", [5, 4, 3, 2, 1]),
        ("4 -7 0 7 -14", [-14, 7, 0, -7]),
        ("5 4 4 4 4 4", [4, 4, 4, 4, 4]),
        ("5 1 2 3 2 1", [1, 2, 3, 2, 1]),
        ("2 1000000 -1000000", [-1000000, 1000000]),
        ("16 675866 -469990 -316526 -586202 -495649 -594977 725024 970614 -758697 -386951 -1260 998677 169990 282058 -501276 -694925",
         [-694925, -501276, 282058, 169990, 998677, -1260, -386951, -758697, 970614, 725024, -594977, -495649, -586202, -316526, -469990, 675866])
    ]
    passed = 0
    for inp_str, expected in test_cases:
        inputs = [int(x) for x in inp_str.split()]
        try:
            out, ticks, w, h = run(man_code, inputs, max_ticks=200000, trace=0)
            if out == expected:
                passed += 1
                if verbose:
                    print(f"  PASS: {inp_str[:25]}... -> {ticks} ticks (grid {w}x{h})")
            else:
                print(f"  FAIL: {inp_str[:25]}...")
                print(f"    Got:      {out}")
                print(f"    Expected: {expected}")
        except Exception as e:
            print(f"  ERROR on {inp_str[:25]}: {e}")
    print(f"Passed {passed}/{len(test_cases)} cases")
    return passed == len(test_cases)
