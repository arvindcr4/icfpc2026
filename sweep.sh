#!/bin/bash
cd /home/claude/icfpc2026
while read -r name tab; do
  [ -z "$name" ] && continue
  r=$(timeout 60 node cdp.js eval "$tab" "(()=>{const b=document.body.innerText;const dl=[...document.querySelectorAll('a,button,[role=button]')].filter(x=>/download/i.test(x.innerText||'')).length;return JSON.stringify({g:!!document.querySelector('[data-testid=\"stop-button\"]'),dl,e:/Something went wrong|Too many requests/.test(b),t:b.slice(-90).replace(/\n/g,' ')});})()" 2>/dev/null | tail -1)
  echo "$name|$r"
done < tabs.txt | python3 -c "
import sys,json
for line in sys.stdin:
    if '|' not in line: continue
    n,raw=line.split('|',1)
    try: d=json.loads(json.loads(raw.strip()))
    except Exception: print(f'{n:<15} unreadable'); continue
    st='working' if d['g'] else ('ERROR' if d['e'] else ('READY dl=%d'%d['dl'] if d['dl'] else 'idle-nofile'))
    print(f\"{n:<15} {st:<14} {d['t'][-70:]}\")
"
