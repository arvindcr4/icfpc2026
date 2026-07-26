#!/bin/bash
s=$1; TID=$2
if [ -z "$TID" ]; then
  TID=$(timeout 60 node cdp.js newtab "https://chatgpt.com/" 2>&1 | tail -1)
  for i in 1 2 3 4 5 6 7 8; do
    python3 -c "import time; time.sleep(4)"
    R=$(timeout 60 node cdp.js eval "$TID" "(()=>!!document.querySelector('#prompt-textarea'))()" 2>&1 | tr -d '\"')
    [ "$R" = "true" ] && break
  done
fi
MODEL=$(timeout 60 node cdp.js eval "$TID" "(()=>{const b=[...document.querySelectorAll('button')].find(e=>/^(Pro|Instant|Thinking|Auto)\b/.test((e.innerText||'').trim()));return b?b.innerText.trim().split('\n')[0]:'?';})()" 2>&1 | tr -d '\"')
OUT=$(timeout 300 node cdp.js ask "$TID" "prompts/$s.txt" 2>&1 | tr '\n' ' ')
printf "  %-14s tab=%s model=%-8s %s\n" "$s" "${TID:0:8}" "$MODEL" "$OUT"
echo "$s:$TID" >> pro_tabs.txt
