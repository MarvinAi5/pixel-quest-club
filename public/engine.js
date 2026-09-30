/* A bounded interpreter, never eval: children's commands cannot access the page or server. */
(function(global){
'use strict';
const AVATAR_X=[160,405,650,895,1140,1390],AVATAR_Y=[208,387,572,749,926];
const THEMES={royal:{name:'Royal Castle',file:'assets/royal.webp',item:'💎',hazard:'🌿',player:13,friend:12,treasure:'gems'},space:{name:'Space Adventure',file:'assets/space.webp',item:'⚡',hazard:'☄',player:21,friend:19,treasure:'crystals'},halloween:{name:'Halloween',file:'assets/halloween.webp',item:'🎃',hazard:'🕸',player:24,friend:27,treasure:'pumpkins'}};
const images={};
function image(src){if(!images[src]){images[src]=new Image();images[src].src=(global.PQC_ASSETS&&global.PQC_ASSETS[src])||src;}return images[src];}
function avatarStyle(index,size=80){const x=AVATAR_X[index%6],y=AVATAR_Y[Math.floor(index/6)],scale=size/200;return `background-size:${1536*scale}px ${1024*scale}px;background-position:${-(x-100)*scale}px ${-(y-100)*scale}px;`;}
function defaultScene(){return {trigger:'start',program:[{op:'right',value:2,target:1},{op:'say',value:'Hello!',target:1}],code:'move right 2\nsay "Hello!"',players:[{x:110,y:345,avatar:null},{x:650,y:345,avatar:null}],items:[{x:230,y:345},{x:350,y:345},{x:470,y:345}],hazards:[]};}
function defaultProject(theme='royal'){return {schema:1,title:'My October creation',theme,mode:'blocks',target:3,speed:3,sound:true,scene:0,scenes:[defaultScene(),{...defaultScene(),program:[{op:'say',value:'The end!',target:1}],code:'say "The end!"'}]};}
const OPS=['right','left','up','down','wait','say','repeat','sound','hide','show','next','message','ifwin'];
function validateProject(p){
 if(!p||p.schema!==1||!THEMES[p.theme]||!Array.isArray(p.scenes)||p.scenes.length!==2)throw Error('Choose a Pixel Quest Club project file.');
 if(typeof p.title!=='string'||p.title.length>80||!['blocks','code'].includes(p.mode)||!Number.isFinite(p.speed)||p.speed<1||p.speed>10||!Number.isInteger(p.target)||p.target<1||p.target>20||![0,1].includes(p.scene))throw Error('Project settings are invalid.');
 for(const s of p.scenes){
  if(!['start','tap','message','controls'].includes(s.trigger)||!Array.isArray(s.program)||s.program.length>80||typeof s.code!=='string'||s.code.length>5000||!Array.isArray(s.players)||s.players.length!==2||!Array.isArray(s.items)||s.items.length>20||!Array.isArray(s.hazards)||s.hazards.length>10)throw Error('Project scene is too large or invalid.');
  for(const obj of [...s.players,...s.items,...s.hazards])if(!Number.isFinite(obj.x)||!Number.isFinite(obj.y)||obj.x<30||obj.x>770||obj.y<50||obj.y>410)throw Error('A stage position is invalid.');
  for(const player of s.players)if(player.avatar!==null&&(!Number.isInteger(player.avatar)||player.avatar<0||player.avatar>29))throw Error('Invalid character.');
  for(const b of s.program){if(!OPS.includes(b.op)||![1,2].includes(b.target))throw Error('A block is invalid.');if(['say','ifwin'].includes(b.op)){if(typeof b.value!=='string'||b.value.length>100)throw Error('Keep speech below 100 characters.');}else if(!Number.isFinite(b.value)||b.value<0||b.value>20)throw Error('Use values between 0 and 20.');if(b.op==='repeat'&&(!['right','left','up','down'].includes(b.direction)||!Number.isInteger(b.count)||b.count<1||b.count>10))throw Error('Use a valid repeat.');}
 }
 return p;
}
function parseCode(text){
 const commands=[];let speed=null,target=null;
 if(text.length>5000)throw Error('Keep practice code under 5,000 characters.');
 text.split('\n').forEach((raw,i)=>{
  const line=raw.trim();if(!line||line.startsWith('#'))return;
  const fail=()=>{throw Error(`Line ${i+1}: ${line}. Try move right 2, repeat 3 right 1, or say "Hello!".`);};
  let m;
  if((m=line.match(/^move (right|left|up|down) (\d+(?:\.\d+)?)$/)))commands.push({op:m[1],value:+m[2],target:1});
  else if((m=line.match(/^repeat (\d+) (right|left|up|down) (\d+(?:\.\d+)?)$/)))commands.push({op:'repeat',count:+m[1],direction:m[2],value:+m[3],target:1});
  else if((m=line.match(/^(say|ifwin)\s+(.+)$/))){let v=m[2];if(v.startsWith('"')&&v.endsWith('"'))v=v.slice(1,-1);commands.push({op:m[1],value:v,target:1});}
  else if((m=line.match(/^wait (\d+(?:\.\d+)?)$/)))commands.push({op:'wait',value:+m[1],target:1});
  else if((m=line.match(/^(speed|target) (\d+)$/))){if(m[1]==='speed')speed=+m[2];else target=+m[2];}
  else if(['sound','next','message','hide','show'].includes(line))commands.push({op:line,value:0,target:1});
  else fail();
 });
 if(commands.length>80)throw Error('Use no more than 80 commands.');
 for(const b of commands){if(['say','ifwin'].includes(b.op)&&b.value.length>100)throw Error('Keep speech under 100 characters.');if(typeof b.value==='number'&&(b.value<0||b.value>20))throw Error('Use values from 0 to 20.');if(b.op==='repeat'&&(b.count<1||b.count>10))throw Error('Repeat from 1 to 10 times.');}
 if(speed!==null&&(speed<1||speed>10))throw Error('Speed must be 1–10.');if(target!==null&&(target<1||target>20))throw Error('Target must be 1–20.');
 return {commands,speed,target};
}
class Stage {
 constructor(canvas,project,notify){this.canvas=canvas;this.ctx=canvas.getContext('2d');canvas.width=800;canvas.height=450;this.project=project;this.notify=notify;this.token=0;this.score=0;this.running=false;this.lost=false;this.won=false;this.layout=null;this.runtime=null;this.reset();this.frame=null;this.pendingFrame=false;this.draw=this.draw.bind(this);this.canvas.addEventListener('pointerdown',e=>this.pointer(e));image('assets/avatars.webp').addEventListener('load',()=>this.paint());this.paint();}
 current(){return this.project.scenes[this.project.scene];}
 reset(){this.stop();this.score=0;this.lost=false;this.won=false;this.project.scene=Math.min(1,Math.max(0,this.project.scene));this.loadScene();this.report('Ready. Press Run.');this.paint();}
 loadScene(){const s=this.current();this.runtime={players:s.players.map(p=>({...p,visible:true,speech:''})),items:s.items.map(p=>({...p,collected:false})),hazards:s.hazards};}
 report(text,error=false){this.notify?.({text,error,score:this.score,target:this.project.target,scene:this.project.scene,lost:this.lost,won:this.won});}
 paint(){if(!this.pendingFrame){this.pendingFrame=true;requestAnimationFrame(()=>{this.pendingFrame=false;this.draw();});}}
 draw(){
  if(!this.runtime)return;const ctx=this.ctx,theme=THEMES[this.project.theme],bg=image(theme.file);ctx.clearRect(0,0,800,450);ctx.fillStyle='#bddde2';ctx.fillRect(0,0,800,450);if(bg.complete&&bg.naturalWidth)ctx.drawImage(bg,0,0,800,450);else bg.onload=()=>this.paint();
  ctx.fillStyle='#18223b25';ctx.fillRect(0,285,800,165);
  ctx.textAlign='center';ctx.textBaseline='middle';ctx.font='40px system-ui';for(const p of this.runtime.items)if(!p.collected)ctx.fillText(theme.item,p.x,p.y);for(const h of this.runtime.hazards)ctx.fillText(theme.hazard,h.x,h.y);
  const atlas=image('assets/avatars.webp');this.runtime.players.forEach((p,i)=>{
   if(!p.visible)return;const av=p.avatar??(i===0?theme.player:theme.friend),cx=AVATAR_X[av%6],cy=AVATAR_Y[Math.floor(av/6)];ctx.save();ctx.beginPath();ctx.arc(p.x,p.y,35,0,Math.PI*2);ctx.clip();if(atlas.complete&&atlas.naturalWidth)ctx.drawImage(atlas,cx-100,cy-100,200,200,p.x-35,p.y-35,70,70);ctx.restore();
   if(p.speech){const lines=this.wrap(p.speech,210),w=230,h=lines.length*24+20,x=Math.min(565,Math.max(5,p.x-w/2)),y=Math.max(8,p.y-65-h);ctx.fillStyle='#fffdf5';ctx.strokeStyle='#18223b';ctx.lineWidth=2;ctx.beginPath();ctx.roundRect?ctx.roundRect(x,y,w,h,12):ctx.rect(x,y,w,h);ctx.fill();ctx.stroke();ctx.fillStyle='#18223b';ctx.font='20px Trebuchet MS';lines.forEach((line,j)=>ctx.fillText(line,x+w/2,y+22+j*24));}
  });
  if(this.won||this.lost){ctx.fillStyle=this.won?'#e8fff0ed':'#fff0d3ed';ctx.fillRect(200,15,400,52);ctx.fillStyle='#18223b';ctx.font='bold 24px Trebuchet MS';ctx.fillText(this.won?'Goal reached!':'Try another route',400,42);}
 }
 wrap(text,width){const ctx=this.ctx;ctx.font='20px Trebuchet MS';const lines=[];let line='';for(const word of text.split(/\s+/)){if(ctx.measureText(line+' '+word).width>width&&line){lines.push(line);line=word;}else line+=(line?' ':'')+word;}lines.push(line);return lines.slice(0,4);}
 stop(){this.token++;this.running=false;this.armed=false;this.busy=false;}
 async run(){this.reset();this.running=true;this.armed=true;if(this.current().trigger==='tap'){this.report('Tap Companion 1 to start.');return;}if(this.current().trigger==='message'){this.report('This scene is waiting for a message from the other scene.');return;}await this.executeScene(this.token,0);if(this.current().trigger==='controls'&&!this.lost){this.running=true;this.report('Use the direction buttons or arrow keys.');}}
 async executeScene(token,depth){if(depth>8){this.report('Too many scene changes. Remove a looping Next scene or Message command.',true);this.stop();return;}const s=this.current();let commands=s.program;
  if(this.project.mode==='code'){const parsed=parseCode(s.code);commands=parsed.commands;if(parsed.speed!==null)this.project.speed=parsed.speed;if(parsed.target!==null)this.project.target=parsed.target;}
  for(let i=0;i<commands.length;i++){if(token!==this.token||this.lost)return;const b=commands[i];this.report(`Command ${i+1} of ${commands.length}`);const changed=await this.command(b,token,depth);if(changed)return;}
  if(token===this.token){this.report(this.won?'Goal reached! Reset to play again.':'Sequence finished. Try changing a command.');if(s.trigger!=='controls')this.running=false;}
 }
 async command(b,token,depth){const p=this.runtime.players[(b.target||1)-1];if(['right','left','up','down'].includes(b.op))await this.move(b.op,b.value,b.target,token);else if(b.op==='repeat'){for(let i=0;i<b.count;i++){if(token!==this.token||this.lost)break;await this.move(b.direction,b.value,b.target,token);}}else if(b.op==='wait')await this.delay(Math.min(5000,b.value*1000),token);else if(b.op==='say'){p.speech=b.value;this.paint();await this.delay(650,token);}else if(b.op==='ifwin'){if(this.score>=this.project.target){p.speech=b.value;this.paint();await this.delay(650,token);}}else if(b.op==='sound')this.beep();else if(b.op==='hide'||b.op==='show'){p.visible=b.op==='show';this.paint();}else if(b.op==='next'||b.op==='message'){
   const other=1-this.project.scene;if(b.op==='message'&&this.project.scenes[other].trigger!=='message'){this.report('Choose Message as the other scene’s trigger.',true);return false;}this.project.scene=other;this.loadScene();this.paint();await this.executeScene(token,depth+1);return true;
  }return false;
 }
 delay(ms,token){return new Promise(resolve=>{const started=performance.now();const tick=()=>{if(token!==this.token||performance.now()-started>=ms)resolve();else setTimeout(tick,30);};tick();});}
 move(dir,steps,target=1,token=this.token){const p=this.runtime.players[target-1],dx=dir==='right'?1:dir==='left'?-1:0,dy=dir==='down'?1:dir==='up'?-1:0,x=p.x,y=p.y,toX=Math.max(35,Math.min(765,x+dx*60*steps)),toY=Math.max(60,Math.min(410,y+dy*60*steps));const duration=Math.max(80,180*steps*(4/this.project.speed)),start=performance.now();return new Promise(resolve=>{const animate=now=>{if(token!==this.token||this.lost){resolve();return;}const f=Math.min(1,(now-start)/duration);p.x=x+(toX-x)*f;p.y=y+(toY-y)*f;if(target===1)this.contacts();this.paint();if(f<1)requestAnimationFrame(animate);else resolve();};requestAnimationFrame(animate);});}
 contacts(){const p=this.runtime.players[0];for(const item of this.runtime.items)if(!item.collected&&Math.hypot(item.x-p.x,item.y-p.y)<35){item.collected=true;this.score++;this.beep();this.report('Treasure collected!');}for(const h of this.runtime.hazards)if(Math.hypot(h.x-p.x,h.y-p.y)<32){this.lost=true;this.running=false;this.report('You touched a hazard. Reset and try a different route.');}if(this.score>=this.project.target&&!this.lost){this.won=true;this.report('Goal reached!');}}
 async control(direction){if(this.layout||!this.running||this.current().trigger!=='controls'||this.busy||this.lost||this.won)return;this.busy=true;await this.move(direction,.5,1,this.token);this.busy=false;this.report(this.lost?'Try another route.':this.won?'Goal reached!':'Keep exploring.');}
 pointer(e){const rect=this.canvas.getBoundingClientRect(),x=(e.clientX-rect.left)/rect.width*800,y=(e.clientY-rect.top)/rect.height*450;
  if(this.layout){const s=this.current(),p={x:Math.round(Math.max(35,Math.min(765,x))),y:Math.round(Math.max(60,Math.min(410,y)))};
   if(this.layout.startsWith('player'))Object.assign(s.players[+this.layout.slice(-1)-1],p);
   else if(this.layout==='erase'){s.items=s.items.filter(o=>Math.hypot(o.x-x,o.y-y)>40);s.hazards=s.hazards.filter(o=>Math.hypot(o.x-x,o.y-y)>40);}
   else{const array=this.layout==='treasure'?s.items:s.hazards;if(array.length>=(this.layout==='treasure'?20:10)){this.report('The stage is full. Erase an item first.',true);return;}array.push(p);}
   this.loadScene();this.paint();this.onEdit?.();return;
  }
  const p=this.runtime.players[0];if(this.armed&&this.current().trigger==='tap'&&!this.busy&&Math.hypot(p.x-x,p.y-y)<50){this.busy=true;this.executeScene(this.token,0).catch(err=>this.report(err.message,true)).finally(()=>this.busy=false);}
 }
 beep(){if(!this.project.sound)return;try{const AC=window.AudioContext||window.webkitAudioContext;if(!AC)return;this.audio??=new AC();if(this.audio.state==='suspended')this.audio.resume();const o=this.audio.createOscillator(),g=this.audio.createGain();o.connect(g);g.connect(this.audio.destination);o.frequency.value=660;g.gain.setValueAtTime(.06,this.audio.currentTime);g.gain.exponentialRampToValueAtTime(.001,this.audio.currentTime+.12);o.start();o.stop(this.audio.currentTime+.13);}catch{}}
 destroy(){this.stop();this.audio?.close();}
}
global.PQC={THEMES,Stage,avatarStyle,defaultProject,validateProject,parseCode,OPS};
})(window);
