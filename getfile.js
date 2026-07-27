(async()=>{
 const CONV='CONVID';
 const s=await (await fetch('/api/auth/session')).json(); const tok=s.accessToken;
 const j=await (await fetch('/backend-api/conversation/'+CONV,{headers:{'Authorization':'Bearer '+tok}})).json();
 const paths=new Set(); let lastMsg=null; let lastCt=0;
 for(const k in j.mapping){const m=j.mapping[k].message; if(!m) continue;
  const c=m.content; const t=(c.parts||[]).filter(p=>typeof p==='string').join('\n')+(c.text||'');
  for(const mm of t.matchAll(/sandbox:(\/mnt\/data\/[A-Za-z0-9_.\-]+)/g)) paths.add(mm[1]);
  if(m.author.role==='assistant'&&m.create_time>lastCt){lastCt=m.create_time;lastMsg=m.id;}}
 const out={paths:[...paths],lastMsg};
 out.dl=[];
 for(const p of out.paths){
  const u='/backend-api/conversation/'+CONV+'/interpreter/download?message_id='+lastMsg+'&sandbox_path='+encodeURIComponent(p);
  const r=await fetch(u,{headers:{'Authorization':'Bearer '+tok}});
  out.dl.push({p,status:r.status,body:(await r.text()).slice(0,300)});}
 return JSON.stringify(out).slice(0,2500);})()
