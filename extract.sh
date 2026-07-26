#!/bin/bash
while IFS=: read -r s id; do
  timeout 90 node cdp.js eval "$id" "(()=>{const pre=[...document.querySelectorAll('pre')].map(p=>p.innerText);const c=pre.filter(t=>/[|+][-+]/.test(t)&&t.includes('@'));return JSON.stringify({n:pre.length,pick:c.length?c[c.length-1]:''});})()" 2>/dev/null > "gpt/$s.raw"
  python3 - "$s" <<'PY'
import json,sys,pathlib
s=sys.argv[1]
try:
    raw=pathlib.Path(f'gpt/{s}.raw').read_text().strip()
    d=json.loads(json.loads(raw))
except Exception:
    print(f"  {s:<16} no response captured"); raise SystemExit
prog=d.get('pick','')
if prog.strip():
    pathlib.Path(f'gpt/{s}.man').write_text(prog if prog.endswith('\n') else prog+'\n')
    L=prog.split('\n')
    print(f"  {s:<16} blocks={d['n']}  program {max(len(x) for x in L)}x{len(L)}")
else:
    print(f"  {s:<16} blocks={d['n']}  (no grid-shaped block yet)")
PY
done
