import sys, json
import sim

def create_tcp_man():
    # Grid dimensions: w=37, h=11
    # Room I: (0,1,2,3)
    # Room O: (5,1,7,3)
    # Room S: (10,1,12,3)
    # Room MAIN: (0,6,27,10)
    # Room MEM: (30,6,34,9)

    grid = """
+-+  +-+  +-+
|I|  |O|  | |
+-+  +-+  +-+
 v    ^   ^v
 v    ^   ^v
+--------------------------+       +----+
|@9M6+b>>v>0sv..r0M........|>----->|@rsv|
|       ^<dm<..^...........|<-----<|^sr<|
|                          |       +----+
|                          |
+--------------------------+
""".strip()
    grid_lines = grid.split('\n')
    w = max(len(l) for l in grid_lines)
    padded_grid = "\n".join(l.ljust(w) for l in grid_lines)
    with open('/home/claude/icfpc2026/tcp.man', 'w') as f:
        f.write(padded_grid + '\n')
    
    import test_generator
    return test_generator.run_test_suite(padded_grid)

if __name__ == '__main__':
    create_tcp_man()
