"""Small private activity aggregates. No click logs or guest/device tracking."""
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
import math, re

SCHEMA = '''
CREATE TABLE IF NOT EXISTS activity_daily(
 user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
 day TEXT NOT NULL, seconds REAL NOT NULL DEFAULT 0,
 PRIMARY KEY(user_id,day));
CREATE TABLE IF NOT EXISTS activity_clock(
 user_id TEXT PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
 credited_until REAL NOT NULL, last_active REAL, last_lesson TEXT);
CREATE TABLE IF NOT EXISTS activity_tabs(
 user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
 tab TEXT NOT NULL, seq INTEGER NOT NULL, ping REAL NOT NULL,
 PRIMARY KEY(user_id,tab));
'''

def record(c, uid, body, now, tz):
 tab, seq, seconds, lesson = (body.get(k) for k in ('tab','seq','seconds','lesson'))
 if not isinstance(tab,str) or not re.fullmatch(r'[a-f0-9]{32}',tab):
  raise ValueError('Invalid activity session.')
 if type(seq) is not int or not 0 <= seq <= 100000000:
  raise ValueError('Invalid activity sequence.')
 if type(seconds) not in (int,float) or not math.isfinite(seconds) or not 0 <= seconds <= 30:
  raise ValueError('Invalid activity interval.')
 if not isinstance(lesson,str) or not re.fullmatch(r'(story|game|dev)-(?:[1-9]|[12][0-9]|30)',lesson):
  raise ValueError('Invalid activity lesson.')
 c.execute('BEGIN IMMEDIATE')
 c.execute('DELETE FROM activity_tabs WHERE ping<?',(now-86400,))
 previous=c.execute('SELECT seq,ping FROM activity_tabs WHERE user_id=? AND tab=?',(uid,tab)).fetchone()
 if previous and seq <= previous['seq']:
  return 0 # A retried/out-of-order packet must never add time twice.
 clock=c.execute('SELECT * FROM activity_clock WHERE user_id=?',(uid,)).fetchone()
 if not previous:
  if c.execute('SELECT count(*) FROM activity_tabs WHERE user_id=?',(uid,)).fetchone()[0]>=20:
   raise ValueError('Too many open activity sessions. Close unused tabs.')
  credited=0 # First ping establishes a server-time baseline.
 else:
  credited=min(seconds,max(0,now-previous['ping']),max(0,now-clock['credited_until']) if clock else 0)
 c.execute('INSERT INTO activity_tabs VALUES(?,?,?,?) ON CONFLICT(user_id,tab) DO UPDATE SET seq=excluded.seq,ping=excluded.ping',(uid,tab,seq,now))
 if not clock:
  c.execute('INSERT INTO activity_clock VALUES(?,?,NULL,NULL)',(uid,now))
 if credited > 0:
  # Divide the credited interval across local midnights, including DST boundaries.
  start=now-credited
  while start < now:
   local=datetime.fromtimestamp(start,tz)
   next_day=datetime.combine(local.date()+timedelta(days=1),datetime.min.time(),tzinfo=tz).timestamp()
   stop=min(now,next_day)
   c.execute('INSERT INTO activity_daily VALUES(?,?,?) ON CONFLICT(user_id,day) DO UPDATE SET seconds=seconds+excluded.seconds',(uid,local.date().isoformat(),stop-start))
   start=stop
  c.execute('UPDATE activity_clock SET credited_until=?,last_active=?,last_lesson=? WHERE user_id=?',(now,now,lesson,uid))
 return credited

def summary(c, uid, now, tz):
 today=datetime.fromtimestamp(now,tz).date()
 starts={'today':today,'week':today-timedelta(days=today.weekday()),'month':today.replace(day=1),'year':today.replace(month=1,day=1),'all':None}
 rows=c.execute('SELECT day,seconds FROM activity_daily WHERE user_id=? ORDER BY day',(uid,)).fetchall()
 periods={key:{'seconds':round(sum(r['seconds'] for r in rows if start is None or start.isoformat()<=r['day']<=today.isoformat())), 'days':sum(1 for r in rows if r['seconds']>0 and (start is None or start.isoformat()<=r['day']<=today.isoformat()))} for key,start in starts.items()}
 clock=c.execute('SELECT last_active,last_lesson FROM activity_clock WHERE user_id=?',(uid,)).fetchone()
 return {'periods':periods,'lastActive':clock['last_active'] if clock else None,'lastLesson':clock['last_lesson'] if clock else None,'recentDays':[dict(day=r['day'],seconds=round(r['seconds'])) for r in rows if r['day']>=(today-timedelta(days=13)).isoformat()], 'timezone':str(tz)}
