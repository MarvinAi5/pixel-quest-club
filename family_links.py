"""Short-lived family invitations. Only hashes of codes are stored."""
import hashlib, secrets, time

SCHEMA = '''
CREATE TABLE IF NOT EXISTS family_codes(
 token_hash TEXT PRIMARY KEY, user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
 kind TEXT NOT NULL CHECK(kind IN ('child','family')), expires REAL NOT NULL,
 uses INTEGER NOT NULL DEFAULT 0);
CREATE TABLE IF NOT EXISTS family_requests(
 child_id TEXT PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
 parent_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
 request_id TEXT UNIQUE NOT NULL, expires REAL NOT NULL);
'''

def code_hash(code):
 return hashlib.sha256(str(code).replace('-', '').replace(' ', '').encode()).hexdigest()

def cleanup(c, now=None):
 now=time.time() if now is None else now
 c.execute('DELETE FROM family_codes WHERE expires<=?',(now,))
 c.execute('DELETE FROM family_requests WHERE expires<=?',(now,))

def revoke(c, uid):
 c.execute('DELETE FROM family_codes WHERE user_id=?',(uid,))
 c.execute('DELETE FROM family_requests WHERE child_id=? OR parent_id=?',(uid,uid))

def issue(c, u, kind):
 if (kind=='child' and (u['role']!='child' or u['parent_id'])) or (kind=='family' and u['role']!='parent'):
  raise ValueError('This account cannot make that connection code.')
 now=time.time();cleanup(c,now)
 # Regeneration invalidates previous invitations and pending child requests.
 c.execute('DELETE FROM family_codes WHERE user_id=? AND kind=?',(u['id'],kind))
 if kind=='child':c.execute('DELETE FROM family_requests WHERE child_id=?',(u['id'],))
 digits=8 if kind=='child' else 12
 code=''.join(secrets.choice('0123456789') for _ in range(digits))
 expires=now+(600 if kind=='child' else 3600)
 c.execute('INSERT INTO family_codes VALUES(?,?,?,?,0)',(code_hash(code),u['id'],kind,expires))
 return dict(code='-'.join(code[i:i+4] for i in range(0,digits,4)),expires=expires)

def claim(c, parent, username, code):
 now=time.time();cleanup(c,now)
 child=c.execute("SELECT * FROM users WHERE username=? AND role='child'",(str(username).strip().lower(),)).fetchone()
 token=c.execute("SELECT * FROM family_codes WHERE token_hash=? AND kind='child' AND expires>?",(code_hash(code),now)).fetchone()
 if not child or child['parent_id'] or not token or token['user_id']!=child['id']:
  raise ValueError('That username and linking code did not match an available invitation. Ask your child for a new code.')
 c.execute('DELETE FROM family_codes WHERE token_hash=?',(token['token_hash'],))
 c.execute('INSERT OR REPLACE INTO family_requests VALUES(?,?,?,?)',(child['id'],parent['id'],secrets.token_hex(16),now+600))
 return dict(message='Request sent. Your child must open My profile → Connect my grown-up and confirm within 10 minutes.')

def pending(c, uid):
 cleanup(c)
 r=c.execute('SELECT family_requests.*,users.username FROM family_requests JOIN users ON users.id=family_requests.parent_id WHERE family_requests.child_id=?',(uid,)).fetchone()
 return dict(requestId=r['request_id'],parentUsername=r['username'],expires=r['expires']) if r else None

def resolve(c, child, request_id, accept):
 if not isinstance(accept,bool):raise ValueError('Choose whether to connect this grown-up.')
 now=time.time();cleanup(c,now)
 r=c.execute('SELECT * FROM family_requests WHERE child_id=? AND request_id=?',(child['id'],request_id)).fetchone()
 current=c.execute('SELECT * FROM users WHERE id=?',(child['id'],)).fetchone()
 if not r or not current or current['parent_id']:
  raise ValueError('This request is no longer available. Make a new linking code if needed.')
 if accept:
  c.execute('UPDATE users SET parent_id=? WHERE id=? AND parent_id IS NULL',(r['parent_id'],child['id']))
 c.execute('DELETE FROM family_requests WHERE child_id=?',(child['id'],))
 c.execute("DELETE FROM family_codes WHERE user_id=? AND kind='child'",(child['id'],))
 return c.execute('SELECT * FROM users WHERE id=?',(child['id'],)).fetchone()

def use_family_code(c, code):
 now=time.time();cleanup(c,now)
 token=c.execute("SELECT family_codes.* FROM family_codes JOIN users ON user_id=users.id WHERE token_hash=? AND kind='family' AND expires>? AND uses<20 AND users.role='parent'",(code_hash(code),now)).fetchone()
 if not token:raise ValueError('That family code is unavailable. Ask your grown-up for a fresh code, or leave it empty and connect later.')
 c.execute('UPDATE family_codes SET uses=uses+1 WHERE token_hash=?',(token['token_hash'],))
 return token['user_id']
