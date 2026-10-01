#!/usr/bin/env python3
"""Pixel Quest Club: dependency-free VPS server. Python 3.11+."""
import os,json,sqlite3,secrets,hashlib,hmac,time,re,threading,urllib.parse,argparse
from contextlib import contextmanager
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from http.cookies import SimpleCookie
from zoneinfo import ZoneInfo
import activity, traffic
ROOT=Path(__file__).resolve().parent
PUBLIC=Path(os.environ.get('PQC_PUBLIC_DIR',str(ROOT/'public')))
DATA=Path(os.environ.get('PQC_DATA_DIR',str(ROOT/'data')))
SECURE=os.environ.get('PQC_SECURE_COOKIES','0')=='1'
SIGNUP=os.environ.get('PQC_OPEN_CHILD_SIGNUP','0')=='1'
PARENT_SIGNUP=os.environ.get('PQC_PARENT_SIGNUP','1')=='1'
INVITE=os.environ.get('PQC_PARENT_INVITE','')
MAX_ACCOUNTS=int(os.environ.get('PQC_MAX_ACCOUNTS','250'))
ACTIVITY_TZ=ZoneInfo(os.environ.get('PQC_TIMEZONE','America/Denver'))
OWNER=os.environ.get('PQC_OWNER_USERNAME','').lower()
CF_ZONE=os.environ.get('PQC_CF_ZONE_ID','')
CF_TOKEN=os.environ.get('PQC_CF_ANALYTICS_TOKEN','')
LOCK=threading.Lock(); ATTEMPTS={}
@contextmanager
def db():
 c=sqlite3.connect(DATA/'club.sqlite',timeout=15)
 c.row_factory=sqlite3.Row;c.execute('PRAGMA foreign_keys=ON')
 try:
  with c:yield c
 finally:c.close()
def init():
 DATA.mkdir(parents=True,exist_ok=True)
 with db() as c:
  c.execute('PRAGMA journal_mode=WAL')
  c.executescript('''CREATE TABLE IF NOT EXISTS users(id TEXT PRIMARY KEY,username TEXT UNIQUE NOT NULL,role TEXT NOT NULL,parent_id TEXT REFERENCES users(id),secret TEXT NOT NULL,recovery TEXT NOT NULL,avatar INTEGER NOT NULL DEFAULT 0,path TEXT NOT NULL DEFAULT 'story',theme TEXT NOT NULL DEFAULT 'royal',created REAL NOT NULL,last_seen REAL NOT NULL);
CREATE TABLE IF NOT EXISTS sessions(token TEXT PRIMARY KEY,user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,expires REAL NOT NULL);
CREATE TABLE IF NOT EXISTS saves(user_id TEXT PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,payload TEXT NOT NULL,revision INTEGER NOT NULL DEFAULT 0,updated REAL NOT NULL);''')
  c.executescript(activity.SCHEMA)
def digest(secret):
 salt=secrets.token_hex(16);return salt+':'+hashlib.pbkdf2_hmac('sha256',secret.encode(),salt.encode(),200000).hex()
def verify(secret,stored):
 try:salt,want=stored.split(':');return hmac.compare_digest(want,hashlib.pbkdf2_hmac('sha256',secret.encode(),salt.encode(),200000).hex())
 except (ValueError,AttributeError):return False
def throttle(key,limit=10,window=600):
 now=time.time()
 with LOCK:
  if len(ATTEMPTS)>5000:
   for k in list(ATTEMPTS):
    if not ATTEMPTS[k] or ATTEMPTS[k][-1]<now-window:ATTEMPTS.pop(k,None)
  a=[x for x in ATTEMPTS.get(key,[]) if x>now-window]
  if len(a)>=limit:return False
  a.append(now);ATTEMPTS[key]=a;return True
def public_user(u):
 result={k:u[k] for k in ['id','username','role','avatar','path','theme','parent_id']}
 result['owner']=bool(OWNER and u['role']=='parent' and u['username']==OWNER)
 return result
