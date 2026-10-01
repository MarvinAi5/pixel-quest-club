import unittest, tempfile, sqlite3
from datetime import datetime
from zoneinfo import ZoneInfo
import server, activity, traffic
from unittest.mock import patch
from pathlib import Path

class ActivityTests(unittest.TestCase):
 def setUp(self):
  self.directory=tempfile.TemporaryDirectory();self.old=server.DATA;server.DATA=Path(self.directory.name);server.init()
  self.parent,_=server.create_user('parent','test-password-123',username='test-parent')
  self.child,_=server.create_user('child','123456',self.parent['id'])
  self.uid=self.child['id'];self.tz=ZoneInfo('America/Denver')
 def tearDown(self):server.DATA=self.old;self.directory.cleanup()
 def record(self,now,seq,seconds=15,tab='a'*32,lesson='story-1'):
  with server.db() as c:return activity.record(c,self.uid,dict(tab=tab,seq=seq,seconds=seconds,lesson=lesson),now,self.tz)
 def summary(self,now):
  with server.db() as c:return activity.summary(c,self.uid,now,self.tz)
 def test_retries_tabs_and_server_time_limit(self):
  self.assertEqual(self.record(1000,0),0)
  self.assertEqual(self.record(1015,1),15)
  self.assertEqual(self.record(1015,1),0)
  self.assertEqual(self.record(1015,0,tab='b'*32),0)
  self.assertEqual(self.record(1030,2),15)
  self.assertEqual(self.record(1030,1,tab='b'*32),0)
  self.assertEqual(self.record(1031,3,30),1)
  self.assertEqual(self.summary(1031)['periods']['all']['seconds'],31)
  with self.assertRaises(ValueError):self.record(1046,4,999)
  with self.assertRaises(ValueError):self.record(1046,4,float('nan'))
  with self.assertRaises(ValueError):self.record(1046,4,15,lesson='story-999')
 def test_midnight_periods_and_last_lesson(self):
  now=datetime(2026,10,1,0,0,5,tzinfo=self.tz).timestamp()
  self.record(now-15,0);self.record(now,1,lesson='game-5')
  s=self.summary(now)
  self.assertEqual(s['periods']['today'],{'seconds':5,'days':1})
  self.assertEqual(s['periods']['month'],{'seconds':5,'days':1})
  self.assertEqual(s['periods']['week'],{'seconds':15,'days':2})
  self.assertEqual(s['periods']['year'],{'seconds':15,'days':2})
  self.assertEqual(s['lastLesson'],'game-5')
 def test_dst_boundary_and_no_historical_invention(self):
  before=datetime(2026,11,1,1,59,55,tzinfo=self.tz).timestamp()
  self.record(before,0);self.record(before+15,1)
  self.assertEqual(self.summary(before+15)['periods']['today']['seconds'],15)
  with server.db() as c:
   oldpayload={'schema':1,'completed':{'story-1':True}}
   c.execute('INSERT INTO saves VALUES(?,?,?,?)',(self.uid,__import__('json').dumps(oldpayload),1,before))
  server.init() # Additive startup is safe for an existing populated database.
  with server.db() as c:self.assertEqual(c.execute('SELECT revision FROM saves WHERE user_id=?',(self.uid,)).fetchone()[0],1)
 def test_delete_cascades_activity(self):
  self.record(1000,0);self.record(1015,1)
  with server.db() as c:c.execute('DELETE FROM users WHERE id=?',(self.uid,))
  with server.db() as c:
   for table in ['activity_daily','activity_clock','activity_tabs']:
    self.assertEqual(c.execute('SELECT count(*) FROM '+table).fetchone()[0],0)
 def test_cloudflare_cached_sanitized_and_optional(self):
  traffic.CACHE.clear()
  self.assertEqual(traffic.report('','')['status'],'not-configured')
  with patch.object(traffic,'fetch_daily',return_value=[dict(day='2026-10-01',requests=20,pageViews=3,uniqueEstimates=2)]) as fetch:
   self.assertEqual(traffic.report('a'*32,'private-fake-token')['status'],'connected')
   traffic.report('a'*32,'private-fake-token');self.assertEqual(fetch.call_count,1)
  traffic.CACHE.clear()
  with patch.object(traffic,'fetch_daily',side_effect=RuntimeError('secret-must-never-escape')):
   r=traffic.report('a'*32,'private-fake-token')
   self.assertEqual(r['status'],'unavailable');self.assertNotIn('secret-must-never-escape',str(r))
