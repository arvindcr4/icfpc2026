import sys, json
import sim
import test_generator

def create_complete_tcp():
    # Constructing complete Littleman code grid
    grid = """
+-+  +-+  +-+
|I|  |O|  | |
+-+  +-+  +-+
 v    ^   ^v
 v    ^   ^v
+--------------------------+       +----+
|@9M6+b>>v>0sv..r0M........|>----->|@rsv|
|       ^<dm<..............|<-----<|^sr<|
|rWMW-M8M8+W-vX            |       +----+
|1N..s..H... v             |             
|            X>r..s1+M.....|             
|                      ^0s<|             
+--------------------------+             
""".strip()
    grid_lines = grid.split('\n')
    w = max(len(l) for l in grid_lines)
    padded_grid = "\n".join(l.ljust(w) for l in grid_lines)
    with open('/home/claude/icfpc2026/tcp.man', 'w') as f:
        f.write(padded_grid + '\n')
    
    return test_generator.run_test_suite(padded_grid)

if __name__ == '__main__':
    create_complete_tcp()
