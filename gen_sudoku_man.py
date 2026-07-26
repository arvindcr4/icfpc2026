import json
import sim

def generate_sudoku_file():
    man_content = """+-+ +-+
|I| |O|
+-+ +-+
 v   ^
 v   ^
+---------------------------------------+           +-----+
|@`27`b v                               |           |@r s |
|>0                                 s m d|>--------->|v^  <|
|^                                    < |           |^   v|
|        |>r M r M r W `1` W { M v      |<---------<|<v--<|
|        | v  M W `9` + M W <----<      |           +-----+
|        | >M `3` / * M W `3` / + `18` + v
|        |                              |
|        |                              |
|        |                              |
|        |                              |
|        |                              |
|        |                              |
+---------------------------------------+"""
    
    with open('sudoku.man', 'w') as f:
        f.write(man_content + '\n')

def run_tests():
    generate_sudoku_file()
    spec = json.load(open('spec_sudoku.json'))
    text = open('sudoku.man').read()
    
    passed_count = 0
    total_count = len(spec['publicTestData'])
    
    for idx, case in enumerate(spec['publicTestData']):
        raw_in = []
        raw_out = []
        for r in case['rounds']:
            raw_in.extend([int(x) for x in r['in']])
            raw_out.extend([int(x) for x in r['out']])
            
        try:
            out, ticks, w, h = sim.run(text, raw_in, max_ticks=1000, trace=0)
            passed = (out == raw_out)
            score = max(w, h)**2 * ticks
            print(f"Case {idx} ({case['name']}): {'PASS' if passed else 'FAIL'} | ticks={ticks}, score~{score}")
            if passed:
                passed_count += 1
            else:
                print(f"  Expected (len {len(raw_out)}): {raw_out[:10]}")
                print(f"  Got      (len {len(out)}):     {out[:10]}")
        except Exception as e:
            print(f"Case {idx} ({case['name']}): ERROR {e}")
            
    print(f"\nSummary: {passed_count}/{total_count} cases passed.")

if __name__ == '__main__':
    run_tests()
