/* State/action regressions with a simulated DOM. Not a browser/layout test. */
const fs=require('fs'),vm=require('vm'),assert=require('assert'),path=require('path');
const root=path.join(__dirname,'..'),DATA=JSON.parse(fs.readFileSync(root+'/public/curriculum.json'));
function setup(){
 const elements=new Map(),storage=new Map();const element=s=>{if(!elements.has(s))elements.set(s,{innerHTML:'',textContent:'',value:'',checked:false,disabled:false,open:false,dataset:{},style:{},scrollTo(){},classList:{add(){},remove(){},toggle(){}},showModal(){this.open=true;},close(){this.open=false;},getBoundingClientRect(){return {width:80};}});return elements.get(s);};
 const saved={getItem:k=>storage.get(k)||null,setItem:(k,v)=>storage.set(k,v),removeItem:k=>storage.delete(k)};
 const context={console,window:{addEventListener(){},PQC_BOOTSTRAP:DATA,innerWidth:1200},document:{querySelector:element,querySelectorAll:()=>[],addEventListener(){}},Image:class{},sessionStorage:saved,localStorage:saved,setTimeout:()=>1,clearTimeout(){},confirm:()=>true,structuredClone,URL,Blob};
 vm.createContext(context);vm.runInContext(fs.readFileSync(root+'/public/engine.js','utf8'),context);context.PQC=context.window.PQC;
 vm.runInContext(fs.readFileSync(root+'/public/app.js','utf8').replace(/start\(\);\s*$/,''),context);
 const run=s=>vm.runInContext(s,context);run('curriculum=window.PQC_BOOTSTRAP;render=()=>{};toast=(text)=>{window.lastToast=text};');return {context,storage,element,run};
}
(async()=>{
 let t=setup();
 t.run(`user={id:'child-a',role:'child',path:'story',theme:'royal',avatar:0};state.path='story';state.notes['story-1']='My unsynced idea';persist();`);
 let draft=JSON.parse(t.storage.get('pqc-child-a'));assert(draft.dirty);assert.equal(draft.payload.notes['story-1'],'My unsynced idea');
 t.run(`api=async(path)=>path==='session'?{user:{id:'child-a',role:'child',path:'story',theme:'royal',avatar:0}}:{revision:0,payload:{schema:1,path:'story',notes:{},projects:{}}};`);
 await t.run('start()');assert.equal(t.run(`state.notes['story-1']`),'My unsynced idea');assert(t.run('dirty'));assert(!t.run('savingConflict'));
 t=setup();t.storage.set('pqc-child-a',JSON.stringify({revision:0,dirty:true,payload:{schema:1,path:'story',projects:{},notes:{'story-1':'Older local draft'}}}));
 t.run(`api=async(path)=>path==='session'?{user:{id:'child-a',role:'child',path:'story',theme:'royal',avatar:0}}:{revision:3,payload:{schema:1,path:'story',projects:{},notes:{}}};`);await t.run('start()');assert(t.run('savingConflict'));assert.equal(t.run(`state.notes['story-1']`),'Older local draft');t.run('persist()');assert.equal(JSON.parse(t.storage.get('pqc-child-a')).revision,0);await t.run('start()');assert(t.run('savingConflict'));
 // Stage reset and starting a fresh program are distinct, reversible actions.
 t=setup();t.run(`state.path='story';project().scenes[0].program=[{op:'right',value:2,target:1}];project().scenes[0].code='move right 2';stage={reset(){},stop(){}};`);
 await t.run(`handleAction('reset')`);assert.equal(t.run('project().scenes[0].program.length'),1);
 await t.run(`handleAction('start-over')`);assert.equal(t.run('project().scenes[0].program.length'),0);assert.equal(t.run('project().scenes[0].code'),'');assert(t.run('canUndoStartOver()'));
 await t.run(`handleAction('undo-start-over')`);assert.equal(t.run('project().scenes[0].program.length'),1);assert.equal(t.run('project().scenes[0].code'),'move right 2');
 await t.run(`handleAction('start-over')`);await t.run(`handleAction('add-block','say')`);assert(!t.run('canUndoStartOver()'));await t.run(`handleAction('undo-start-over')`);assert.equal(t.run("project().scenes[0].program[0].op"),'say');
 t.run(`project().scene=1;project().scenes[1].code='say "scene two"';`);await t.run(`handleAction('start-over')`);assert.equal(t.run("project().scenes[0].program[0].op"),'say');await t.run(`handleAction('undo-start-over')`);assert.equal(t.run('project().scenes[1].code'),'say "scene two"');
 // Successful save clears the pending draft and advances its revision.
 t=setup();t.run(`user={id:'child-a',role:'child'};state.path='story';dirty=true;api=async()=>({revision:1});`);await t.run('saveOnline()');draft=JSON.parse(t.storage.get('pqc-child-a'));assert.equal(draft.revision,1);assert(!draft.dirty);
 t=setup();await t.run(`handleAction('path','story')`);t.run(`project().title='My own game';project().scenes[0].code='say "My words"';`);await t.run(`handleAction('theme','space')`);assert.equal(t.run('project().title'),'My own game');assert.equal(t.run('project().scenes[0].code'),'say "My words"');
 assert.equal(t.run('project().scenes[0].program.length'),0);
 for(const op of t.context.PQC.OPS){await t.run(`handleAction('add-block',${JSON.stringify(op)})`);}assert.equal(t.run('project().scenes[0].program.length'),13);assert(t.run('PQC.validateProject(project())'));
 await t.run(`handleAction('later',null,{dataset:{index:'0'}})`);await t.run(`handleAction('earlier',null,{dataset:{index:'1'}})`);await t.run(`handleAction('remove-block',null,{dataset:{index:'0'}})`);assert.equal(t.run('project().scenes[0].program.length'),12);
 await t.run(`handleAction('path','game')`);await t.run(`handleAction('path','story')`);assert.equal(t.run('project().title'),'My own game');
 for(const path of ['story','game','dev'])for(let day=1;day<=30;day++){t.run(`state.path=${JSON.stringify(path)};activeDay=${day};`);await t.run(`handleAction('starter')`);assert(t.run('PQC.validateProject(project())'));}
 t=setup();t.run(`api=async()=>({user:null,sessionState:'missing-cookie'});`);await assert.rejects(t.run(`adoptUser({user:{id:'parent-a',role:'parent'}})`),/cookie did not reach/);assert.equal(t.run('user'),null);
 t=setup();t.run(`api=async()=>({user:null,sessionState:'unrecognized-session'});`);await assert.rejects(t.run(`adoptUser({user:{id:'parent-a',role:'parent'}})`),/session was not recognized/);assert.equal(t.run('user'),null);
 t=setup();t.run(`api=async()=>({user:{id:'parent-other',role:'parent'}});`);await assert.rejects(t.run(`adoptUser({user:{id:'parent-a',role:'parent'}})`),/could not be verified/);assert.equal(t.run('user'),null);
 console.log('State/actions: draft recovery/conflicts, save acknowledgement, path/theme preservation, all 13 block additions, reorder/delete and 90 starter applications passed (simulated DOM).');
})().catch(e=>{console.error(e);process.exitCode=1;});
