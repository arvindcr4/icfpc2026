import subprocess
import json
import os

def create_matmul_man():
    # Write layout for matmul.man
    layout = """+-+ +-+
|I| |O|
+-+ +-+
 v   ^
 v   ^
+-------------------------------+   +-----+
|@r s  v|>--------------------->|>->| >r v|
|^     <|<-<<<<<<<<<<<<<<<<<<<<<|<-<| ^s <|
+-------------------------------+   +-----+"""
    
    with open('/home/claude/icfpc2026/matmul.man', 'w') as f:
        f.write(layout + '\n')

if __name__ == '__main__':
    create_matmul_man()
    print("Created matmul.man")
