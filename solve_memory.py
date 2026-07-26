#!/usr/bin/env python3
import json
import sys
import sim

def create_memory_man():
    # Complete memory.man ASCII grid with working Memory Room helper man
    lines = [
        "+-+   +-+",
        "|I|   |O|",
        "+-+   +-+",
        " v     ^ ",
        " v     ^ ",
        "+--------------------------------------------------+     +------+",
        "|@9M1+M*bv                                         |>>>>>|>r  v |",
        "|        v                                         |<<<<<|^ s < |",
        "|        v                                         |     |      |",
        "|        v                                         |     |      |",
        "|        >>>>>>>>>>>>>>>>>>>>>>>>>>0smdv           |     |      |",
        "|                                 .    v           |     |      |",
        "|                                 ^<<<<            |     |      |",
        "|        <-----------------------------<           |     |      |",
        "|        v                                         |     |      |",
        "|        rXrW-X9M1+M*+WWb+W1+9M1+M*%Mv             |     |      |",
        "|         v                          v             |     |      |",
        "|         rW-X9M1+M*+WWb+W1+9M1+M*%M v             |     |      |",
        "|         |  v<<<<<<<<<<<<<<<<<<<<<< v             |     |      |",
        "|         >dmsr        >dmsr         v             |     |      |",
        "|          v<--<        v<--<        v             |     |      |",
        "|          r            r            v             |     |      |",
        "|          r            s            v             |     |      |",
        "|          s            |            v             |     |      |",
        "|          |  s<<<<<<<<<+            v             |     |      |",
        "|          v  v                      v             |     |      |",
        "|          ^<<^<<<<<<<<<<<<<<<<<<<<<<<             |     |      |",
        "+--------------------------------------------------+     +------+"
    ]
    return "\n".join(lines)

def run_tests():
    spec = json.load(open('spec.json'))
    cases = spec['publicTestData']
    
    prog_text = create_memory_man()
    with open('memory.man', 'w') as f:
        f.write(prog_text + '\n')
    
    print("Generated memory.man with Memory Room man. Running tests...")
    
    passed = 0
    total = len(cases)
    for i, tc in enumerate(cases):
        inputs = [int(x) for x in tc['in']]
        expected = [int(x) for x in tc['out']]
        try:
            out, ticks, w, h = sim.run(prog_text, inputs, max_ticks=500000)
            if out == expected:
                passed += 1
                print(f"  Case {i}: PASS (ticks={ticks}, out_len={len(out)})")
            else:
                print(f"  Case {i}: FAIL - expected {expected[:3]}..., got {out[:3]}...")
        except Exception as e:
            print(f"  Case {i}: ERROR - {type(e).__name__}: {e}")
            
    print(f"\nResult: {passed}/{total} passed.")

if __name__ == '__main__':
    run_tests()
