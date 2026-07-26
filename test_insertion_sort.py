import sys, json

def insertion_sort_sim(nums):
    storage_pipe = []
    output_pipe = []
    
    # Process each item in nums
    for xi in nums:
        inserted = False
        n_items = len(storage_pipe)
        new_storage = []
        for _ in range(n_items):
            item = storage_pipe.pop(0)
            if not inserted and xi <= item:
                new_storage.append(xi)
                new_storage.append(item)
                inserted = True
            else:
                new_storage.append(item)
        if not inserted:
            new_storage.append(xi)
        storage_pipe = new_storage
        
    # Drain storage pipe to output
    while storage_pipe:
        output_pipe.append(storage_pipe.pop(0))
        
    return output_pipe

# Test on all cases
spec = json.load(open('/home/claude/icfpc2026/spec_sort.json'))
for idx, tc in enumerate(spec['publicTestData']):
    for r_idx, r in enumerate(tc['rounds']):
        inp = r['in'][1:]
        nums = [int(x) for x in inp]
        exp = [int(x) for x in r['out']]
        got = insertion_sort_sim(nums)
        assert got == exp, f"Fail at case {idx+1} round {r_idx+1}: got {got}, exp {exp}"
print("Insertion sort logic simulation: 100% PASS ALL 19 ROUNDS!")
