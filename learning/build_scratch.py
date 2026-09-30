"""Small, editable Scratch checkpoints built from the block recipes taught here."""
from pathlib import Path
import hashlib,json,zipfile
ROOT=Path(__file__).resolve().parents[1]
class Blocks:
 def __init__(self):self.blocks={};self.n=0
 def add(self,op,fields=None,inputs=None,**kw):
  self.n+=1;k='b'+str(self.n);self.blocks[k]=dict(opcode=op,next=None,parent=None,inputs=inputs or {},fields=fields or {},shadow=kw.pop("shadow",False),topLevel=False,**kw);return k
 def chain(self,*ids):
  for a,b in zip(ids,ids[1:]):self.blocks[a]['next']=b;self.blocks[b]['parent']=a
  return ids[0]
 def script(self,*ids):
  k=self.chain(*ids);self.blocks[k].update(topLevel=True,x=30,y=self.n*18);return k
 def sub(self,parent,key,child):self.blocks[parent]['inputs'][key]=[2,child];self.blocks[child]['parent']=parent
 def hat(self):return self.add('event_whenflagclicked')
 def val(self,v):return [1,[4,str(v)]]
 def text(self,v):return [1,[10,str(v)]]
 def variable(self,name):return self.add('data_variable',{'VARIABLE':[name,name]})
 def set(self,name,v):return self.add('data_setvariableto',{'VARIABLE':[name,name]},{'VALUE':self.val(v)})
 def eq(self,a,v):
  k=self.add('operator_equals',inputs={'OPERAND1':[2,a],'OPERAND2':self.text(v)});self.blocks[a]['parent']=k;return k
 def key(self,name):
  m=self.add('sensing_keyoptions',{'KEY_OPTION':[name,None]},shadow=True);k=self.add('sensing_keypressed',inputs={'KEY_OPTION':[1,m]});self.blocks[m]['parent']=k;return k
 def touching(self,name):
  m=self.add('sensing_touchingobjectmenu',{'TOUCHINGOBJECTMENU':[name,None]},shadow=True);k=self.add('sensing_touchingobject',inputs={'TOUCHINGOBJECTMENU':[1,m]});self.blocks[m]['parent']=k;return k
 def wait(self,cond):
  k=self.add('control_wait_until',inputs={'CONDITION':[2,cond]});self.blocks[cond]['parent']=k;return k
 def broadcast(self,name):
  m=self.add('event_broadcast_menu',{'BROADCAST_OPTION':[name,name]},shadow=True);k=self.add('event_broadcast',inputs={'BROADCAST_INPUT':[1,m]});self.blocks[m]['parent']=k;return k
 def motion(self,axis,amount):return self.add('motion_change'+axis+'by',inputs={('DX' if axis=='x' else 'DY'):self.val(amount)})
 def condition(self,cond,actions):
  k=self.add('control_if',inputs={'CONDITION':[2,cond]});self.blocks[cond]['parent']=k;self.sub(k,'SUBSTACK',self.chain(*actions));return k
 def forever(self,actions):
  k=self.add('control_forever');self.sub(k,'SUBSTACK',self.chain(*actions));return k
 def say(self,text):return self.add('looks_say',inputs={'MESSAGE':self.text(text)})
