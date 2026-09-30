# Prelaunch QA — September 30, 2026

## Confirmed local results
- Isolated HTTP account tests pass: ownership isolation, parent/child login and signup, recovery rotation, session revocation, deletion, cross-origin rejection, throttling, conflicting saves, and malformed saved-data rejection.
- 90 lesson views and 270 starter/theme executions pass in simulated canvas. All 13 command additions, order/removal, 30 avatar indexes, stage layout limits, cancel/stop, scenes, messages and loop guards pass.
- Simulated state tests cover unsynced draft recovery, repeated-refresh conflict protection, successful save acknowledgement and path/theme preservation. These do not certify DOM behavior.
- Load fixture: 100 disposable pre-authenticated child sessions, not real children or production accounts. At 8/25/50/100 concurrent workers, 549 total reads completed without errors. After fixing connection backlog and database connection cleanup, all 100 concurrent saves completed and SQLite integrity_check returned ok. The first save burst dropped 19 connections. Test timings are from the development container, not a capacity guarantee for the shared Hostinger VPS. Login bursts are subject to separate rate limits and tested independently.

## Real browser gate
The local environment cannot download Chromium and the cloud browser cannot open the local app. A GitHub Actions workflow runs disposable-server real Chromium tests and stores screenshots/results as prelaunch-qa-evidence. Until its result is reviewed, browser QA is PENDING. The suite exercises all 90 lesson views with all three themes, all block types, typed output/errors, run/stop/reset, tap/direction input, character/settings choices, scene/message routing, download/import, guest persistence, account flows and five touch viewports.

After that gate: test actual Fire 7 / HD 8 in Amazon Kids, soft keyboard, sound, portrait/landscape, downloads and return visits. Viewport simulation does not emulate Fire memory, browser versions or parent controls. Test the deployed site's Caddy/Cloudflare headers and real browser paint before launch. Godot/Scratch instructions and Retroid export require external-tool/hardware tests; the browser suite does not certify them.

See .github/workflows/prelaunch-qa.yml and tests/browser_qa.cjs. Use only disposable non-production test accounts. The test suite never connects to the public learning domain or changes existing users.
