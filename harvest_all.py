#!/usr/bin/env python3
"""Poll the five in-flight ChatGPT Pro runs; harvest, verify and log each as it finishes.

Two harvest paths, because big grids never survive the chat DOM:
  1. fenced code blocks in the rendered message (works for small programs);
  2. the backend-api sandbox download for /mnt/data/*.man (works for big grids).
Every harvested program is verified with verify.py before it is called a pass.
"""
import json, os, re, subprocess, sys, time, pathlib

RUNS = {
    "little-little-little-man": "6a65deb8",
    "little-little-man":        "6a65ddab",
    "subset-sum":               "6a65d7ad",
    "pathfinder":               "6a65d6e5",
    "matmul":                   "6a65d61e",
}
D = pathlib.Path("/home/claude/icfpc2026")
LOG = D / "harvest.log"

def cdp(conv, js):
    r = subprocess.run(["node", "cdp.js", "eval", conv, js], cwd=D,
                       capture_output=True, text=True, timeout=180)
    out = r.stdout.strip().split("\n")[-1] if r.stdout.strip() else ""
    try:
        return json.loads(out)
    except Exception:
        return out

def log(m):
    line = f"[{time.strftime('%H:%M:%S')}] {m}"
    print(line, flush=True)
    with LOG.open("a") as f: f.write(line + "\n")

BUSY_JS = """(()=>JSON.stringify({busy:!!document.querySelector('[data-testid="stop-button"]'),
  turns:document.querySelectorAll('[data-message-author-role="assistant"]').length,
  ansLen:(()=>{const a=[...document.querySelectorAll('[data-message-author-role="assistant"]')].pop();
    return a?a.innerText.length:0;})()}))()"""

BLOCK_JS = """(()=>{const a=[...document.querySelectorAll('[data-message-author-role="assistant"]')].pop();
  if(!a) return JSON.stringify({blocks:[],paths:[]});
  const bs=[...a.querySelectorAll('pre code, pre')].map(e=>e.innerText)
    .filter(t=>t.includes('+')&&(t.includes('|')||t.includes('@')));
  const paths=[...new Set([...a.innerText.matchAll(/\\/mnt\\/data\\/[A-Za-z0-9_.\\-]+/g)].map(m=>m[0]))];
  return JSON.stringify({blocks:bs.slice(-3),paths});})()"""

def fetch_sandbox(conv, path):
    js = ("""(async()=>{const s=await (await fetch('/api/auth/session')).json();const tok=s.accessToken;
      const j=await (await fetch('/backend-api/conversation/'+location.pathname.split('/c/')[1],
        {headers:{'Authorization':'Bearer '+tok}})).json();
      let last=null,ct=0;
      for(const k in j.mapping){const m=j.mapping[k].message;if(!m)continue;
        if(m.author.role==='assistant'&&m.create_time>ct){ct=m.create_time;last=m.id;}}
      const u='/backend-api/conversation/'+location.pathname.split('/c/')[1]+
        '/interpreter/download?message_id='+last+'&sandbox_path='+encodeURIComponent(%s);
      const r=await fetch(u,{headers:{'Authorization':'Bearer '+tok}});
      const j2=await r.json(); if(!j2.download_url) return JSON.stringify({err:JSON.stringify(j2).slice(0,200)});
      const txt=await (await fetch(j2.download_url)).text();
      return JSON.stringify({ok:true,txt});})()""" % json.dumps(path))
    return cdp(conv, js)

def verify(slug, f):
    r = subprocess.run([sys.executable, "verify.py", slug, str(f)], cwd=D,
                       capture_output=True, text=True, timeout=900)
    tail = [l for l in r.stdout.strip().split("\n") if l.strip()]
    return tail[-1] if tail else (r.stderr.strip().split("\n")[-1] if r.stderr.strip() else "no output")

done = {}
while len(done) < len(RUNS):
    for slug, conv in RUNS.items():
        if slug in done: continue
        st = cdp(conv, BLOCK_JS.replace("XX","") if False else BUSY_JS)
        if not isinstance(st, dict):
            log(f"{slug}: cdp read failed ({str(st)[:60]})"); continue
        if st.get("busy"):
            continue
        got = cdp(conv, BLOCK_JS)
        if not isinstance(got, dict):
            log(f"{slug}: block read failed"); done[slug]="read-fail"; continue
        prog = None
        for b in reversed(got.get("blocks") or []):
            if len(b) > 40: prog = b; break
        if not prog:
            for pth in got.get("paths") or []:
                r = fetch_sandbox(conv, pth)
                if isinstance(r, dict) and r.get("ok") and len(r.get("txt","")) > 40:
                    prog = r["txt"]; log(f"{slug}: pulled {pth} ({len(prog)} chars)"); break
        if not prog:
            log(f"{slug}: FINISHED but no program found (ansLen={st.get('ansLen')})")
            done[slug] = "no-program"; continue
        f = D / "gpt" / f"{slug}.man"
        f.write_text(prog.rstrip("\n") + "\n")
        log(f"{slug}: harvested {len(prog)} chars -> {f.name}; verifying")
        res = verify(slug, f)
        log(f"{slug}: VERIFY {res}")
        done[slug] = res
    if len(done) < len(RUNS):
        time.sleep(120)
log("ALL RUNS RESOLVED: " + json.dumps(done, indent=1))
