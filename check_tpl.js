(async()=>{
 const s=await (await fetch('/api/auth/session')).json(); const tok=s.accessToken;
 const convs=__CONVS__; const out=[];
 for(const [name,cid] of convs){
  try{
   const j=await (await fetch('/backend-api/conversation/'+cid,{headers:{'Authorization':'Bearer '+tok}})).json();
   let lastCt=0,lastTxt='',paths=new Set(),n=0;
   for(const k in j.mapping){const m=j.mapping[k].message; if(!m) continue;
    const c=m.content; const t=(c.parts||[]).filter(p=>typeof p==='string').join('\n')+(c.text||'');
    for(const mm of t.matchAll(/\/mnt\/data\/[A-Za-z0-9_.\-]+/g)) paths.add(mm[0]);
    if(m.author.role==='assistant'){n++; if(m.create_time>lastCt&&c.content_type==='text'&&t.trim()){lastCt=m.create_time;lastTxt=t;}}}
   out.push({name,msgs:n,paths:[...paths],tail:lastTxt.slice(-260)});
  }catch(e){out.push({name,err:String(e).slice(0,80)});}}
 return JSON.stringify(out);})()
