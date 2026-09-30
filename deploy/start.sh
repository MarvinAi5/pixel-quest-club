#!/bin/sh
# Run as the dedicated app user. Install at /srv/pixel-quest-club-site/deploy/start.sh.
set -eu
umask 077
cd /srv/pixel-quest-club-site
# Private file outside the checkout/webroot. Never echo its contents.
set -a
. /var/lib/pixel-quest-club/app.env
set +a
export HOST=127.0.0.1
export PQC_DATA_DIR=/var/lib/pixel-quest-club
: "${PORT:?Set an unused backend port in app.env}"
: "${PQC_SECURE_COOKIES:?Set this to 1 behind Cloudflare HTTPS}"
exec 9>/var/lib/pixel-quest-club/start.lock
flock -n 9 || exit 0
# Health probe also avoids restarting a healthy application.
if python3 -c 'import os,urllib.request; urllib.request.urlopen("http://127.0.0.1:"+os.environ["PORT"]+"/api/session",timeout=3)' >/dev/null 2>&1; then exit 0; fi
if [ -f /var/lib/pixel-quest-club/app.pid ] && kill -0 "$(cat /var/lib/pixel-quest-club/app.pid)" 2>/dev/null; then
  echo 'Existing process is unhealthy; inspect it instead of starting a second process.' >&2
  exit 1
fi
nohup python3 server.py >>/var/lib/pixel-quest-club/app.log 2>&1 </dev/null 9>&- &
echo "$!" >/var/lib/pixel-quest-club/app.pid
