#!/usr/bin/env python3
import json, pathlib, sys
slug, maxframe_cases = sys.argv[1], int(sys.argv[2])
D = pathlib.Path('/home/claude/icfpc2026')
d = json.loads((D / f'spec_{slug}.json').read_text())
old = (D / 'prompts' / f'{slug}.txt').read_text()
cut = old.find('Sample public cases:')
head = old[:cut] if cut > 0 else old
disp = d.get('io', {}).get('display')
P = [head.rstrip(), '\n=== COMPLETE PUBLIC TEST DATA ===',
     'The earlier version of this prompt showed truncated inputs and `out=[]`, which was',
     'misleading: this is a DISPLAY problem, so the real expected result is `frames`.',
     f"Display is {disp.get('width')}x{disp.get('height')}." if disp else '',
     'Below is the complete data: `in` is the exact value sequence delivered to the input room,',
     '`frames` is the exact sequence of display frames your program must commit.\n']
for ci, c in enumerate(d['publicTestData']):
    P.append(f"--- case: {c['name']} ({len(c['rounds'])} rounds) ---")
    for i, r in enumerate(c['rounds']):
        P.append(f"  round {i} in = {json.dumps(r.get('in', []))}")
        if r.get('out'): P.append(f"  round {i} out = {json.dumps(r['out'])}")
        if ci < maxframe_cases:
            for j, fr in enumerate(r.get('frames') or []):
                P.append(f"  round {i} frame {j}:")
                for row in fr: P.append(f"      {row}")
    P.append('')
if '=== WHAT I WANT BACK ===' in old:
    P.append(old[old.find('=== WHAT I WANT BACK ==='):])
P.append(f"""
DELIVERY: write the finished program with python to /mnt/data/{slug}_v2.man — verbatim grid, one
line per row, no markdown fences, single trailing newline. Build a simulator and check every
public case above against its frames BEFORE writing the file, then report which cases pass.

Keep the grid small: score is max(width,height)^2 * avgTicks, so a wide grid scores badly even
when correct. And route every pipe so its body is only '-' (horizontal) or '|' (vertical) with
arrowheads at both ends and at every bend — a pipe that runs through any other glyph is a load
error that fails every case.
""")
out = D / 'prompts2' / f'{slug}_full.txt'
out.write_text('\n'.join(P))
print(f"{out.name}: {out.stat().st_size} bytes")
