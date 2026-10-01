"""Owner-only, server-side Cloudflare aggregates. Credentials never reach browsers."""
import json, re, threading, time, urllib.request
from datetime import datetime, timedelta, timezone
LOCK=threading.Lock()
CACHE={}

def fetch_daily(zone,token):
 if not re.fullmatch(r'[a-fA-F0-9]{32}',zone):raise ValueError('Invalid zone configuration.')
 today=datetime.now(timezone.utc).date()
 query='''query($zone:String!,$start:Date!,$end:Date!){viewer{zones(filter:{zoneTag:$zone}){httpRequests1dGroups(limit:7,orderBy:[date_ASC],filter:{date_geq:$start,date_leq:$end}){dimensions{date} sum{requests pageViews} uniq{uniques}}}}}'''
 request=urllib.request.Request('https://api.cloudflare.com/client/v4/graphql',data=json.dumps({'query':query,'variables':{'zone':zone,'start':(today-timedelta(days=6)).isoformat(),'end':today.isoformat()}}).encode(),headers={'Authorization':'Bearer '+token,'Content-Type':'application/json'},method='POST')
 with urllib.request.urlopen(request,timeout=8) as response:
  raw=response.read(1000001)
 if len(raw)>1000000:raise ValueError('Oversized analytics response.')
 result=json.loads(raw)
 if result.get('errors'):raise ValueError('Analytics access unavailable.')
 zones=result['data']['viewer']['zones']
 if not zones:raise ValueError('Zone access unavailable.')
 rows=zones[0]['httpRequests1dGroups']
 return [{'day':r['dimensions']['date'],'requests':max(0,int(r['sum']['requests'])),'pageViews':max(0,int(r['sum']['pageViews'])),'uniqueEstimates':max(0,int(r['uniq']['uniques']))} for r in rows]

def report(zone,token):
 if not zone or not token:return {'status':'not-configured','message':'Johnny-5 can connect a zone-scoped read-only Cloudflare analytics token in the private server configuration.'}
 with LOCK:
  now=time.time()
  if CACHE.get('key')==(zone,token) and now-CACHE.get('at',0)<300:return CACHE['value']
  try:value={'status':'connected','daily':fetch_daily(zone,token),'updated':now,'timezone':'UTC'}
  except Exception:
   # Never expose provider errors, headers or secrets to the browser/logs.
   value={'status':'unavailable','message':'Cloudflare analytics could not be read. Ask Johnny-5 to check token permissions, zone access and dataset availability. Family progress still works.'}
  CACHE.update(key=(zone,token),at=now,value=value)
  return value
