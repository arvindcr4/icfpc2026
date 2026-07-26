import sys, json
import sim

def build_grid():
    # We construct a 2D array of characters for the solution
    lines = [
        "+-+  +-+  +-+",
        "|I|  |O|  | |",
        "+-+  +-+  +-+",
        " v    ^   ^v ",
        " v    ^   ^v ",
        "+--------------------------+       +----+",
        "|@                         |>----->|@rsv|",
        "|                          |<-----<|^sr<|",
        "+--------------------------+       +----+"
    ]
    return "\n".join(lines)

def run():
    grid = build_grid()
    with open('/home/claude/icfpc2026/tcp.man', 'w') as f:
        f.write(grid + '\n')
    
    import test_tcp
    return test_tcp.test_all_cases('/home/claude/icfpc2026/tcp.man')

if __name__ == '__main__':
    run()
