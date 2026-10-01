'use strict';
/* Estimate recent visible lesson use. Never records guests, keys, or click histories. */
window.PQCActivity={start(getContext,send){
 let uid=null,tab='',seq=0,lastTick=performance.now(),lastInput=performance.now(),pending=0,busy=false,ready=false,lastEligible=false;
 const interaction=()=>{lastInput=performance.now();};
 for(const name of ['pointerdown','keydown','input','scroll'])window.addEventListener(name,interaction,{passive:true});
 document.addEventListener('visibilitychange',()=>{lastTick=performance.now();lastEligible=false;pending=0;});
 function sample(){
  const now=performance.now(),ctx=getContext(),nextUid=ctx.user?.role==='child'&&ctx.user.parent_id?ctx.user.id:null;
  if(nextUid!==uid){uid=nextUid;tab=Array.from(crypto.getRandomValues(new Uint8Array(16)),v=>v.toString(16).padStart(2,'0')).join('');seq=0;pending=0;ready=false;lastEligible=false;lastInput=now;}
  const eligible=!!uid&&document.visibilityState==='visible'&&['lesson','help'].includes(ctx.view)&&!!ctx.lesson&&now-lastInput<120000;
  const elapsed=(now-lastTick)/1000;
  if(!eligible||elapsed>2)pending=0;
  if(ready&&eligible&&lastEligible&&elapsed>=0&&elapsed<=2)pending=Math.min(30,pending+elapsed);
  lastTick=now;lastEligible=eligible;
  return {eligible,ctx};
 }
 async function flush(){
  const {eligible,ctx}=sample();
  if(busy||!eligible||(!pending&&ready))return;
  const identity=uid,amount=ready?pending:0;pending=0;busy=true;
  try{await send({tab,seq:seq++,seconds:amount,lesson:ctx.lesson});if(uid===identity)ready=true;}catch{if(uid===identity)ready=false;}finally{busy=false;}
 }
 const sampler=setInterval(sample,1000),sender=setInterval(flush,15000);
 return {flush,stop(){clearInterval(sampler);clearInterval(sender);}};
}};
