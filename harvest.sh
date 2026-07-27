#!/bin/bash
TID=$(cat harvest_tab.txt)
while read -r href; do
  [ -z "$href" ] && continue
  timeout 60 node cdp.js eval "$TID" "(()=>{location.href='https://chatgpt.com$href';return 1;})()" >/dev/null 2>&1
  python3 -c "import time; time.sleep(9)"
  timeout 90 node cdp.js eval "$TID" "(()=>{
    const u=[...document.querySelectorAll('[data-message-author-role=\"user\"]')].map(e=>e.innerText).join(' ');
    const m=u.match(/\(slug ([a-z-]+)\)/); const slug=m?m[1]:'?';
    const a=[...document.querySelectorAll('[data-message-author-role=\"assistant\"]')];
    const pre=a.flatMap(t=>[...t.querySelectorAll('pre')].map(p=>p.innerText));
    const g=pre.filter(t=>/[|+][-+]/.test(t)&&t.includes('@')&&t.split('\n').length>3);
    return JSON.stringify({slug,grids:g.length,pick:g.length?g[g.length-1]:'',reply:a.map(x=>x.innerText).join('').length});
  })()" 2>/dev/null > /tmp/h.json
  python3 - <<'PY'
import json,pathlib
try:
    d=json.loads(json.loads(pathlib.Path('/tmp/h.json').read_text().strip()))
except Exception: raise SystemExit
s=d['slug']; p=d.get('pick','')
if p.strip() and s!='?':
    L=p.rstrip('\n').split('\n')
    pathlib.Path(f'gpt/h_{s}.man').write_text('\n'.join(L)+'\n')
    print(f"    {s:<26} GRID {max(len(x) for x in L)}x{len(L)}  reply={d['reply']}")
else:
    print(f"    {s:<26} no grid (reply={d['reply']})")
PY
done
