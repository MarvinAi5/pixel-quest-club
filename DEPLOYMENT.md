# Deployment overview

This project serves versioned static files through Caddy and sends /api/* to a private Python service. Run `python3 build.py` to validate the curriculum and produce dist/. Set PQC_NODE to the desired Node executable for syntax checks. Copy only validated dist/ into the webroot through your normal deployment hook. Preserve older hashed assets for existing tabs/rollback. Keep HTML no-cache and hashed assets immutable.

Templates in deploy/ are examples. Choose unused origin/backend ports and adapt paths and process ownership to your environment. The start script assumes an installed checkout at /srv/pixel-quest-club-site and private data/config at /var/lib/pixel-quest-club. Keep that directory outside the webroot and Git, with permissions restricted to the application user. Use your existing process supervision/watchdog and safe rollback pattern. Never overwrite another site's service or configuration.

Set Secure cookies when public HTTPS terminates at your reverse proxy. Configure a private parent setup code before enabling registration; disable parent registration after initial setup. Unlinked child registration is disabled by default. Friends can use guest lessons. Keep original Host headers when proxying /api so Origin checks work. Account payloads and API responses must not be cached. Take private SQLite backup snapshots through backup.py, and test restoration.

The hosted index uses external scripts compatible with script-src self. The downloadable standalone preview intentionally embeds scripts: use it locally, not as the hosted entry point. Audit real proxy/edge CSP headers, including dynamic inline styles. Verify actual browser rendering, controls, child saving and parent resets through public HTTPS; HTTP 200 alone does not establish success. Test Fire tablets and school access separately.

Private infrastructure handoffs, DNS/tunnel details, credentials, database exports and user information are excluded from the public repository. Obtain operator approval for changes to their hosting configuration. See QA.md for tests and limitations.

## Installation checklist for the hosting operator

Source: https://github.com/MarvinAi5/pixel-quest-club, branch `main`. The repository exists and contains the tested source. This is ready for a family deployment; production proxy/device checks below still need to pass. There is no Docker, systemd, Godot, Android SDK, or npm install required to serve the website. Scratch and Godot are learner tools on their computers, not server dependencies.

1. Inspect the operator's existing post-receive hook, Caddy supervision and rollback pattern before making changes. Check Python 3.12+, Node (use the approved Node 22 executable for builds), Git, Caddy, rsync, flock and cron. Choose two unused ports: one for Caddy and one for the API. The template ports are examples only.
2. Create the source checkout at `/srv/pixel-quest-club-site`, the bare mirror at `/srv/git/pixel-quest-club.git`, the static webroot at `/var/www/pixel-quest-club`, and private application storage at `/var/lib/pixel-quest-club`. Use a dedicated app user and permit Caddy to read the webroot. The app user must be able to read the checkout and write private storage. Restrict private storage to mode 700.
3. Initialize the mirror using the existing deployment convention, set its HEAD to `refs/heads/main`, and install the adapted deployment hook before pushing to it. GitHub pushes do not automatically deploy to this VPS: the operator must explicitly fetch GitHub main and push it to the bare mirror, or wire that same action into their existing automation. Do not establish a second manual webroot-copy deployment path.
4. In the hook, check out the exact incoming main commit and run:

   ```sh
   PQC_NODE=/usr/local/bin/node22 python3 build.py
   ```

   Use the actual approved Node path if different. The build creates `dist/`, including versioned lesson data, images, browser code and downloadable Scratch/Godot files. Publish only a successful `dist/` build through the hook. Preserve older hashed assets for open tabs and rollback; replace HTML with the new HTML. A failed build must leave the live webroot and backend unchanged. There is no Astro cache to clear.
5. Copy `deploy/app.env.example` to `/var/lib/pixel-quest-club/app.env`, owned by the app user and mode 600. Set `PORT` to the selected API port, `PQC_SECURE_COOKIES=1`, `PQC_PARENT_SIGNUP=1`, a private nonempty `PQC_PARENT_INVITE`, and `PQC_OPEN_CHILD_SIGNUP=0`. This is a shell-sourced file: quote values correctly and never commit it or print its contents. The example's empty invite is a placeholder, not a safe public setup.
6. Run the start script **as the app user**:

   ```sh
   sh /srv/pixel-quest-club-site/deploy/start.sh
   ```

   Probe `http://127.0.0.1:<api-port>/api/session`. A successful response should be JSON with no signed-in user. Install the absolute start-script path in that user's watchdog cron, following the existing hosting convention. `start.sh` starts a missing process; it deliberately refuses to kill an unhealthy existing process. It also does not reload a healthy process after an update: the deployment hook must implement a verified, site-specific stop/start and rollback. Avoid broad process-name kills and do not use systemctl.
7. Adapt `deploy/Caddyfile.example` with the actual origin/API ports and webroot. Its top-level global block belongs to the relevant Caddy instance and must not be pasted as a second global block into a shared configuration. Validate the resulting configuration with `caddy validate --config <config-path> --adapter caddyfile` before using the existing start/reload mechanism. Caddy binds by port, proxies `/api/*` to localhost, and preserves the original Host header. The API must not be externally exposed or edge-cached.
8. After the owner's approval required by their private hosting policy, route the website hostname through the existing tunnel to Caddy's origin port and configure DNS. Add the origin watchdog and existing health-check registration. Do not replace another site's route or restart unrelated services.
9. Perform the live acceptance checks below. Create the owner's parent account with the private setup code, add the children, then set `PQC_PARENT_SIGNUP=0` and restart only this site's backend through the established procedure. Confirm registration is closed afterward. Friends can still use guest lessons.

## Live acceptance checks before family use

- Probe the origin with the real hostname in the Host header, then the public HTTPS homepage and `/api/session`. Expect HTML and JSON respectively; a public API response must have `Cache-Control: no-store`.
- Open the public site in a real browser, inspect errors and blocked resources, and compare actual Cloudflare/Caddy content-security-policy headers. External scripts must load with `script-src 'self'`; dynamic styles must also be permitted by every applied policy. HTTP 200 alone is insufficient.
- Check HTML uses `no-cache`, versioned assets use immutable caching, and an unknown page returns the custom 404 with HTTP 404. Make sure Cloudflare does not cache accounts, API responses or cookie-bearing responses.
- Select all three paths and themes, run a browser activity, switch lessons, and download a Scratch checkpoint and the Godot reference. Verify images and tablet layouts.
- Through public HTTPS, create the parent/child test account, sign in, save a project, reload, and reset the child's code from the parent account. Confirm the previous child's session is revoked. Check Secure and HttpOnly session cookies. Use disposable test data and remove it through the supported parent controls.
- With the family, check real Fire tablets, Amazon Kids allow-list, screen rotation, touch input and the soft keyboard. Check school access separately. Physical Retroid installation/controller testing remains a learner-device task, not a server prerequisite.
- Record the deployed commit, live URL, assigned ports, watchdogs, backup arrangement and acceptance results. Report any unmet check rather than calling the site fully launched.

## Backups and restoration

Run snapshots as the app user, using a new private destination each time:

```sh
PQC_DATA_DIR=/var/lib/pixel-quest-club python3 /srv/pixel-quest-club-site/backup.py /private/backup/path/club-snapshot.sqlite
```

Choose real private backup storage outside the checkout and webroot. Back up before backend/schema updates, arrange scheduled snapshots and retain a copy outside the VPS. The app has no automatic orphan-account purge. The initial cap is 250 accounts, with a 200 KB saved payload cap per account; monitor disk use, logs and latency rather than treating that as a capacity guarantee.

Test restoration against an isolated private copy first. For production restoration, stop only this site's backend and pause its watchdog, preserve the current database and its SQLite sidecar files privately, restore the selected snapshot as `club.sqlite` with app ownership and mode 600, and ensure old `club.sqlite-wal`/`club.sqlite-shm` files cannot be reused with the restored database. Restart the backend/watchdog and verify sign-in and saved progress. Do not replace a live database while the service is running. Never publish or commit snapshots, credentials, child information or logs.

## Family dashboard update

This update adds private daily active-time totals, last active lesson, active-day counts, and a read-only completed-lesson checklist for each linked child. Parent authentication and the existing parent-child relationship authorize every read. Guests and unlinked accounts are not measured. The client sends bounded activity intervals only during visible, recently used lesson/help pages; the server caps credits by elapsed server time, ignores repeated packets, and prevents concurrent tabs from crediting the same interval twice. Reading time is approximate; idle time stops after two minutes. Scratch/Godot app time is excluded. Interrupted connections may lose intervals. There is no reconstruction of activity from before deployment.

Back up the database before this update. Deploy the new static assets AND restart this site's backend through the normal hook. Startup adds three activity tables without changing existing users/saves. Deleting a child also deletes their activity rows. No data export, new password, or account recreation is needed. Old open tabs need a reload to begin recording.

Set `PQC_TIMEZONE=America/Denver` privately for local dates (including daylight saving); week starts Monday. Set this before tracking begins and keep it stable: already stored daily dates do not move if the timezone is changed later. UTC is used separately for Cloudflare traffic dates. Existing child accounts created by the parent's Add a child account button are already linked. Existing unlinked child accounts can use My profile → Connect a grown-up account; the parent enters their own credentials.

Verify the parent sees only their children, each period button works, completed quests remain after reload, and activity time increases while a signed-in child uses a lesson. Confirm it pauses in hidden/idle tabs, guest use sends no activity, and another parent/child cannot read the owner's traffic. Use test accounts and avoid recording synthetic time into real children's records. The backend tests cover server caps, duplicates, tab overlap, local midnight, DST, upgrade preservation, and deletion; `tests/family_browser.cjs` exercises the real collector and dashboard in Chromium with disposable data.

### Optional owner-only Cloudflare panel

Set `PQC_OWNER_USERNAME` to the owner's **existing parent username** in private app.env; leave it empty to hide the owner panel. Do not hard-code the real username in Git. Only that authenticated parent can call `/api/site-traffic`; children and other parents are denied.

To connect, set `PQC_CF_ZONE_ID` and `PQC_CF_ANALYTICS_TOKEN` privately. Use a new read-only Zone Analytics token scoped to the Pixel Quest Club zone, not the existing broad DNS/tunnel token. Restart this backend through the normal deployment procedure. The server queries the official Cloudflare GraphQL endpoint for the last seven UTC dates, caches for five minutes, and returns daily requests, page views and daily unique estimates. No Cloudflare token or raw provider error reaches browsers. No client analytics beacon is installed. Missing configuration and API/plan/permission failure appear as clear status messages without interrupting family progress.

This initial integration is **zone-wide traffic including bots**, not a bot-filtered human count. Daily unique estimates must not be summed as unique people across days. The API and available datasets must be verified against the live token/plan by the operator; mocked provider tests are not live Cloudflare verification. If the existing bot-filtered report uses a different dataset or service, adapt that source separately after checking its metric definitions. Do not relabel unfiltered traffic as real people. Reference: https://developers.cloudflare.com/analytics/graphql-api/ .

## Sign-in session verification and Fire background reliability

Login now verifies `/api/session` with a second authenticated request before displaying a saved account. API fetches explicitly bypass browser caches. An expired parent session clears the stale family dashboard. New-account recovery keys are still shown even if session verification fails, so a cookie problem does not strand a newly created account.

`/api/session` reports only a safe state: `verified`, `missing-cookie`, or `unrecognized-session`. It never returns a cookie value. If the live password is accepted but child creation gets 401, use a disposable test parent to check the HTTPS round trip: login response sets a Secure/HttpOnly cookie; the next session request includes it; then child creation succeeds. Do not print, paste or log passwords, session tokens or recovery keys. `missing-cookie` means no named session cookie reached the backend; inspect browser storage/blocking and proxy request/response header handling. `unrecognized-session` means a named cookie reached it but no valid user session was found; check expiration, cookie parsing, consistent backend process/data directory, database access, and apex/www routing. The application tests establish the symptom and correct UI handling, not the cause of a particular production failure.

Backgrounds are now stage-sized 800×450 to reduce decoded memory on Fire tablets. Each has a JPEG fallback, including theme thumbnails. Failed background loads show an explicit status and a Reload background button, which preserves the child's code and layout. Publish the new JPEG files and updated hashed scripts together, keep old hashed assets for open tabs, and extend the Caddy versioned-asset matcher to include `jpg`. The lesson heading now prominently states Lesson N of 30. Verify Royal, Space and Halloween on the actual Fire tablet after reloading. A desktop screenshot or touch viewport is not physical Fire verification.

The play controls distinguish **Reset stage** (reset positions/score, keep the program) from **Start over** (empty the current scene's picture blocks and typed commands, keep the layout/other scene). **Undo start over** restores the cleared commands until new commands are entered. Undo is temporary in that browser tab, not a persistent backup. Lesson completion checkmarks are preserved. These controls are exercised in both the state/action and real-browser tests.