def create_user(role,secret,parent=None,username=None,avatar=0,path='story',theme='royal'):
 now=time.time();uid=secrets.token_hex(12);recovery=secrets.token_urlsafe(24)
 if username is None:
  username='-'.join([secrets.choice(['Comet','Pixel','Sunny','Moon','Royal','Brave']),secrets.choice(['Otter','Fox','Owl','Panda','Dragon','Robot']),str(secrets.randbelow(90000)+10000)]).lower()
 if not re.fullmatch(r'[a-z0-9-]{3,40}',username):raise ValueError('Use 3–40 letters, numbers or hyphens for the username.')
 if role=='child' and not re.fullmatch(r'\d{6}',secret):raise ValueError('Choose a six-digit code.')
 if role=='parent' and not 10<=len(secret)<=128:raise ValueError('Use a password of 10–128 characters.')
 if path not in ['story','game','dev'] or theme not in ['royal','space','halloween'] or not 0<=avatar<30:raise ValueError('Choose a valid path, theme and avatar.')
 secret_hash=digest(secret);recovery_hash=digest(recovery)
 with db() as c:
  c.execute('BEGIN IMMEDIATE')
  if c.execute('SELECT count(*) FROM users').fetchone()[0]>=MAX_ACCOUNTS:raise ValueError('The club is full for now. Guest lessons are still available.')
  c.execute('INSERT INTO users VALUES(?,?,?,?,?,?,?,?,?,?,?)',(uid,username,role,parent,secret_hash,recovery_hash,avatar,path,theme,now,now))
  u=c.execute('SELECT * FROM users WHERE id=?',(uid,)).fetchone()
 return u,recovery
def validate_save(payload):
 if payload.get('schema')!=1:raise ValueError('Invalid draft version.')
 for field in ['completed','checks','notes','lastDays','projects']:
  value=payload.get(field,{})
  if not isinstance(value,dict):raise ValueError('Invalid '+field+'.')
  if len(value)>(3 if field in ['lastDays','projects'] else 90):raise ValueError('Too many saved entries.')
 for field in ['completed','checks','notes']:
  for key,value in payload.get(field,{}).items():
   if not re.fullmatch(r'(story|game|dev)-(?:[1-9]|[12][0-9]|30)',key):raise ValueError('Invalid quest identifier.')
   if field=='completed' and not isinstance(value,bool):raise ValueError('Invalid completion.')
   if field=='notes' and (not isinstance(value,str) or len(value)>400):raise ValueError('Keep notes below 400 characters.')
   if field=='checks' and (not isinstance(value,list) or len(value)>4 or any(x is not None and not isinstance(x,bool) for x in value)):raise ValueError('Invalid quest checks.')
 for key,value in payload.get('lastDays',{}).items():
  if key not in ['story','game','dev'] or not isinstance(value,int) or not 1<=value<=30:raise ValueError('Invalid last quest.')
 for key,value in payload.get('projects',{}).items():
  if key not in ['story','game','dev'] or not isinstance(value,dict) or value.get('schema')!=1:raise ValueError('Invalid browser project.')
 if payload.get('path') not in [None,'story','game','dev'] or payload.get('theme','royal') not in ['royal','space','halloween']:raise ValueError('Invalid path or theme.')
 if not isinstance(payload.get('avatar',0),int) or not 0<=payload.get('avatar',0)<30:raise ValueError('Invalid avatar.')

class ClubServer(ThreadingHTTPServer):
 request_queue_size=256

