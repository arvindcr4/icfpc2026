#!/usr/bin/env python3
"""Run a .man against the problem's real publicTestData using sim.py's engine."""
import json, subprocess, sys, urllib.request, pathlib
sys.path.insert(0, '/home/claude/icfpc2026')
import sim

def spec(slug):
    p = pathlib.Path(f'/home/claude/icfpc2026/spec_{slug}.json')
    if not p.exists():
        p.write_bytes(urllib.request.urlopen(
            f'https://icfpcontest2026.com/api/v1/public/problems/{slug}', timeout=60).read())
    return json.loads(p.read_text())

def cases(d):
    out = []
    for c in d.get('publicTestData') or []:
        if 'rounds' in c:
            ins, outs = [], []
            for r in c['rounds']:
                ins += [int(x) for x in r.get('in', [])]
                outs += [int(x) for x in r.get('out', [])]
            out.append((c.get('name','?'), ins, outs))
        else:
            out.append((c.get('name','?'), [int(x) for x in c.get('in',[])],
                        [int(x) for x in c.get('out',[])]))
    return out

slug, prog = sys.argv[1], sys.argv[2]
text = pathlib.Path(prog).read_text()
cs = cases(spec(slug))
npass = 0
for name, ins, exp in cs:
    try:
        got, ticks, w, h = sim.run(text, ins, max_ticks=400000)
        ok = got == exp
        npass += ok
        print(f"  {'PASS' if ok else 'FAIL'}  {name[:34]:<34} got={got[:8]}{'...' if len(got)>8 else ''} want={exp[:8]}{'...' if len(exp)>8 else ''}")
    except Exception as e:
        print(f"  ERR   {name[:34]:<34} {type(e).__name__}: {str(e)[:70]}")
print(f"  => {npass}/{len(cs)} public cases pass")
