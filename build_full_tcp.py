import sim, test_generator

def create_tcp_man():
    # Constructing clean grid for tcp.man
    # I room: (0,1,2,3)
    # O room: (5,1,7,3)
    # S room (store): (10,1,12,3)
    # MAIN room: (0,6,27,11)
    # MEM room: (30,6,34,9)

    grid = """
+-+  +-+  +-+
|I|  |O|  | |
+-+  +-+  +-+
 v    ^   ^v
 v    ^   ^v
+--------------------------+       +----+
|@9M6+b0smdrM..............|>----->|@rsv|
|rWMW-M9M6+W-vX............|<-----<|^sr<|
|..........................|       +----+
|..........................|
+--------------------------+
""".strip()
    grid_lines = grid.split('\n')
    w = max(len(l) for l in grid_lines)
    padded_grid = "\n".join(l.ljust(w) for l in grid_lines)
    with open('/home/claude/icfpc2026/tcp.man', 'w') as f:
        f.write(padded_grid + '\n')
    
    return test_generator.run_test_suite(padded_grid)

if __name__ == '__main__':
    create_tcp_man()