class Handler(SimpleHTTPRequestHandler):
 server_version='PixelQuestClub'
 def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(PUBLIC),**kwargs)
 def log_message(self,fmt,*args):pass # Do not log children's identifiers or request payloads.
 def end_headers(self):
  self.send_header('X-Content-Type-Options','nosniff');self.send_header('Referrer-Policy','same-origin')
  self.send_header('Content-Security-Policy',"default-src 'self'; img-src 'self' blob: data:; script-src 'self'; style-src 'self' 'unsafe-inline'; connect-src 'self'; frame-src 'none'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'")
  super().end_headers()
 def reply(self,status,data,cookie=None):
  raw=json.dumps(data).encode();self.send_response(status);self.send_header('Content-Type','application/json');self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(raw)))
  if cookie:self.send_header('Set-Cookie',cookie)
  self.end_headers();self.wfile.write(raw)
 def cookie(self,value='',age=0):return f'pqc_session={value}; Path=/; HttpOnly; SameSite=Lax; Max-Age={age}'+('; Secure' if SECURE else '')
 def user(self):
  try:
   cookie=SimpleCookie(self.headers.get('Cookie',''));token=cookie['pqc_session'].value if 'pqc_session' in cookie else ''
   with db() as c:
    u=c.execute('SELECT users.* FROM users JOIN sessions ON users.id=sessions.user_id WHERE sessions.token=? AND sessions.expires>?',(hashlib.sha256(token.encode()).hexdigest(),time.time())).fetchone()
   return u
  except Exception:return None
 def login(self,u,remember=False):
  token=secrets.token_urlsafe(32);age=2592000 if remember else 28800
  with db() as c:
   c.execute('DELETE FROM sessions WHERE expires<?',(time.time(),));c.execute('INSERT INTO sessions VALUES(?,?,?)',(hashlib.sha256(token.encode()).hexdigest(),u['id'],time.time()+age));c.execute('UPDATE users SET last_seen=? WHERE id=?',(time.time(),u['id']))
  return self.cookie(token,age)
 def do_GET(self):
  path=urllib.parse.urlparse(self.path).path
  if path.startswith('/api/'):
   u=self.user()
   if path=='/api/session':return self.reply(200,dict(user=public_user(u) if u else None,openChildSignup=SIGNUP,parentSignup=PARENT_SIGNUP,inviteRequired=bool(INVITE)))
   if not u:return self.reply(401,dict(error='Sign in to save online.'))
   if path=='/api/save':
    with db() as c:r=c.execute('SELECT * FROM saves WHERE user_id=?',(u['id'],)).fetchone()
    return self.reply(200,dict(payload=json.loads(r['payload']) if r else None,revision=r['revision'] if r else 0))
   if path=='/api/children' and u['role']=='parent':
    with db() as c:
     rows=c.execute('SELECT users.*,saves.payload FROM users LEFT JOIN saves ON users.id=saves.user_id WHERE parent_id=?',(u['id'],)).fetchall()
     children=[]
     for r in rows:
      saved=json.loads(r['payload']) if r['payload'] else {}
      children.append(dict(**{**public_user(r),'path':saved.get('path') or r['path']},progress=saved.get('completed',{}),lastDays=saved.get('lastDays',{}),activity=activity.summary(c,r['id'],time.time(),ACTIVITY_TZ)))
    return self.reply(200,dict(children=children,timezone=str(ACTIVITY_TZ)))
   if path=='/api/site-traffic':
    if not public_user(u)['owner']:return self.reply(403,dict(error='Site traffic is available only to the owner.'))
    return self.reply(200,traffic.report(CF_ZONE,CF_TOKEN))
   return self.reply(404,dict(error='Not found.'))
  if '..' in urllib.parse.unquote(path).split('/'):return self.reply(404,dict(error='Not found.'))
  return super().do_GET()
 def do_POST(self):self.mutate()
 def do_PUT(self):self.mutate()
 def do_DELETE(self):self.mutate()
 def mutate(self):
  # JSON-only requests with same-origin checks prevent cross-site form writes.
  origin=self.headers.get('Origin');host=self.headers.get('Host','')
  if origin and urllib.parse.urlparse(origin).netloc!=host:return self.reply(403,dict(error='Use this website to make changes.'))
  if not self.headers.get('Content-Type','').startswith('application/json'):return self.reply(415,dict(error='Use JSON.'))
  try:
   size=int(self.headers.get('Content-Length','0'))
   if not 0<size<=250000:return self.reply(413,dict(error='This draft is too large.'))
   b=json.loads(self.rfile.read(size));path=urllib.parse.urlparse(self.path).path
   if not isinstance(b,dict):raise ValueError('Invalid request.')
   u=self.user()
   if path in ['/api/login','/api/register','/api/recover']:
    key=str(b.get('username','')).lower()[:40]
    if not throttle('auth-user:'+key,10) or not throttle('auth-ip:'+self.client_address[0],100):return self.reply(429,dict(error='Too many tries. Take a break and try again later.'))
   if path=='/api/login':
    name=str(b.get('username','')).strip().lower();secret=str(b.get('secret',''))[:128]
    with db() as c:r=c.execute('SELECT * FROM users WHERE username=?',(name,)).fetchone()
    if not r or not verify(secret,r['secret']):return self.reply(401,dict(error='That username and code/password did not match.'))
    return self.reply(200,dict(user=public_user(r)),self.login(r,b.get('remember') is True))
   if path=='/api/register':
    role=b.get('role','parent')
    if role=='parent':
     if not PARENT_SIGNUP:return self.reply(403,dict(error='Parent registration is closed.'))
     if INVITE and not hmac.compare_digest(str(b.get('invite','')),INVITE):return self.reply(403,dict(error='Ask the club owner for the family setup code.'))
    elif role=='child':
     if not SIGNUP:return self.reply(403,dict(error='Guest lessons are open. Ask a grown-up to create a saved account.'))
    else:raise ValueError('Choose a valid account type.')
    r,key=create_user(role,str(b.get('secret','')),username=str(b['username']).lower() if role=='parent' else None,avatar=int(b.get('avatar',0)),path=b.get('path','story'),theme=b.get('theme','royal'))
    return self.reply(201,dict(user=public_user(r),recoveryKey=key),self.login(r))
   if path=='/api/recover':
    with db() as c:r=c.execute('SELECT * FROM users WHERE username=?',(str(b.get('username','')).lower(),)).fetchone()
    if not r or not verify(str(b.get('recoveryKey',''))[:128],r['recovery']):return self.reply(400,dict(error='That recovery information did not match.'))
    new=str(b.get('secret',''))
    if (r['role']=='child' and not re.fullmatch(r'\d{6}',new)) or (r['role']=='parent' and not 10<=len(new)<=128):raise ValueError('Choose a valid new code/password.')
    key=secrets.token_urlsafe(24)
    with db() as c:c.execute('UPDATE users SET secret=?,recovery=? WHERE id=?',(digest(new),digest(key),r['id']));c.execute('DELETE FROM sessions WHERE user_id=?',(r['id'],))
    return self.reply(200,dict(recoveryKey=key,message='Code changed. Keep the new recovery key and sign in.'))
   if not u:return self.reply(401,dict(error='Sign in first.'))
   if not throttle('writes:'+u['id'],120,60):return self.reply(429,dict(error='Saving too quickly. Try again shortly.'))
   if path=='/api/logout':
    cookie=SimpleCookie(self.headers.get('Cookie',''));token=cookie['pqc_session'].value if 'pqc_session' in cookie else ''
    with db() as c:c.execute('DELETE FROM sessions WHERE token=?',(hashlib.sha256(token.encode()).hexdigest(),))
    return self.reply(200,dict(ok=True),self.cookie())
   if path=='/api/activity':
    if u['role']!='child' or not u['parent_id']:return self.reply(403,dict(error='Activity summaries are for linked child accounts.'))
    with db() as c:credited=activity.record(c,u['id'],b,time.time(),ACTIVITY_TZ)
    return self.reply(200,dict(credited=credited))
   if path=='/api/save':
    payload=b.get('payload');revision=b.get('revision',0)
    if not isinstance(payload,dict) or not isinstance(revision,int):raise ValueError('Invalid draft.')
    validate_save(payload)
    raw=json.dumps(payload)
    if len(raw.encode())>200000:raise ValueError('Keep drafts below 200 KB; download a project backup.')
    with db() as c:
     c.execute('BEGIN IMMEDIATE');r=c.execute('SELECT revision FROM saves WHERE user_id=?',(u['id'],)).fetchone();current=r[0] if r else 0
     if revision!=current:return self.reply(409,dict(error='Another device saved a newer version. Download your draft before loading the online version.',revision=current))
     c.execute('INSERT INTO saves VALUES(?,?,?,?) ON CONFLICT(user_id) DO UPDATE SET payload=excluded.payload,revision=excluded.revision,updated=excluded.updated',(u['id'],raw,current+1,time.time()))
    return self.reply(200,dict(revision=current+1))
   if path=='/api/children' and u['role']=='parent':
    r,key=create_user('child',str(b.get('secret','')),u['id'],avatar=int(b.get('avatar',0)),path=b.get('path','story'),theme=b.get('theme','royal'))
    return self.reply(201,dict(child=public_user(r),recoveryKey=key))
   if path in ['/api/reset-child','/api/delete-child'] and u['role']=='parent':
    with db() as c:r=c.execute('SELECT * FROM users WHERE id=? AND parent_id=?',(b.get('id'),u['id'])).fetchone()
    if not r:return self.reply(404,dict(error='Child account not found.'))
    if path=='/api/reset-child':
     pin=str(b.get('secret',''))
     if not re.fullmatch(r'\d{6}',pin):raise ValueError('Choose a six-digit code.')
     with db() as c:c.execute('UPDATE users SET secret=? WHERE id=?',(digest(pin),r['id']));c.execute('DELETE FROM sessions WHERE user_id=?',(r['id'],))
    else:
     with db() as c:c.execute('DELETE FROM users WHERE id=?',(r['id'],))
    return self.reply(200,dict(ok=True))
   if path=='/api/link-parent' and u['role']=='child' and not u['parent_id']:
    name=str(b.get('username','')).lower()
    if not throttle('link:'+name,10):return self.reply(429,dict(error='Too many tries.'))
    with db() as c:r=c.execute("SELECT * FROM users WHERE username=? AND role='parent'",(name,)).fetchone()
    if not r or not verify(str(b.get('secret',''))[:128],r['secret']):return self.reply(401,dict(error='Parent sign-in did not match.'))
    with db() as c:c.execute('UPDATE users SET parent_id=? WHERE id=?',(r['id'],u['id']))
    return self.reply(200,dict(ok=True))
   return self.reply(404,dict(error='Not found.'))
  except sqlite3.IntegrityError:return self.reply(409,dict(error='That username is already in use. Choose another.'))
  except (ValueError,TypeError,KeyError,json.JSONDecodeError) as e:return self.reply(400,dict(error=str(e) or 'Check your entries.'))
  except Exception:return self.reply(500,dict(error='Could not save that change. Your local draft is still available.'))
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--port',type=int,default=int(os.environ.get('PORT','8080')));parser.add_argument('--host',default=os.environ.get('HOST','127.0.0.1'));args=parser.parse_args();init()
 print(f'Pixel Quest Club serving on {args.host}:{args.port}',flush=True)
 ClubServer((args.host,args.port),Handler).serve_forever()
