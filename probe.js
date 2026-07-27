(async()=>{
 const s=await (await fetch('/api/auth/session')).json();
 const r=await fetch('/backend-api/conversation/6a65bd47-62f0-83ee-a5bd-abe9a985881d',{headers:{'Authorization':'Bearer '+s.accessToken}});
 const j=await r.json(); const out=[];
 for(const k in j.mapping){const m=j.mapping[k].message; if(!m) continue;
  const c=m.content; const role=m.author.role+'/'+(m.author.name||'');
  let info={role,ct:c.content_type};
  if(c.parts) info.plen=c.parts.map(p=>typeof p==='string'?p.length:('OBJ:'+JSON.stringify(p).slice(0,80)));
  if(c.text) info.tlen=c.text.length;
  if(m.metadata&&m.metadata.aggregate_result) info.agg=JSON.stringify(m.metadata.aggregate_result).slice(0,200);
  out.push(info);}
 return JSON.stringify(out).slice(0,3000);})()
