import unittest,tempfile,os,sys,subprocess,time,json,urllib.request,urllib.error,http.cookiejar
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class Client:
 def __init__(self):self.opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
 def call(self,path,data=None,origin=None):
  headers={'Content-Type':'application/json'}
  if origin:headers['Origin']=origin
  req=urllib.request.Request('http://127.0.0.1:8082/api/'+path,data=json.dumps(data).encode() if data is not None else None,headers=headers)
  try:
   with self.opener.open(req) as r:return r.status,json.load(r)
  except urllib.error.HTTPError as e:return e.code,json.load(e)
class ClubTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.temp=tempfile.TemporaryDirectory();env={**os.environ,'PQC_DATA_DIR':cls.temp.name,'PQC_PARENT_INVITE':'test-family','PQC_OPEN_CHILD_SIGNUP':'0'}
  cls.proc=subprocess.Popen([sys.executable,str(ROOT/'server.py'),'--port','8082'],env=env,stdout=subprocess.DEVNULL)
  for _ in range(40):
   try:Client().call('session');break
   except OSError:time.sleep(.05)
 @classmethod
 def tearDownClass(cls):cls.proc.terminate();cls.proc.wait();cls.temp.cleanup()
 def test_accounts_isolation_recovery_and_save_conflict(self):
  parent=Client();other=Client();guest=Client();child=Client()
  self.assertEqual(guest.call('save')[0],401)
  self.assertEqual(guest.call('register',{'role':'child','secret':'123456'})[0],403)
  self.assertEqual(parent.call('register',{'role':'parent','username':'parent-one','secret':'test-password-123','invite':'wrong'})[0],403)
  status,p=parent.call('register',{'role':'parent','username':'parent-one','secret':'test-password-123','invite':'test-family'});self.assertEqual(status,201)
  status,o=other.call('register',{'role':'parent','username':'parent-two','secret':'test-password-456','invite':'test-family'});self.assertEqual(status,201)
  status,k=parent.call('children',{'secret':'123456','avatar':13,'path':'story','theme':'royal'});self.assertEqual(status,201);kid=k['child']
  self.assertEqual(other.call('reset-child',{'id':kid['id'],'secret':'654321'})[0],404)
  self.assertEqual(other.call('delete-child',{'id':kid['id']})[0],404)
  self.assertEqual(child.call('login',{'username':kid['username'],'secret':'123456'})[0],200)
  self.assertEqual(child.call('children')[0],404)
  payload={'schema':1,'completed':{'story-1':True},'projects':{}}
  status,r=child.call('save',{'payload':payload,'revision':0});self.assertEqual(status,200);self.assertEqual(r['revision'],1)
  self.assertEqual(child.call('save',{'payload':payload,'revision':0})[0],409)
  self.assertEqual(child.call('save',{'payload':payload,'revision':1},origin='https://evil.example')[0],403)
  self.assertEqual(parent.call('children')[1]['children'][0]['progress'],{'story-1':True})
  self.assertEqual(parent.call('reset-child',{'id':kid['id'],'secret':'654321'})[0],200)
  self.assertEqual(child.call('save')[0],401)
  self.assertEqual(child.call('recover',{'username':kid['username'],'recoveryKey':k['recoveryKey'],'secret':'222222'})[0],200)
  self.assertEqual(child.call('recover',{'username':kid['username'],'recoveryKey':k['recoveryKey'],'secret':'333333'})[0],400)
  self.assertEqual(child.call('login',{'username':kid['username'],'secret':'222222'})[0],200)
  self.assertEqual(parent.call('delete-child',{'id':kid['id']})[0],200)
  self.assertEqual(child.call('save')[0],401)
 def test_malformed_saves_are_rejected_without_destroying_progress(self):
  parent=Client();child=Client()
  self.assertEqual(parent.call('register',{'role':'parent','username':'guard-parent','secret':'test-password-guard','invite':'test-family'})[0],201)
  status,k=parent.call('children',{'secret':'123456'});self.assertEqual(status,201)
  self.assertEqual(child.call('login',{'username':k['child']['username'],'secret':'123456'})[0],200)
  valid={'schema':1,'completed':{'story-1':True},'projects':{}}
  self.assertEqual(child.call('save',{'payload':valid,'revision':0})[0],200)
  for bad in [{'schema':1,'completed':[]},{'schema':1,'projects':[]},{'schema':1,'completed':{'story-999':True}},{'schema':1,'notes':{'story-1':'x'*401}},{'schema':1,'checks':{'story-1':['wrong']}},{'schema':1,'projects':{'__proto__':{'schema':1}}}]:
   self.assertEqual(child.call('save',{'payload':bad,'revision':1})[0],400)
  status,saved=child.call('save');self.assertEqual(saved['revision'],1);self.assertEqual(saved['payload'],valid)
 def test_authentication_attempt_limit(self):
  client=Client()
  for _ in range(10):self.assertEqual(client.call('login',{'username':'wrong-person','secret':'000000'})[0],401)
  self.assertEqual(client.call('login',{'username':'wrong-person','secret':'000000'})[0],429)
if __name__=='__main__':unittest.main()
