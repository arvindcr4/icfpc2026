import json

def test_formulas():
    spec = json.load(open('spec_sudoku.json'))
    for idx, case in enumerate(spec['publicTestData']):
        for r_item in case['rounds']:
            r = int(r_item['in'][0])
            c = int(r_item['in'][1])
            v = int(r_item['in'][2])
            
            b = (r // 3) * 3 + (c // 3)
            
            k1 = r
            k2 = 8 + c - r
            k3 = 8 + b - c
            k4 = 8 - b
            
            assert k1 >= 0
            assert k2 >= 0
            assert k3 >= 0
            assert k4 >= 0
            assert k1 + 1 + k2 + 1 + k3 + 1 + k4 == 27
            
    print("All formula assertions passed 100%!")

test_formulas()
