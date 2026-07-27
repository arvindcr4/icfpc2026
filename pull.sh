#!/bin/bash
# pull.sh <convId> <sandboxPath> <outFile>
TID=$(cat /home/claude/icfpc2026/harvest_tab.txt)
sed -e "s|__CONV__|$1|" -e "s|__PATH__|$2|" /home/claude/icfpc2026/pull_tpl.js > /tmp/pull_run.js
timeout 180 node /home/claude/icfpc2026/cdp.js evalfile "$TID" /tmp/pull_run.js > /tmp/pull_out.json 2>/tmp/pull_err.txt
python3 - "$3" <<'PY'
import json,sys,pathlib
raw=pathlib.Path('/tmp/pull_out.json').read_text()
try: txt=json.loads(raw)
except Exception:
    print("PULL FAILED:", raw[:200], pathlib.Path('/tmp/pull_err.txt').read_text()[:200]); raise SystemExit(1)
pathlib.Path(sys.argv[1]).write_text(txt)
L=txt.rstrip('\n').split('\n')
print(f"wrote {sys.argv[1]}: {len(txt)} bytes, {len(L)} rows, max width {max(len(x) for x in L)}")
PY
