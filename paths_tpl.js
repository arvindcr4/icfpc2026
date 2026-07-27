(async()=>{
 const CONV='__CONV__';
 const s=await (await fetch('/api/auth/session')).json(); const tok=s.accessToken;
 const j=await (await fetch('/backend-api/conversation/'+CONV,{headers:{'Authorization':'Bearer '+tok}})).json();
 const paths=new Set();
 for(const k in j.mapping){const m=j.mapping[k].message; if(!m) continue;
  const c=m.content; const t=(c.parts||[]).filter(p=>typeof p==='string').join('\n')+(c.text||'');
  for(const mm of t.matchAll(/\/mnt\/data\/[A-Za-z0-9_.\-]+/g)) paths.add(mm[0]);}
 return JSON.stringify([...paths]);})()
