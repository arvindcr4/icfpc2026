#!/bin/bash
# grab.sh <name> <tabId>  — click the download link, capture the file Chromium writes.
cd /home/claude/icfpc2026
n="$1"; t="$2"
mkdir -p /home/claude/Downloads/_old
mv /home/claude/Downloads/.org.chromium* /home/claude/Downloads/*.man /home/claude/Downloads/_old/ 2>/dev/null
before=$(ls -a /home/claude/Downloads | sort | md5sum)
r=$(timeout 60 node cdp.js eval "$t" "(()=>{const e=[...document.querySelectorAll('a,button,[role=button]')].filter(x=>/download/i.test(x.innerText||''));if(!e.length)return 'none';e[e.length-1].click();return 'clicked:'+e[e.length-1].innerText.trim();})()" 2>/dev/null)
echo "$n: $r"
[ "$r" = '"none"' ] && exit 1
for i in $(seq 1 20); do
  python3 -c "import time; time.sleep(5)"
  after=$(ls -a /home/claude/Downloads | sort | md5sum)
  [ "$before" != "$after" ] && break
done
f=$(ls -t /home/claude/Downloads/.org.chromium* /home/claude/Downloads/*.man 2>/dev/null | head -1)
if [ -n "$f" ]; then
  s1=0; for k in $(seq 1 30); do s2=$(stat -c%s "$f"); [ "$s1" = "$s2" ] && [ "$s2" != "0" ] && break; s1=$s2; python3 -c "import time; time.sleep(4)"; done
fi
[ -z "$f" ] && { echo "$n: no file appeared"; exit 1; }
python3 - "$f" "gpt/$n.man" <<'PY'
import pathlib,sys
t=pathlib.Path(sys.argv[1]).read_text(errors='replace')
L=t.rstrip('\n').split('\n')
ok=any('@' in x for x in L) and any('+' in x for x in L)
print(f"   rows={len(L)} maxw={max(len(x) for x in L)} bytes={len(t)} grid={ok}")
if ok: pathlib.Path(sys.argv[2]).write_text('\n'.join(L)+'\n'); print("   -> "+sys.argv[2])
PY
