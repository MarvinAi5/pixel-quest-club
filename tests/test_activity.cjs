const fs=require('fs'),vm=require('vm'),assert=require('node:assert/strict');
let now=0,ctx={user:null,view:'lesson',lesson:'story-1'},events={},timers=[],packets=[];
const sandbox={window:{addEventListener:(name,fn)=>events[name]=fn},document:{visibilityState:'visible',addEventListener:(name,fn)=>events[name]=fn},performance:{now:()=>now},crypto:require('node:crypto').webcrypto,Uint8Array,setInterval:fn=>{timers.push(fn);return timers.length;},clearInterval(){}};
vm.createContext(sandbox);vm.runInContext(fs.readFileSync('public/activity.js','utf8'),sandbox);
const tracker=sandbox.window.PQCActivity.start(()=>ctx,async body=>packets.push(body));
const tick=seconds=>{for(let i=0;i<seconds;i++){now+=1000;timers[0]();}};
(async()=>{
 await tracker.flush();assert.equal(packets.length,0);
 ctx.user={role:'child',id:'a',parent_id:'parent'};await tracker.flush();assert.equal(packets[0].seconds,0);
 tick(15);await tracker.flush();assert.equal(packets[1].seconds,15);
 sandbox.document.visibilityState='hidden';events.visibilitychange();tick(15);await tracker.flush();assert.equal(packets.length,2);
 sandbox.document.visibilityState='visible';events.visibilitychange();events.pointerdown();tick(16);await tracker.flush();assert.equal(packets[2].seconds,15);
 tick(130);await tracker.flush();const count=packets.length;assert.equal(count,3);
 events.keydown();tick(16);await tracker.flush();assert.equal(packets.at(-1).seconds,15); // idle pending time is discarded, never replayed later
 ctx.view='month';tick(15);await tracker.flush();assert.equal(packets.length,count+1);
 ctx.user={role:'child',id:'b',parent_id:'parent'};ctx.view='lesson';await tracker.flush();assert.equal(packets.at(-1).seconds,0);assert.notEqual(packets.at(-1).tab,packets[0].tab);
 ctx.user={role:'parent',id:'parent'};tick(15);await tracker.flush();assert.equal(packets.length,count+2);
 console.log('Activity client: guest/parent exclusion, visible/idle pause, bounded intervals, identity isolation passed.');
})().catch(e=>{console.error(e);process.exitCode=1;});
