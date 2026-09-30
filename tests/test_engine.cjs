const fs=require('fs'),vm=require('vm'),assert=require('assert'),path=require('path');
const root=path.join(__dirname,'..');
const fakeContext=new Proxy({measureText:s=>({width:s.length*9})},{get:(obj,p)=>obj[p]||(()=>{})});
const context={window:{},Image:class{constructor(){this.complete=true;this.naturalWidth=1536;}addEventListener(){}},performance,requestAnimationFrame:fn=>setTimeout(()=>fn(performance.now()),2),setTimeout,console};context.window=context.window;vm.createContext(context);vm.runInContext(fs.readFileSync(root+'/public/engine.js','utf8'),context);const P=context.window.PQC;
const copy=x=>JSON.parse(JSON.stringify(x));
(async()=>{
 assert.equal(P.parseCode('move right 2\nrepeat 3 up 1\nsay "Hello"').commands.length,3);
 for(const invalid of ['eval(1)','repeat 999 right 1','speed 0','move right 200','fetch("secret")'])assert.throws(()=>P.parseCode(invalid));
 const p=P.defaultProject();assert(P.validateProject(p));const bad=copy(p);bad.scenes[0].players[0].avatar=999;assert.throws(()=>P.validateProject(bad));
 const canvas={getContext:()=>fakeContext,addEventListener(){},getBoundingClientRect:()=>({left:0,top:0,width:800,height:450})};
 let latest;const stage=new P.Stage(canvas,p,r=>latest=r);p.speed=10;p.scenes[0].program=[{op:'right',value:6,target:1}];await stage.run();assert.equal(stage.score,3);assert(stage.won);stage.reset();assert.equal(stage.score,0);assert(!stage.won);
 p.scenes[0].hazards=[{x:170,y:345}];p.scenes[0].program=[{op:'right',value:2,target:1}];await stage.run();assert(stage.lost);p.scenes[0].hazards=[];
 p.scenes[0].program=[{op:'next',value:0,target:1}];p.scenes[1].program=[{op:'say',value:'The end!',target:1}];p.scene=0;await stage.run();assert.equal(p.scene,1);assert.equal(stage.runtime.players[0].speech,'The end!');
 p.scene=0;p.scenes[0].trigger='tap';p.scenes[0].program=[{op:'say',value:'Tapped!',target:1}];await stage.run();assert(stage.armed);assert.equal(stage.runtime.players[0].speech,'');stage.pointer({clientX:110,clientY:345});await new Promise(r=>setTimeout(r,750));assert.equal(stage.runtime.players[0].speech,'Tapped!');
 p.scene=0;p.scenes[0].trigger='start';p.scenes[0].program=[{op:'wait',value:5,target:1},{op:'say',value:'Never',target:1}];const running=stage.run();stage.stop();await running;assert.notEqual(stage.runtime.players[0].speech,'Never');stage.destroy();
 console.log('Interpreter: parsing, limits, collection, hazards, reset, scene changes, tap events and cancellation passed.');
})().catch(e=>{console.error(e);process.exitCode=1;});
