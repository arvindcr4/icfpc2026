#!/usr/bin/env python3
import json
import sys
import sim

def generate_memory_man():
    # Construct memory.man
    # Width = 55, Height = 28
    
    # We will write out the exact memory.man content
    lines = [
        "+-+   +-+",
        "|I|   |O|",
        "+-+   +-+",
        " v     ^ ",
        "+---------------------------------------+     +-----+",
        "|@`100`b                                |     |r v  |",
        "|v<dms0                                 |>>>>>|^ s <|",
        "|r                                      |<<<<<|     |",
        "|X                                      |     +-----+",
        "| r                                     |            ",
        "| W-X`100`+WWb+W1+`100`%M               |            ",
        "|   v<------------------<               |            ",
        "|   v>dmsr                              |            ",
        "|     v<--<                             |            ",
        "|     r                                 |            ",
        "|     s                                 |            ",
        "|     s>v                               |            ",
        "|       |                               |            ",
        "|       +------------------------------>|            ",
        "|                                       |            ",
        "| r                                     |            ",
        "| W-X`100`+WWb+W1+`100`%M               |            ",
        "|   v<------------------<               |            ",
        "|   v>dmsr                              |            ",
        "|     v<--<                             |            ",
        "|     rWrWsWM                           |            ",
        "|     s>v                               |            ",
        "|       |                               |            ",
        "|       +------------------------------>|            ",
        "+---------------------------------------+            "
    ]
    return "\n".join(lines)

if __name__ == '__main__':
    prog = generate_memory_man()
    with open('memory.man', 'w') as f:
        f.write(prog + '\n')
    print("Wrote memory.man")
