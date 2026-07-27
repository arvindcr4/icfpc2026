(async()=>{
 const s=await (await fetch('/api/auth/session')).json();
 const j=await (await fetch('/backend-api/conversation/6a65bd47-62f0-83ee-a5bd-abe9a985881d',{headers:{'Authorization':'Bearer '+s.accessToken}})).json();
 const rows=[];
 for(const k in j.mapping){const m=j.mapping[k].message; if(!m||m.author.role!=='assistant') continue;
  const c=m.content; if(c.content_type!=='text') continue;
  const t=(c.parts||[]).join('\n'); if(t.includes('sandbox:')||t.includes('.man')||t.includes('.md'))
    rows.push({id:m.id,ct:m.create_time,t});}
 rows.sort((a,b)=>a.ct-b.ct);
 return JSON.stringify(rows.slice(-4)).slice(0,3000);})()