def project(day):
 assets={}
 def costume(name,color,size):
  svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}"><rect width="{size}" height="{size}" fill="{color}"/></svg>'.encode();aid=hashlib.md5(svg).hexdigest();assets[aid+'.svg']=svg
  return dict(name=name,assetId=aid,md5ext=aid+'.svg',dataFormat='svg',rotationCenterX=size/2,rotationCenterY=size/2,bitmapResolution=1)
 def target(name,B,stage=False,x=0,y=0,color='#007f83',size=30):
  t=dict(isStage=stage,name=name,variables={},lists={},broadcasts={},blocks=B.blocks,comments={},currentCostume=0,costumes=[costume(name,color,size)],sounds=[],volume=100,layerOrder=0 if stage else len(targets),visible=True,x=x,y=y,size=100,direction=90,draggable=False,rotationStyle='all around')
  if stage:t.update(variables={'score':['score',0],'playing':['playing',1]},broadcasts={'Win':'Win','Lose':'Lose'},tempo=60,videoTransparency=50,videoState='off',textToSpeechLanguage=None)
  return t
 targets=[];B=Blocks();start=[B.hat()]
 if day>=19:start+=[B.set('score',0)]
 if day>=23:start+=[B.set('playing',1)]
 B.script(*start)
 if day>=24:B.script(B.hat(),B.wait(B.eq(B.variable('score'),5)),B.broadcast('Win'))
 if day>=23:
  for name in ('Win','Lose'):
   B.script(B.add('event_whenbroadcastreceived',{'BROADCAST_OPTION':[name,name]}),B.set('playing',0))
 targets.append(target('Stage',B,stage=True,color='#fff9ed',size=480))
 B=Blocks();goto=B.add('motion_gotoxy',inputs={'X':B.val(-150),'Y':B.val(0)});start=[B.hat(),goto,B.say('Arrows: collect 5 treasures; avoid orange. Green flag replays.' if day>=25 else '')]
 if day>=17:
  moves=[]
  for key,axis,n in [('right arrow','x',4),('left arrow','x',-4),('up arrow','y',4),('down arrow','y',-4)]:
   if day<21 and key!='right arrow':continue
   actions=[B.motion(axis,n)]
   moves.append(B.condition(B.key(key),actions))
  if day>=23:moves=[B.condition(B.eq(B.variable('playing'),1),moves)]
  start+=[B.forever(moves)]
 B.script(*start)
 if day==16:B.script(B.add('event_whenkeypressed',{'KEY_OPTION':['right arrow',None]}),B.motion('x',10))
 if day>=24:
  B.script(B.add('event_whenbroadcastreceived',{'BROADCAST_OPTION':['Win','Win']}),B.say('You win! Green flag to replay.'))
 if day>=23:
  B.script(B.add('event_whenbroadcastreceived',{'BROADCAST_OPTION':['Lose','Lose']}),B.say('Try another route! Green flag to replay.'))
 targets.append(target('Player',B,x=-150))
 if day>=18:
  positions=[(-80,0)] if day<22 else [(-80,0),(0,0),(80,0),(160,0),(200,80)]
  for i,(x,y) in enumerate(positions,1):
   B=Blocks();seq=[B.hat(),B.add('looks_show'),B.add('control_wait',inputs={'DURATION':B.val(0.1)}),B.wait(B.touching('Player'))]
   if day>=19:
    change=B.add('data_changevariableby',{'VARIABLE':['score','score']},{'VALUE':B.val(1)})
    if day>=23:change=B.condition(B.eq(B.variable('playing'),1),[change])
    seq+=[change]
   seq+=[B.add('looks_hide')];B.script(*seq);targets.append(target('Treasure'+str(i),B,x=x,y=y,color='#ffbf42',size=20))
 if day>=23:
  B=Blocks();B.script(B.hat(),B.add('control_wait',inputs={'DURATION':B.val(0.1)}),B.wait(B.touching('Player')),B.broadcast('Lose'));targets.append(target('Hazard',B,x=0,y=-100,color='#bc581d',size=40))
 return dict(targets=targets,monitors=[],extensions=[],meta={'semver':'3.0.0','vm':'5.0.0','agent':'Pixel Quest Club educational reference'}),assets

def build(output=None):
 out=Path(output) if output else ROOT/'public';out.mkdir(parents=True,exist_ok=True)
 for day in range(15,31):
  data,assets=project(day)
  with zipfile.ZipFile(out/f'scratch-day-{day}.sb3','w',zipfile.ZIP_DEFLATED) as z:
   z.writestr('project.json',json.dumps(data))
   for name,content in assets.items():z.writestr(name,content)
if __name__=='__main__':build()
