import sys, json
import sim
import test_generator

def create_final_tcp():
    # Full verified Littleman program for tcp.man
    grid = """
+-+  +-+  +-+
|I|  |O|  | |
+-+  +-+  +-+
 v    ^   ^v
 v    ^   ^v
+--------------------------+       +----+
|@9M6+b>>>>>v>0sv..r0M.....|>----->|@rsv|
|          ^<dm<........v..|<-----<|^sr<|
|rWMW-M8M8+W-vX.........v..|       +----+
|1N..s..H... v..........v..|            
|            X>r..s1+M..v..|            
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
    create_final_tcp()
