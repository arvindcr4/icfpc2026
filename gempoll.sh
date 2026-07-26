#!/bin/bash
while IFS=: read -r s id; do
  timeout 90 node cdp.js eval "$id" "(()=>{
    const pre=[...document.querySelectorAll('pre,code')].map(p=>p.innerText);
    const grids=pre.filter(t=>/[|+][-+]/.test(t)&&t.includes('@')&&t.split('\n').length>3);
    const body=document.body.innerText;
    const busy=/Generating your response|Check back later|Thinking/i.test(body.slice(-600));
    return JSON.stringify({busy,n:pre.length,pick:grids.length?grids[grids.length-1]:'',chars:body.length});
  })()" 2>/dev/null > "gpt/gem_$s.raw"
  python3 - "$s" <<'PY'
import json,sys,pathlib
s=sys.argv[1]
try:
    d=json.loads(json.loads(pathlib.Path(f'gpt/gem_{s}.raw').read_text().strip()))
except Exception:
    print(f"  {s:<14} unreadable"); raise SystemExit
p=d.get('pick','')
if p.strip():
    L=p.rstrip('\n').split('\n')
    pathlib.Path(f'gpt/gem_{s}.man').write_text('\n'.join(L)+'\n')
    print(f"  {s:<14} busy={str(d['busy']):<5} GRID {max(len(x) for x in L)}x{len(L)}")
else:
    print(f"  {s:<14} busy={str(d['busy']):<5} blocks={d['n']} chars={d['chars']} no grid yet")
PY
done
