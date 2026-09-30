"""Bounded, disposable local load test. Never targets production."""
import concurrent.futures,hashlib,json,os,sqlite3,statistics,subprocess,sys,tempfile,time,urllib.request,urllib.error
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def run():
 with tempfile.TemporaryDirectory() as directory:
  port=8097;url=f'http://127.0.0.1:{port}';env={**os.environ,'PQC_DATA_DIR':directory,'PQC_SECURE_COOKIES':'0','PQC_PARENT_SIGNUP':'0'}
  proc=subprocess.Popen([sys.executable,str(ROOT/'server.py'),'--port',str(port)],env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  try:
   for _ in range(80):
    try:urllib.request.urlopen(url+'/api/session',timeout=1).close();break
    except OSError:time.sleep(.05)
   with sqlite3.connect(Path(directory)/'club.sqlite') as db:
    for n in range(100):
     uid=f'test-child-{n}';now=time.time();token=f'disposable-load-session-{n}'
     db.execute('INSERT INTO users VALUES(?,?,?,?,?,?,?,?,?,?,?)',(uid,uid,'child',None,'unused-test-hash','unused-test-hash',n%30,'story','royal',now,now))
     db.execute('INSERT INTO sessions VALUES(?,?,?)',(hashlib.sha256(token.encode()).hexdigest(),uid,now+600))
   def request(n,path,body=None):
    start=time.perf_counter();headers={'Cookie':f'pqc_session=disposable-load-session-{n}','Content-Type':'application/json'}
    req=urllib.request.Request(url+path,data=json.dumps(body).encode() if body is not None else None,headers=headers)
    try:
     with urllib.request.urlopen(req,timeout=12) as r:r.read();status=r.status
    except urllib.error.HTTPError as e:status=e.code;e.close()
    except OSError:status=0
    return status,(time.perf_counter()-start)*1000
   phases=[]
   for count in [8,25,50,100]:
    start=time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=count) as pool:
     jobs=[]
     for n in range(count):
      jobs.append(pool.submit(request,n,'/api/session'))
      jobs.append(pool.submit(request,n,'/api/save'))
      jobs.append(pool.submit(request,n,'/curriculum.json'))
     results=[j.result() for j in jobs]
    times=sorted(x[1] for x in results);errors=[x[0] for x in results if x[0]!=200]
    phases.append({'concurrency':count,'requests':len(results),'failures':len(errors),'status_codes':sorted(set(errors)),'p50_ms':round(statistics.median(times),1),'p95_ms':round(times[int(len(times)*.95)-1],1),'seconds':round(time.perf_counter()-start,2)})
   start=time.perf_counter()
   with concurrent.futures.ThreadPoolExecutor(max_workers=100) as pool:
    results=list(pool.map(lambda n:request(n,'/api/save',{'revision':0,'payload':{'schema':1,'path':'story','completed':{'story-1':True},'projects':{},'notes':{},'checks':{},'lastDays':{},'theme':'royal','avatar':0,'keep':False,'school':False}}),range(100)))
   times=sorted(x[1] for x in results);phases.append({'concurrency':100,'operation':'save','requests':100,'failures':sum(x[0]!=200 for x in results),'status_codes':sorted(set(x[0] for x in results if x[0]!=200)),'p50_ms':round(statistics.median(times),1),'p95_ms':round(times[94],1),'seconds':round(time.perf_counter()-start,2)})
   with sqlite3.connect(Path(directory)/'club.sqlite') as db:
    saved=db.execute('SELECT count(*) FROM saves WHERE revision=1').fetchone()[0]
    integrity=db.execute('PRAGMA integrity_check').fetchone()[0]
   rss=None
   try:rss=int(next(l.split()[1] for l in Path(f'/proc/{proc.pid}/status').read_text().splitlines() if l.startswith('VmRSS:')))
   except (OSError,StopIteration):pass
   result={'environment':'local development container, not Hostinger VPS','fixture':'100 disposable pre-authenticated child sessions; login tested separately','phases':phases,'successful_saves':saved,'database_integrity':integrity,'server_rss_kib_at_end':rss}
   print(json.dumps(result,indent=2))
   return result
  finally:proc.terminate();proc.wait(timeout=10)
if __name__=='__main__':
 result=run()
 if any(p['failures'] for p in result['phases']) or result['successful_saves']!=100 or result['database_integrity']!='ok':raise SystemExit(1)
