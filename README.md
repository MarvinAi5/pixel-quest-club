# Pixel Quest Club — October 2026

90 lessons, three readiness-based paths, 30 avatars and three interchangeable project worlds. October 31 is the showcase. Base styling is cream/navy. No birth date is collected. Guest lessons are open; hosted child accounts are managed by parents initially.

## Local use
Requires Python 3.12+. Run `python3 server.py` and open http://127.0.0.1:8080. There are no Python package dependencies. The separately supplied standalone `Pixel-Quest-Club-October.html` is an offline guest preview; it must NOT be hosted on the Cloudflare site because it intentionally embeds scripts. Hosted files in public/ and dist/ use external scripts only.

## Caddy / tunnel deployment
Read [DEPLOYMENT.md](DEPLOYMENT.md) first. This deployment uses Caddy behind the existing Cloudflare tunnel, a private Python account/progress service, SQLite, start scripts and watchdog cron. It does not use Docker or systemd.

```sh
PQC_NODE=/usr/local/bin/node22 python3 build.py
```
The build validates all 90 lessons and JS syntax before changing dist/. Content-hashed assets allow immutable caching; HTML is no-cache. The operator should adapt their existing deployment hook to run this build. SQLite lives outside the deploy checkout and webroot. Do not deploy it through a static-only hook: /api must reach the backend for accounts to work.

## Learning and account boundaries
Story Makers (about 6–7) learn in the website. Game Makers (about 8–10) use browser practice then Scratch. Game Developers (about 11+ or ready) use browser practice then Godot. Every day includes instructions, help, a challenge and reflection. Browser typing uses a bounded teaching language, not GDScript or JavaScript. Completion is a child's self-check, not automatic grading of external projects.

Hosted saves have a 200 KB payload cap per account, with a default 250-account cap. Credentials are salted and hashed, sign-ins throttled, child codes six digits, recovery key/linked parent resets supported. No email-reset flow, uploads of photos, gallery, chat, analytics or advertising. Inactive accounts are not automatically purged: decide retention before enabling unlinked signup. Keep `PQC_OPEN_CHILD_SIGNUP=0` for family launch; friends use guest mode. This is a small-club prototype: security/privacy review is appropriate before broad enrollment.

## Verification
`python3 -m unittest discover -s tests -p 'test_*.py'`

`node tests/test_engine.cjs`

`node tests/test_views.cjs`

See QA.md. Physical Fire/Amazon Kids, live Cloudflare browser rendering, native Godot and Retroid export remain to be verified. The optional Godot reference is structurally checked only. Code, deploy scripts and public assets can go in GitHub; private environment files, database, logs and recovery keys must not.
