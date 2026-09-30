"""Validate source, then produce versioned static files for Caddy."""
from pathlib import Path
import hashlib,json,shutil,subprocess,os,re
root=Path(__file__).resolve().parent; public=root/'public';dist=root/'dist'
data=json.loads((public/'curriculum.json').read_text())
assert set(data['paths'])=={'story','game','dev'}
assert len(data['lessons'])==90
for path in data['paths']:
 lessons=[l for l in data['lessons'] if l['path']==path]
 assert sorted(l['day'] for l in lessons)==list(range(1,31))
 for l in lessons: assert len(l['steps'])==3 and all(l.get(k) for k in ['concept','hint','challenge','recall'])
node=os.environ.get('PQC_NODE','node')
for name in ['app.js','engine.js']:subprocess.run([node,'--check',str(public/name)],check=True)
# No output changes until all source checks pass.
if dist.exists():shutil.rmtree(dist)
dist.mkdir();mapping={}
def emit(name,content):
 p=Path(name);digest=hashlib.sha256(content).hexdigest()[:12]
 target=str(p.with_name(p.stem+'-'+digest+p.suffix));dest=dist/target
 dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(content);mapping[name]=target
for p in (public/'assets').glob('*.webp'):emit('assets/'+p.name,p.read_bytes())
for name in ['curriculum.json','starter-godot.zip','favicon.svg']:emit(name,(public/name).read_bytes())
for name in ['style.css','engine.js','app.js']:
 text=(public/name).read_text()
 for before,after in mapping.items():text=re.sub(re.escape(before)+r'(?![A-Za-z0-9_])',lambda _match:after,text)
 emit(name,text.encode())
text=(public/'index.html').read_text()
for before,after in mapping.items():text=re.sub(re.escape(before)+r'(?![A-Za-z0-9_])',lambda _match:after,text)
assert '<script>' not in text and 'script src=' in text
(dist/'index.html').write_text(text)
(dist/'404.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Quest not found</title><h1>That quest is not here.</h1><p><a href="/">Return to Pixel Quest Club</a></p></html>')
for script in dist.glob('*.js'):subprocess.run([node,'--check',str(script)],check=True)
print('Validated 90 lessons and generated JavaScript; built versioned static assets in dist/.')
