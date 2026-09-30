# Prelaunch QA — September 30, 2026

## Confirmed local results
- Isolated HTTP account tests pass: ownership isolation, parent/child login and signup, recovery rotation, session revocation, deletion, cross-origin rejection, throttling, conflicting saves, and malformed saved-data rejection.
- 90 lesson views and 270 starter/theme executions pass in simulated canvas. All 13 command additions, order/removal, 30 avatar indexes, stage layout limits, cancel/stop, scenes, messages and loop guards pass.
- Simulated state tests cover unsynced draft recovery, repeated-refresh conflict protection, successful save acknowledgement and path/theme preservation. These do not certify DOM behavior.
- Load fixture: 100 disposable pre-authenticated child sessions, not real children or production accounts. At 8/25/50/100 concurrent workers, 549 total reads completed without errors. After fixing connection backlog and database connection cleanup, all 100 concurrent saves completed and SQLite integrity_check returned ok. The final GitHub runner also recorded zero failed reads/saves and 100 saved records; save p95 was 198.9 ms. The first save burst dropped 19 connections. Test timings are from the development container, not a capacity guarantee for the shared Hostinger VPS. Login bursts are subject to separate rate limits and tested independently.

## Real browser results
Real Chromium integration tests run against the generated, hashed `dist` build on a disposable local server in GitHub Actions. Final run: https://github.com/MarvinAi5/pixel-quest-club/actions/runs/36772183994 — **PASSED**, including build, regression, browser and load steps.

Coverage includes all 90 lesson pages in all three themes; image loading; all 13 command controls and fields; typed output and line errors; run/stop/reset; collection and winning; tap and directional input; all 30 character and profile avatar choices; stage placement/erase; scene settings and messages; project download/import; guest persistence and shared-device mode; parent signup, child creation/login, online saves/reload, failed-save draft recovery, two-device conflict protection, optional unlinked signup, recovery-key reset, parent linking, PIN reset and deletion. Five touch viewports cover 600×1024, 1024×600, 800×1280, 1280×800 and 360×740, including narrow-screen workspace tabs. Screenshots and machine-readable browser/load results are available in the run's evidence artifact.

These are enumerated automated checks, not proof of every possible input, lesson solution, device or user sequence. Browser viewport simulation is not physical tablet testing.

## Faults fixed during testing
- Increased the server connection backlog and closed database connections reliably after a 100-save burst dropped 19 requests. Repeated load tests require 100/100 saved records and database integrity to pass.
- Made account-cap checks and insertion atomic, and reject malformed save structures before they reach the UI.
- Preserve unsynced child drafts through refresh, and stop automatic overwrites when another device has saved a newer version.
- Prevent canceled control actions from changing the new stage, and disarm finished tap sequences until Run is pressed again.
- Align typed-code limits with the interpreter, require a selected learning path before import, and support starter downloads under a deployment base path.
- Fix asset hashing that accidentally changed `style.cssText` in generated JavaScript and left the deployed build stuck loading. The build now checks every generated JavaScript file for syntax errors, and browser QA runs the deployable build.

Before inviting children: test actual Fire 7 / HD 8 in Amazon Kids, soft keyboard, sound, portrait/landscape, downloads and return visits. Viewport simulation does not emulate Fire memory, browser versions or parent controls. Test the deployed site's Caddy/Cloudflare headers and real browser paint before launch. Godot/Scratch instructions and Retroid export require external-tool/hardware tests; the browser suite does not certify them.

See .github/workflows/prelaunch-qa.yml and tests/browser_qa.cjs. Use only disposable non-production test accounts. The test suite never connects to the public learning domain or changes existing users.
