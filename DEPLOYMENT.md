# Deployment overview

This project serves versioned static files through Caddy and sends /api/* to a private Python service. Run `python3 build.py` to validate the curriculum and produce dist/. Set PQC_NODE to the desired Node executable for syntax checks. Copy only validated dist/ into the webroot through your normal deployment hook. Preserve older hashed assets for existing tabs/rollback. Keep HTML no-cache and hashed assets immutable.

Templates in deploy/ are examples. Choose unused origin/backend ports and adapt paths and process ownership to your environment. The start script assumes an installed checkout at /srv/pixel-quest-club-site and private data/config at /var/lib/pixel-quest-club. Keep that directory outside the webroot and Git, with permissions restricted to the application user. Use your existing process supervision/watchdog and safe rollback pattern. Never overwrite another site's service or configuration.

Set Secure cookies when public HTTPS terminates at your reverse proxy. Configure a private parent setup code before enabling registration; disable parent registration after initial setup. Unlinked child registration is disabled by default. Friends can use guest lessons. Keep original Host headers when proxying /api so Origin checks work. Account payloads and API responses must not be cached. Take private SQLite backup snapshots through backup.py, and test restoration.

The hosted index uses external scripts compatible with script-src self. The downloadable standalone preview intentionally embeds scripts: use it locally, not as the hosted entry point. Audit real proxy/edge CSP headers, including dynamic inline styles. Verify actual browser rendering, controls, child saving and parent resets through public HTTPS; HTTP 200 alone does not establish success. Test Fire tablets and school access separately.

Private infrastructure handoffs, DNS/tunnel details, credentials, database exports and user information are excluded from the public repository. Obtain operator approval for changes to their hosting configuration. See QA.md for tests and limitations.
