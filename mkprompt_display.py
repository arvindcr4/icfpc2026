#!/usr/bin/env python3
"""Rebuild a prompt for a DISPLAY problem with COMPLETE public test data.

The earlier prompts truncated `in` at 60 items and printed `out=[]`, which for a display
problem is the entire expected answer thrown away — the real target is `frames`.
"""
import json, pathlib, sys

slug = sys.argv[1]
D = pathlib.Path('/home/claude/icfpc2026')
d = json.loads((D / f'spec_{slug}.json').read_text())
old = (D / 'prompts' / f'{slug}.txt').read_text()

# keep everything in the old prompt before the (bad) sample-cases block
cut = old.find('Sample public cases:')
head = old[:cut] if cut > 0 else old

parts = [head.rstrip(), '\n=== COMPLETE PUBLIC TEST DATA ===',
         'This is the FULL data, not a sample. For each round: `in` is the exact value sequence',
         'delivered to the input room, and `frames` is the exact sequence of display frames your',
         'program must commit (each frame is 16 rows of 16 characters). `out` is empty for this',
         'problem because everything observable is on the display.\n']

for c in d['publicTestData']:
    parts.append(f"--- case: {c['name']} ({len(c['rounds'])} rounds) ---")
    for i, r in enumerate(c['rounds']):
        parts.append(f"  round {i} in  = {json.dumps(r.get('in', []))}")
        if r.get('out'):
            parts.append(f"  round {i} out = {json.dumps(r['out'])}")
        for j, fr in enumerate(r.get('frames') or []):
            parts.append(f"  round {i} frame {j}:")
            for row in fr:
                parts.append(f"      {row}")
    parts.append('')

tail = old[old.find('=== WHAT I WANT BACK ==='):] if '=== WHAT I WANT BACK ===' in old else ''
parts.append(tail)
parts.append("""
DELIVERY: write the finished program with python to /mnt/data/%s_v2.man — verbatim grid, one
line per row, no markdown fences, single trailing newline. Build a simulator and check every
public case above against its frames BEFORE writing the file. Report which cases pass.

Note on the previous attempt: it failed to load with
    LoadError: pipe from (11976,1142) hit '=' at (12167,1878)
A pipe body may only be '-' (horizontal) or '|' (vertical) with arrowheads at both ends and at
every bend. It may not run through any other glyph. Route pipes so they never cross foreign
characters, and keep the grid small — score is max(width,height)^2 * avgTicks, so a
12,834-column grid scores catastrophically even if correct.
""" % slug)

out = D / 'prompts2' / f'{slug}_full.txt'
out.write_text('\n'.join(parts))
print(f"{out}: {out.stat().st_size} bytes")
