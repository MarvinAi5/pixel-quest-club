const fs=require('fs'),vm=require('vm'),assert=require('assert'),path=require('path');
const root=path.join(__dirname,'..');const data=JSON.parse(fs.readFileSync(root+'/public/curriculum.json','utf8'));
const context={console,window:{addEventListener(){},innerWidth:1200},document:{addEventListener(){}},Image:class{},setTimeout,clearTimeout,URL,Blob,confirm:()=>true};
vm.createContext(context);vm.runInContext(fs.readFileSync(root+'/public/engine.js','utf8'),context);context.PQC=context.window.PQC;
let source=fs.readFileSync(root+'/public/app.js','utf8').replace(/start\(\);\s*$/,'');
vm.runInContext(source,context);context.DATA=data;
const report=vm.runInContext(`curriculum=DATA;
const rendered=[];
for(const p of ['story','game','dev']){state.path=p;for(activeDay=1;activeDay<=30;activeDay++){const html=lessonHTML();if(!html.includes('id="stage"')||!html.includes('id="complete"')||!html.includes('id="editor"'))throw Error('Missing workspace');rendered.push(html);}}
JSON.stringify({count:rendered.length,all:rendered});`,context);
const output=JSON.parse(report);assert.equal(output.count,90);fs.writeFileSync(root+'/tests/rendered-views.json',report);
for(const l of data.lessons){assert.equal(l.steps.length,3);assert(l.concept&&l.recall&&l.hint&&l.challenge);assert(l.day>=1&&l.day<=30);}
console.log('All 90 lesson views render, each with the stage, editor, three task checks, explanation and completion control.');
