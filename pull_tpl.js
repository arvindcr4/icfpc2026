(async()=>{
 const CONV='__CONV__', PATH='__PATH__';
 const sleep=ms=>new Promise(r=>setTimeout(r,ms));
 const s=await (await fetch('/api/auth/session')).json(); const tok=s.accessToken;
 const j=await (await fetch('/backend-api/conversation/'+CONV,{headers:{'Authorization':'Bearer '+tok}})).json();
 let lastMsg=null,lastCt=0;
 for(const k in j.mapping){const m=j.mapping[k].message;
  if(m&&m.author.role==='assistant'&&m.create_time>lastCt){lastCt=m.create_time;lastMsg=m.id;}}
 const u='/backend-api/conversation/'+CONV+'/interpreter/download?message_id='+lastMsg+'&sandbox_path='+encodeURIComponent(PATH);
 let err='';
 for(let a=0;a<4;a++){
  try{
   const r=await fetch(u,{headers:{'Authorization':'Bearer '+tok}});
   const d=await r.json();
   if(!d.download_url){err='NOURL '+JSON.stringify(d).slice(0,150); await sleep(8000); continue;}
   const f=await fetch(d.download_url,{credentials:'include'});
   const t=await f.text();
   if(t.length>40) return t;
   err='short '+t.length;
  }catch(e){err=String(e).slice(0,120);}
  await sleep(8000);
 }
 return 'PULLERR '+err;})()
