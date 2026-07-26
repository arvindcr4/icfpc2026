import json
import subprocess
import os

def test_matmul_solution():
    man_path = '/home/claude/icfpc2026/matmul.man'
    spec_path = '/home/claude/icfpc2026/matmul_spec.json'
    
    if not os.path.exists(man_path):
        print(f"Error: {man_path} does not exist.")
        return False
        
    with open(spec_path) as f:
        spec = json.load(f)
        
    public_data = spec.get('publicTestData', [])
    total_cases = 0
    passed_cases = 0
    total_ticks = 0
    
    print(f"Testing {man_path} against publicTestData...")
    
    for cat_idx, category in enumerate(public_data):
        cat_name = category.get('name', f'Category {cat_idx}')
        rounds = category.get('rounds', [])
        
        for r_idx, round_data in enumerate(rounds):
            total_cases += 1
            in_list = round_data.get('in', [])
            expected_out = round_data.get('out', [])
            
            in_str = ' '.join(in_list)
            
            cmd = ['python3', '/home/claude/icfpc2026/sim.py', man_path, '--in', in_str]
            res = subprocess.run(cmd, capture_output=True, text=True)
            
            if res.returncode != 0:
                print(f"[FAIL] {cat_name} (Round {r_idx}): Exit code {res.returncode}")
                print(f"       Stderr: {res.stderr.strip()}")
                continue
                
            actual_out = [x.strip() for x in res.stdout.strip().split() if x.strip()]
            
            if actual_out == expected_out:
                passed_cases += 1
                # Parse ticks and score from stderr line e.g. [23x15 area2=529 ticks=1234 score~652831]
                stderr_line = res.stderr.strip().splitlines()[-1] if res.stderr.strip() else ""
                print(f"[PASS] {cat_name} (Round {r_idx}): Output matched ({len(actual_out)} ints). Info: {stderr_line}")
            else:
                print(f"[FAIL] {cat_name} (Round {r_idx}): Mismatch. Expected len {len(expected_out)}, got {len(actual_out)}")
                if len(actual_out) <= 10:
                    print(f"       Actual: {actual_out}")
                    print(f"       Expected: {expected_out}")
                    
    print("\n" + "="*50)
    print(f"SUMMARY: Passed {passed_cases} / {total_cases} test cases.")
    print("="*50)
    
    return passed_cases == total_cases

if __name__ == '__main__':
    test_matmul_solution()
