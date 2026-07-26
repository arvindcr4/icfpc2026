#!/bin/bash
s=$1
TID=$(timeout 60 node cdp.js newtab "https://gemini.google.com/app" 2>&1 | tail -1)
for i in 1 2 3 4 5 6; do
  python3 -c "import time; time.sleep(5)"
  R=$(timeout 60 node cdp.js eval "$TID" "(()=>!!document.querySelector('div[contenteditable=\"true\"]'))()" 2>&1 | tr -d '\"')
  [ "$R" = "true" ] && break
done
timeout 90 node cdp.js eval "$TID" "(()=>{const b=[...document.querySelectorAll('button')].find(e=>/mode picker/i.test(e.getAttribute('aria-label')||''));if(b)b.click();return 'picker';})()" >/dev/null 2>&1
python3 -c "import time; time.sleep(3)"
timeout 90 node cdp.js eval "$TID" "(()=>{const els=[...document.querySelectorAll('*')].filter(e=>e.children.length===0||e.getAttribute('role'));const t=els.find(e=>/^Deep Think/.test((e.innerText||'').trim()));if(!t)return 'nf';let n=t;for(let i=0;i<6&&n;i++){if(n.getAttribute&&/menuitem|option/i.test(n.getAttribute('role')||'')){n.click();return 'ok';}n=n.parentElement;}t.click();return 'leaf';})()" >/dev/null 2>&1
python3 -c "import time; time.sleep(3)"
MODE=$(timeout 60 node cdp.js eval "$TID" "(()=>{const b=[...document.querySelectorAll('button')].find(e=>/mode picker/i.test(e.getAttribute('aria-label')||''));return b?b.getAttribute('aria-label'):'?';})()" 2>&1 | tr -d '\"')
OUT=$(timeout 300 node cdp.js ask "$TID" "prompts/$s.txt" 2>&1 | tail -1)
printf "  %-14s tab=%s  %s  |  %s\n" "$s" "${TID:0:8}" "$MODE" "$OUT"
echo "$s:$TID" >> gem_tabs.txt
