/* Activity outcomes through the actual deployed UI. No injected lesson solutions. */
const {chromium}=require('playwright'),assert=require('node:assert/strict'),fs=require('fs'),path=require('path'),os=require('os'),{spawn}=require('child_process');
const ROOT=path.resolve(__dirname,'..'),OUT=path.join(ROOT,'qa-artifacts'),DATA=JSON.parse(fs.readFileSync(ROOT+'/public/curriculum.json'));fs.mkdirSync(OUT,{recursive:true});
const dir=fs.mkdtempSync(path.join(os.tmpdir(),'pqc-lessons-')),port=8099,url='http://127.0.0.1:'+port;
const server=spawn('python3',['server.py','--port',String(port)],{cwd:ROOT,env:{...process.env,PQC_DATA_DIR:dir,PQC_PUBLIC_DIR:ROOT+'/dist',PQC_SECURE_COOKIES:'0'},stdio:'ignore'});
const report={status:'running',lessons:[],errors:[],scope:'Browser tasks executed through UI; external recipes reviewed here and executed by separate engine tests. Human explanations, family playtests and hardware tasks are not automated.'};let browser,page;
const click=async(a,v)=>page.locator(`[data-action="${a}"]${v===undefined?'':`[data-value="${v}"]`}`).filter({visible:true}).first().click();
async function run(){await click('run');await page.waitForFunction(()=>!stage.running&&!stage.busy||stage.current().trigger==='controls'&&stage.running);}
async function setting(id,value){await page.locator('summary').filter({hasText:'Scene settings'}).evaluate(e=>e.parentElement.open=true);await page.locator('#'+id).fill(String(value));await page.locator('#'+id).press('Tab');}
async function blocks(list){await click('clear-program');for(const b of list){await click('add-block',b.op);const row=page.locator('.block').last();if(['right','left','up','down','repeat','wait','say','ifwin'].includes(b.op))await row.locator('[data-block-field="value"]').fill(String(b.value));if(b.target)await row.locator('[data-block-field="target"]').selectOption(String(b.target));if(b.op==='repeat'){await row.locator('[data-block-field="direction"]').selectOption(b.direction);await row.locator('[data-block-field="count"]').fill(String(b.count));}}}
const b=(op,value=0,more={})=>({op,value,...more});
async function speech(n,text){await page.waitForFunction(([n,t])=>stage.runtime.players[n].speech===t,[n,text]);}
async function moveResult(x,y){const p=await page.evaluate(()=>stage.runtime.players[0]);assert(Math.abs(p.x-x)<1,`x ${p.x}, expected ${x}`);assert(Math.abs(p.y-y)<1,`y ${p.y}, expected ${y}`);}
async function tap(){const box=await page.locator('#stage').boundingBox();await page.locator('#stage').click({position:{x:110/800*box.width,y:345/450*box.height}});await page.waitForFunction(()=>!stage.running&&!stage.busy);}
async function directions(direction,n){for(let i=0;i<n;i++){await page.locator(`[data-direction="${direction}"]`).click();await page.waitForFunction(()=>!stage.busy);}}
async function exportImport(){const pending=page.waitForEvent('download');await click('download');const d=await pending;const file=path.join(dir,'roundtrip.json');await d.saveAs(file);const data=JSON.parse(fs.readFileSync(file));const cp=page.waitForEvent('filechooser');await click('import');await (await cp).setFiles(file);await page.waitForFunction(()=>document.querySelector('#toast').textContent==='Project opened.');assert.equal(await page.locator('#project-title').inputValue(),data.title);}
async function story(d){
 if(d===1){await page.locator('summary').filter({hasText:'Scene settings'}).evaluate(e=>e.parentElement.open=true);await page.locator('#character-1').selectOption('13');await run();await moveResult(170,345);}
 else if(d===2){await run();await moveResult(230,345);await page.locator('[data-block-field="value"]').fill('4');await run();await moveResult(350,345);}
 else if(d===3){await run();await moveResult(230,345);await speech(0,'Hello');}
 else if(d===4){await run();await moveResult(110,405);await blocks([b('up',1),b('down',1)]);await run();await moveResult(110,345);}
 else if(d===5){await run();await moveResult(230,345);await page.locator('[data-action="later"]').first().click();assert.equal(await page.locator('.block').first().getAttribute('data-op'),'right');await run();await speech(0,'Ready');}
 else if(d===6){await click('run');await speech(0,'Hello');await page.waitForTimeout(250);await speech(0,'Hello');await speech(0,'Goodbye');}
 else if(d===7){await blocks([b('right',1),b('say','My own story'),b('wait',.5)]);await run();await moveResult(170,345);await speech(0,'My own story');}
 else if(d===8){await run();await moveResult(290,345);await blocks([b('right',1),b('right',1),b('right',1)]);await run();await moveResult(290,345);}
 else if(d===9){await run();await moveResult(110,225);await page.locator('[data-block-field="count"]').fill('3');await run();await moveResult(110,165);}
 else if(d===10){await page.locator('[data-block-field="value"]').fill('A spooky greeting');await run();await speech(0,'A spooky greeting');}
 else if(d===11){await run();await speech(1,'Hello');await speech(0,'Hello back!');}
 else if(d===12||d===24){await click('run');assert.equal(await page.evaluate(()=>stage.runtime.players[0].speech),'');await tap();if(d===12)await speech(0,'You tapped me!');else assert.equal(await page.evaluate(()=>stage.runtime.players[1].visible),true);}
 else if(d===13){await run();await speech(0,'Hello');await page.locator('summary').filter({hasText:'Scene settings'}).evaluate(e=>e.parentElement.open=true);await page.locator('#sound').uncheck();await run();await speech(0,'Hello');}
 else if(d===14){await run();await speech(0,'Hello');await page.locator('.block[data-index="2"] [data-action="earlier"]').click();await page.locator('.block[data-index="1"] [data-action="earlier"]').click();await run();await speech(0,'Goodbye');}
 else if(d===15){await page.locator('#scene-select').selectOption('1');await blocks([b('say','Scene two')]);await run();await speech(0,'Scene two');await page.locator('#scene-select').selectOption('0');await run();await speech(0,'Welcome to Scene 1');}
 else if([16,17,23,29,30].includes(d)){await run();assert.equal(await page.locator('#scene-select').inputValue(),'1');await speech(d===17?1:0,d===17?'Hello back!':'The end!');if(d===29)await exportImport();if(d===30){await page.locator('#scene-select').selectOption('0');await page.locator('[data-block-field="count"]').fill('3');await run();await speech(0,'The end!');}}
 else if(d===18){await click('run');await page.waitForFunction(()=>stage.runtime.players[1].visible===false);await page.waitForFunction(()=>!stage.running);assert.equal(await page.evaluate(()=>stage.runtime.players[1].visible),true);}
 else if(d===19){await click('reset');await run();await speech(0,'Press Run to begin!');}
 else if(d===20){await blocks([b('say','Find a friend'),b('right',1),b('wait',.5)]);await run();await moveResult(170,345);}
 else if(d===21){await run();await speech(0,'Hello, friend!');await moveResult(170,345);}
 else if(d===22){await run();await moveResult(230,345);await speech(1,'I found you!');}
 else if(d===25){await run();await speech(0,'The end');}
 else if(d===26){await page.locator('[data-block-field="value"]').first().fill('Improved favorite');await run();await speech(0,'Improved favorite');}
 else if(d===27){await run();await moveResult(170,345);await page.locator('#quest-note').fill('QA observed: Run instructions are visible. Actual family playtest remains a human task.');}
 else if(d===28){await page.locator('[data-block-field="value"]').first().fill('Press Run to start');await run();await speech(0,'The end');}
 else throw Error('No authored activity '+d);
}
async function game(d){
 if(d===1){await run();await moveResult(230,345);}
 else if(d===2){await run();await moveResult(230,285);}
 else if(d===3){await run();await speech(0,'Started!');await page.locator('#trigger').selectOption('tap');await click('run');assert.equal(await page.evaluate(()=>stage.runtime.players[0].speech),'');await tap();await speech(0,'Started!');}
 else if(d===4){await run();assert.equal(await page.evaluate(()=>stage.score),3);await click('reset');assert.equal(await page.evaluate(()=>stage.score),0);await setting('target',5);await run();assert.equal(await page.evaluate(()=>stage.won),false);}
 else if(d===5){await run();assert.equal(await page.evaluate(()=>stage.score),1);}
 else if(d===6){await run();await speech(0,'You win');await blocks([b('up',1),b('ifwin','You win')]);await run();assert.equal(await page.evaluate(()=>stage.runtime.players[0].speech),'');}
 else if(d===7){await run();assert.equal(await page.evaluate(()=>stage.score),3);await speech(0,'You win');}
 else if(d===8){await run();await moveResult(290,345);await blocks([b('right',1),b('right',1),b('right',1)]);await run();await moveResult(290,345);}
 else if(d===9){await setting('speed',2);let t=Date.now();await run();const slow=Date.now()-t;await moveResult(470,345);await setting('speed',6);t=Date.now();await run();const fast=Date.now()-t;assert(fast<slow);await moveResult(470,345);}
 else if(d===10){await run();await directions('right',1);await moveResult(140,345);await page.locator('#stage').focus();await page.keyboard.press('ArrowUp');await page.waitForFunction(()=>!stage.busy);await moveResult(140,315);}
 else if(d===11){await run();await directions('right',6);assert.equal(await page.evaluate(()=>stage.lost),true);await click('reset');await run();await directions('up',2);await directions('right',8);assert.equal(await page.evaluate(()=>stage.lost),false);}
 else if(d===12){await run();await directions('right',12);assert.equal(await page.evaluate(()=>stage.won),true);await click('reset');assert.equal(await page.evaluate(()=>stage.score),0);assert.equal(await page.evaluate(()=>stage.runtime.items.filter(x=>!x.collected).length),3);await run();await directions('right',12);assert.equal(await page.evaluate(()=>stage.won),true);}
 else if(d===13){await run();await speech(0,'Collect three treasures. Use the direction buttons.');assert.equal(await page.evaluate(()=>stage.runtime.hazards.length),1);}
 else if(d===14){await run();await directions('up',2);assert.equal(await page.evaluate(()=>stage.score),0);await click('reset');await run();await directions('right',6);assert.equal(await page.evaluate(()=>stage.lost),true);await click('reset');await run();await directions('right',4);await directions('up',2);await directions('right',8);await directions('down',2);await directions('left',4);assert.equal(await page.evaluate(()=>stage.won),true);await click('reset');assert.equal(await page.evaluate(()=>stage.score),0);}
}
async function dev(d){
 if(d===1){await run();await moveResult(230,345);await page.locator('#code').fill('move right 3');await run();await moveResult(290,345);}
 else if(d===2){let t=Date.now();await run();const slow=Date.now()-t;await page.locator('#code').fill('speed 6\nmove right 4');t=Date.now();await run();assert(Date.now()-t<slow);await moveResult(350,345);assert.match(await page.locator('.lesson-panel .guide-code').innerText(),/var speed/);}
 else if(d===3){await run();await speech(0,'Hello');await run();await speech(0,'Hello');assert.match(await page.locator('.lesson-panel .guide-code').innerText(),/func greet/);}
 else if(d===4){await run();await speech(0,'You win');await page.locator('#code').fill('target 1\nmove up 1\nifwin "You win"');await run();assert.equal(await page.evaluate(()=>stage.runtime.players[0].speech),'');}
 else if(d===5){await run();await moveResult(290,345);await page.locator('#code').fill('move right 1\nmove right 1\nmove right 1');await run();await moveResult(290,345);assert.match(await page.locator('.lesson-panel .guide-code').innerText(),/range\(3\)/);}
 else if(d===6){await page.locator('#code').fill('moove right 2');await run();assert.match(await page.locator('#run-status').innerText(),/Line 1/);await page.locator('#code').fill('move right 2');await run();await moveResult(230,345);}
 else if(d===7){await run();assert.equal(await page.evaluate(()=>stage.score),3);await speech(0,'You win');}
}
(async()=>{
 for(let i=0;i<80;i++){try{if((await fetch(url+'/api/session')).ok)break;}catch{}await new Promise(r=>setTimeout(r,100));}
 browser=await chromium.launch();page=await browser.newPage({viewport:{width:1440,height:1100},acceptDownloads:true});page.on('dialog',d=>d.accept());page.on('pageerror',e=>report.errors.push(e.message));await page.goto(url);await page.getByRole('heading',{name:'What would you like to make?'}).waitFor();
 for(const pathName of ['story','game','dev']){
  await click('path',pathName);
  for(const l of DATA.lessons.filter(l=>l.path===pathName)){
   await click('day',l.day);const item={id:l.id,title:l.title,mode:l.mode,checks:[]};report.lessons.push(item);
   await page.locator('summary').filter({hasText:'Need a hint?'}).click();await page.locator('summary').filter({hasText:'Extra challenge'}).click();await page.locator('summary').filter({hasText:'Walk through this activity'}).click();assert(l.success&&l.walkthrough.length);item.checks.push('Hint, challenge, walkthrough and expected result visible');
   for(const theme of ['royal','space','halloween']){await click('theme',theme);await page.waitForFunction(()=>Array.from(document.images).every(i=>i.complete&&i.naturalWidth>0));}
   if(l.mode==='browser'){
    await click('practice');await click('starter');if(pathName==='story')await story(l.day);else if(pathName==='game')await game(l.day);else await dev(l.day);item.checks.push('Authored activity actions and expected runtime outcome passed');
    await page.locator('#quest-note').fill('QA: '+l.success.slice(0,360));for(let i=0;i<3;i++){await page.locator('#step-'+i).check();assert.equal(await page.locator('#complete').isEnabled(),false);}await page.locator('#explained').check();await click('complete');assert.match(await page.locator('#complete').innerText(),/completed/);await click('month');await click('day',l.day);assert.match(await page.locator('#complete').innerText(),/completed/);item.checks.push('Completion gating and return-visit progress passed');
    if([1,12,17,30].includes(l.day))await page.screenshot({path:OUT+'/'+l.id+'.png',fullPage:true});
   }else{
    await click('tool-guide');assert((await page.locator('#dialog .guide-code').first().innerText()).trim()===l.guideCode.trim());const expected=l.mode==='scratch'?l.checkpoint:'starter-godot';const href=await page.locator(`#dialog a[download]`).filter({hasText:l.mode==='scratch'?'Scratch checkpoint':'Godot reference'}).getAttribute('href');const r=await page.request.get(new URL(href,url).href);assert.equal(r.status(),200);assert((await r.body()).length>100);await click('close-dialog');item.checks.push('Lesson-specific tool recipe and downloadable reference work');item.status='external-engine-check-required';
   }
   item.status ||= 'browser-activity-passed';console.log('PASS '+l.id+' '+item.status);await click('month');
  }
  await click('choose');
 }
 await page.waitForTimeout(200);
 const cdp=await page.context().newCDPSession(page);await cdp.send('HeapProfiler.collectGarbage');const proto=await cdp.send('Runtime.evaluate',{expression:'PQC.Stage.prototype',objectGroup:'stage-retention-qa'});const objects=await cdp.send('Runtime.queryObjects',{prototypeObjectId:proto.result.objectId,objectGroup:'stage-retention-qa'});const count=await cdp.send('Runtime.callFunctionOn',{objectId:objects.objects.objectId,functionDeclaration:'function(){return this.length;}',returnByValue:true});report.retainedStagesAfterCalendar=count.result.value;assert(count.result.value<=2,'Old lesson stages are retained in memory: '+count.result.value);await cdp.send('Runtime.releaseObjectGroup',{objectGroup:'stage-retention-qa'});await cdp.detach();
 assert.deepEqual(report.errors,[]);assert.equal(report.lessons.length,90);report.status='passed';
})().catch(async e=>{report.status='failed';report.failure=e.stack;console.error(e);if(page)await page.screenshot({path:OUT+'/curriculum-failure.png',fullPage:true}).catch(()=>{});process.exitCode=1;}).finally(async()=>{fs.writeFileSync(OUT+'/curriculum-browser-results.json',JSON.stringify(report,null,2));await browser?.close();server.kill();fs.rmSync(dir,{recursive:true,force:true});});
