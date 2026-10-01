/* Real Chromium; only disposable local accounts, never production children. */
const assert=require('node:assert/strict'),fs=require('node:fs'),os=require('node:os'),path=require('node:path'),{spawn,execFileSync}=require('node:child_process');
let chromium;try{({chromium}=require('playwright'));}catch{({chromium}=require(process.env.CODEX_PRIMARY_RUNTIME_NODE_MODULES+'/playwright'));}
const root=path.resolve(__dirname,'..'),out=path.join(root,'qa-artifacts'),data=fs.mkdtempSync(path.join(os.tmpdir(),'pqc-family-')),url='http://127.0.0.1:8097';fs.mkdirSync(out,{recursive:true});
const proc=spawn('python3',['server.py','--port','8097'],{cwd:root,env:{...process.env,PQC_DATA_DIR:data,PQC_PUBLIC_DIR:path.join(root,'dist'),PQC_PARENT_SIGNUP:'1',PQC_PARENT_INVITE:'qa-family',PQC_SECURE_COOKIES:'0',PQC_OWNER_USERNAME:'qa-owner',PQC_CF_ZONE_ID:'',PQC_CF_ANALYTICS_TOKEN:''},stdio:'ignore'});
let browser;const report={checks:[],errors:[]};
async function call(context,path,body){const r=body===undefined?await context.request.get(url+'/api/'+path):await context.request.post(url+'/api/'+path,{data:body});assert(r.ok(),await r.text());return r.json();}
(async()=>{
 for(let i=0;i<80;i++){try{if((await fetch(url+'/api/session')).ok)break;}catch{}await new Promise(r=>setTimeout(r,100));}
 browser=await chromium.launch();const owner=await browser.newContext({viewport:{width:1440,height:1050}}),kid=await browser.newContext(),other=await browser.newContext();
 await call(owner,'register',{role:'parent',username:'qa-owner',secret:'disposable-parent-password',invite:'qa-family'});
 const created=await call(owner,'children',{secret:'123456',path:'story',avatar:13});
 await call(kid,'login',{username:created.child.username,secret:'123456'});
 await call(other,'register',{role:'parent',username:'qa-other',secret:'disposable-parent-password',invite:'qa-family'});
 const childPage=await kid.newPage();childPage.on('pageerror',e=>report.errors.push(e.message));await childPage.goto(url);await childPage.locator('[data-action="day"][data-value="1"]').first().click();
 // Exercise the real collector at normal server time; first interval establishes baseline.
 await childPage.evaluate(()=>window.familyPackets=[]);
 await childPage.route('**/api/activity',async route=>{await childPage.evaluate(body=>window.familyPackets.push(body),route.request().postDataJSON());await route.continue();});
 await childPage.waitForFunction(()=>window.familyPackets.length>=2,null,{timeout:40000});
 const actual=(await call(owner,'children')).children[0];assert(actual.activity.periods.today.seconds>=10);assert.equal(actual.activity.lastLesson,'story-1');
 report.checks.push('Real browser visible lesson collector and server time accumulation');
 for(let i=0;i<3;i++)await childPage.locator('#step-'+i).check();await childPage.locator('#explained').check();await childPage.locator('#complete').click();await childPage.locator('[data-action="save-now"]').click();await childPage.waitForFunction(()=>document.querySelector('#save-status').textContent==='Saved online');
 // Add explicit fixture days for readable multi-day period UI; not measured learner activity.
 execFileSync('python3',['-c',`import sqlite3,sys,datetime; from zoneinfo import ZoneInfo; c=sqlite3.connect(sys.argv[1]); today=datetime.datetime.now(ZoneInfo('America/Denver')).date(); c.execute('INSERT OR REPLACE INTO activity_daily VALUES(?,?,?)',(sys.argv[2],today.isoformat(),900)); c.execute('INSERT OR REPLACE INTO activity_daily VALUES(?,?,?)',(sys.argv[2],(today-datetime.timedelta(days=1)).isoformat(),600)); c.commit()`,path.join(data,'club.sqlite'),created.child.id]);
 const page=await owner.newPage();page.on('pageerror',e=>report.errors.push(e.message));await page.goto(url);await page.locator('.family-card').waitFor();assert.match(await page.locator('.family-card').innerText(),/1 of 30 quests completed/);
 for(const period of ['today','week','month','year','all']){await page.locator(`[data-action="parent-period"][data-value="${period}"]`).click();await page.locator('.family-card').waitFor();assert.equal(await page.locator(`[data-value="${period}"]`).getAttribute('aria-pressed'),'true');}
 await page.locator('.family-card summary').click();assert.equal(await page.locator('.family-lessons li.done').count(),1);await page.locator('.family-card summary').click();
 await page.locator('[data-action="refresh-family"]').click();await page.waitForFunction(()=>document.querySelector('#site-traffic')?.textContent.includes('Johnny-5'));await page.screenshot({path:path.join(out,'family-dashboard-desktop.png'),fullPage:true});
 for(const viewport of [{width:600,height:1024},{width:1024,height:600},{width:360,height:740}]){await page.setViewportSize(viewport);await page.screenshot({path:path.join(out,`family-dashboard-${viewport.width}.png`),fullPage:true});assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+2));}
 report.checks.push('Five period buttons, refresh, completed lesson lists, desktop and three narrow/tablet layouts');
 const otherPage=await other.newPage();await otherPage.goto(url);await otherPage.getByText('Add your first child account.',{exact:false}).waitFor();assert.equal(await otherPage.locator('.family-card').count(),0);assert.equal(await otherPage.locator('#site-traffic').count(),0);assert.equal((await other.request.get(url+'/api/site-traffic')).status(),403);assert.equal((await kid.request.get(url+'/api/site-traffic')).status(),403);
 report.checks.push('Other-family isolation and owner-only site traffic; unconfigured connection is explained');
 assert.deepEqual(report.errors,[]);report.status='passed';console.log(JSON.stringify(report));
})().catch(e=>{report.status='failed';report.failure=e.stack;console.error(e);process.exitCode=1;}).finally(async()=>{fs.writeFileSync(path.join(out,'family-browser-results.json'),JSON.stringify(report,null,2));if(browser)await browser.close();proc.kill();fs.rmSync(data,{recursive:true,force:true});});
