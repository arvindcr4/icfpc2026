#!/bin/bash
# usage: printf 'slug:tabid\n' ... | ./poll.sh
while IFS=: read -r s id; do
  timeout 90 node cdp.js eval "$id" "(()=>{
    const turns=[...document.querySelectorAll('[data-message-author-role=\"assistant\"]')];
    const pre=turns.flatMap(t=>[...t.querySelectorAll('pre')].map(p=>p.innerText));
    const grids=pre.filter(t=>/[|+][-+]/.test(t)&&t.includes('@'));
    const busy=!!document.querySelector('button[aria-label*=\"Stop\"],button[data-testid*=\"stop\"]');
    const model=(()=>{const b=[...document.querySelectorAll('button')].find(e=>/^(Pro|Instant|Thinking|Auto)\b/.test((e.innerText||'').trim()));return b?b.innerText.trim().split('\n')[0]:'?';})();
    const txt=turns.map(t=>t.innerText).join('\n');
    return JSON.stringify({busy,model,turns:turns.length,grids:grids.length,
      pick:grids.length?grids[grids.length-1]:'',reply:txt.length});
  })()" 2>/dev/null > "gpt/$s.raw"
  python3 - "$s" <<'PY'
import json,sys,pathlib
s=sys.argv[1]
try:
    raw=pathlib.Path(f'gpt/{s}.raw').read_text().strip()
    d=json.loads(json.loads(raw))
except Exception:
    print(f"  {s:<16} unreadable"); raise SystemExit
prog=d.get('pick','')
tag=f"busy={str(d['busy']):<5} model={d['model']:<8} reply={d['reply']:<6}"
if prog.strip():
    L=prog.rstrip('\n').split('\n')
    pathlib.Path(f'gpt/{s}.man').write_text('\n'.join(L)+'\n')
    print(f"  {s:<16} {tag} GRID {max(len(x) for x in L)}x{len(L)}")
else:
    print(f"  {s:<16} {tag} no grid yet")
PY
done
