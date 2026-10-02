import unittest, tempfile, os, sys, subprocess, time, json, urllib.request, urllib.error, http.cookiejar, sqlite3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import server

class Client:
 def __init__(self):self.opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
 def call(self,path,body=None):
  req=urllib.request.Request('http://127.0.0.1:8086/api/'+path,data=json.dumps(body).encode() if body is not None else None,headers={'Content-Type':'application/json'})
  try:
   with self.opener.open(req) as r:return r.status,json.load(r)
  except urllib.error.HTTPError as e:return e.code,json.load(e)

class FamilyLinks(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();cls.database=Path(cls.tmp.name)/'club.sqlite'
  original=server.DATA;server.DATA=Path(cls.tmp.name);server.init()
  for name in ['link-alpha','link-beta','link-guesser']:server.create_user('parent','disposable-password',username=name)
  server.DATA=original
  env={**os.environ,'PQC_DATA_DIR':cls.tmp.name,'PQC_OPEN_CHILD_SIGNUP':'1','PQC_PARENT_SIGNUP':'0','PQC_SECURE_COOKIES':'0'}
  cls.proc=subprocess.Popen([sys.executable,str(ROOT/'server.py'),'--port','8086'],env=env,stdout=subprocess.DEVNULL)
  for _ in range(80):
   try:Client().call('session');break
   except OSError:time.sleep(.05)
 @classmethod
 def tearDownClass(cls):cls.proc.terminate();cls.proc.wait();cls.tmp.cleanup()
 def parent(self,name='link-alpha'):
  c=Client();self.assertEqual(c.call('login',{'username':name,'secret':'disposable-password'})[0],200);return c
 def child(self,**fields):
  c=Client();status,r=c.call('register',{'role':'child','secret':'123456','avatar':7,'path':'game','theme':'space',**fields});self.assertEqual(status,201,r);return c,r['user']
 def expire(self,table,column,value):
  with sqlite3.connect(self.database) as c:c.execute(f'UPDATE {table} SET expires=0 WHERE {column}=?',(value,))
 def test_confirmation_preserves_saved_work_and_isolation(self):
  parent=self.parent();other=self.parent('link-beta');child,kid=self.child()
  self.assertEqual(child.call('session')[1]['user']['avatar'],7)
  self.assertFalse(kid['parent_id']);self.assertFalse(child.call('session')[1]['parentSignup'])
  self.assertEqual(Client().call('register',{'role':'parent','username':'uninvited','secret':'disposable-password'})[0],403)
  payload={'schema':1,'path':'game','theme':'space','completed':{'game-1':True},'projects':{},'notes':{'game-1':'Before linking'}}
  self.assertEqual(child.call('save',{'payload':payload,'revision':0})[0],200)
  code=child.call('child-link-code',{})[1]['code']
  self.assertEqual(parent.call('request-child-link',{'username':kid['username']})[0],400)
  self.assertEqual(parent.call('request-child-link',{'username':kid['username'],'code':code})[0],200)
  self.assertNotIn(kid['id'],[r['id'] for r in parent.call('children')[1]['children']])
  self.assertEqual(other.call('request-child-link',{'username':kid['username'],'code':code})[0],400)
  pending=child.call('family-link')[1]['pending'];self.assertEqual(pending['parentUsername'],'link-alpha')
  self.assertEqual(other.call('resolve-child-link',{'requestId':pending['requestId'],'accept':True})[0],403)
  self.assertEqual(child.call('resolve-child-link',{'requestId':'wrong','accept':True})[0],400)
  self.assertEqual(child.call('resolve-child-link',{'requestId':pending['requestId'],'accept':True})[0],200)
  self.assertEqual(child.call('resolve-child-link',{'requestId':pending['requestId'],'accept':True})[0],400)
  self.assertEqual(child.call('save')[1],{'payload':payload,'revision':1})
  row=next(r for r in parent.call('children')[1]['children'] if r['id']==kid['id']);self.assertEqual(row['progress'],{'game-1':True})
  self.assertNotIn(kid['id'],[r['id'] for r in other.call('children')[1]['children']])
  self.assertEqual(other.call('reset-child',{'id':kid['id'],'secret':'654321'})[0],404)
  self.assertEqual(child.call('child-link-code',{})[0],400)
  self.assertEqual(child.call('link-parent',{'username':'link-beta','secret':'disposable-password'})[0],404)
  self.assertEqual(parent.call('reset-child',{'id':kid['id'],'secret':'654321'})[0],200)
  self.assertEqual(child.call('session')[1]['user'],None)
 def test_decline_regeneration_expiry_and_hashes(self):
  parent=self.parent();child,kid=self.child()
  old=child.call('child-link-code',{})[1]['code'];new=child.call('child-link-code',{})[1]['code']
  self.assertEqual(parent.call('request-child-link',{'username':kid['username'],'code':old})[0],400)
  with sqlite3.connect(self.database) as c:
   stored=c.execute('SELECT token_hash FROM family_codes WHERE user_id=?',(kid['id'],)).fetchone()[0]
  self.assertNotEqual(stored,new.replace('-',''));self.assertEqual(len(stored),64)
  self.assertEqual(parent.call('request-child-link',{'username':kid['username'],'code':new})[0],200)
  req=child.call('family-link')[1]['pending']
  self.assertEqual(child.call('resolve-child-link',{'requestId':req['requestId'],'accept':False})[0],200)
  self.assertIsNone(child.call('session')[1]['user']['parent_id'])
  code=child.call('child-link-code',{})[1]['code'];self.expire('family_codes','user_id',kid['id'])
  self.assertEqual(parent.call('request-child-link',{'username':kid['username'],'code':code})[0],400)
  code=child.call('child-link-code',{})[1]['code'];parent.call('request-child-link',{'username':kid['username'],'code':code})
  req=child.call('family-link')[1]['pending'];self.expire('family_requests','child_id',kid['id'])
  self.assertEqual(child.call('resolve-child-link',{'requestId':req['requestId'],'accept':True})[0],400)
 def test_family_signup_revocation_and_atomic_capacity(self):
  parent=self.parent();other=self.parent('link-beta');code=parent.call('family-code',{})[1]['code']
  for _ in range(2):
   child,kid=self.child(familyCode=code);self.assertIsNotNone(kid['parent_id'])
  self.assertEqual(other.call('revoke-family-code',{})[0],200)
  _,kid=self.child(familyCode=code) # Other parent cannot revoke this invitation.
  self.assertEqual(parent.call('revoke-family-code',{})[0],200)
  with sqlite3.connect(self.database) as c:before=c.execute('SELECT count(*) FROM users').fetchone()[0]
  self.assertEqual(Client().call('register',{'role':'child','secret':'123456','familyCode':code})[0],400)
  with sqlite3.connect(self.database) as c:self.assertEqual(c.execute('SELECT count(*) FROM users').fetchone()[0],before)
  code=parent.call('family-code',{})[1]['code']
  with sqlite3.connect(self.database) as c:c.execute("UPDATE family_codes SET uses=19 WHERE kind='family'")
  self.child(familyCode=code)
  self.assertEqual(Client().call('register',{'role':'child','secret':'123456','familyCode':code})[0],400)
  new=parent.call('family-code',{})[1]['code'];self.assertEqual(Client().call('register',{'role':'child','secret':'123456','familyCode':code})[0],400)
  uid=parent.call('session')[1]['user']['id'];self.expire('family_codes','user_id',uid)
  self.assertEqual(Client().call('register',{'role':'child','secret':'123456','familyCode':new})[0],400)
 def test_link_guessing_and_role_boundaries(self):
  parent=self.parent('link-guesser');child,kid=self.child()
  self.assertEqual(Client().call('child-link-code',{})[0],401)
  self.assertEqual(parent.call('child-link-code',{})[0],403)
  self.assertEqual(child.call('family-code',{})[0],403)
  self.assertEqual(child.call('request-child-link',{'username':kid['username'],'code':'00000000'})[0],403)
  for _ in range(10):self.assertEqual(parent.call('request-child-link',{'username':'unknown-child','code':'00000000'})[0],400)
  self.assertEqual(parent.call('request-child-link',{'username':'unknown-child','code':'00000000'})[0],429)
 def test_last_family_code_use_is_atomic(self):
  import concurrent.futures
  original=server.DATA
  with tempfile.TemporaryDirectory() as directory:
   try:
    server.DATA=Path(directory);server.init();parent,_=server.create_user('parent','disposable-password',username='race-family')
    with server.db() as c:
     c.execute('BEGIN IMMEDIATE');code=server.family_links.issue(c,parent,'family')['code'];c.execute('UPDATE family_codes SET uses=19')
    def create(_):
     try:server.create_user('child','123456',family_code=code);return True
     except ValueError:return False
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:self.assertEqual(sum(pool.map(create,range(5))),1)
    with server.db() as c:self.assertEqual(c.execute('SELECT count(*) FROM users').fetchone()[0],2)
   finally:server.DATA=original

if __name__=='__main__':unittest.main()
