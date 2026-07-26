import subprocess, sys, json

# Let's assemble the complete brackets.man program in python and run all 9 public test cases

with open('/home/claude/icfpc2026/spec_brackets.json') as f:
    spec = json.load(f)
public_tests = spec['publicTestData']

# Let's test python simulation of our exact Littleman instruction pipeline
def solve_single_case(inputs):
    if not inputs: return 0
    n = inputs[0]
    if n == 0: return 0
    chars = inputs[1:n+1]
    
    stack = 0
    pos = 1
    
    for c in chars:
        if c < 50:
            btype = 1
            diff = c - 40
        elif c < 110:
            btype = 2
            diff = c - 91
        else:
            btype = 3
            diff = c - 123
            
        if diff == 0:
            stack = stack * 4 + btype
        else:
            top = stack % 4
            stack = stack // 4
            if top != btype:
                return pos
        pos += 1
        
    if stack != 0:
        return pos
    return 0

for tc in public_tests:
    res = solve_single_case([int(x) for x in tc['in']])
    exp = int(tc['out'][0])
    assert res == exp, f"Mismatch on {tc['name']}: got {res}, expected {exp}"

print("All 9 test cases verified logically in Python!")
