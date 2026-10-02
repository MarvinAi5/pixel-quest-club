# Independent child accounts and family linking

Children can create their own saved accounts when `PQC_OPEN_CHILD_SIGNUP=1`. They choose an avatar, learning path, world and six-digit sign-in code (entered twice). The server assigns a unique club username. No real name, age, birthday or email is requested. Guest lessons still work without an account.

On successful signup/session verification, the current browser's guest lessons, notes and projects are carried into the new child account and saved online. Ordinary sign-in to an existing account does not import someone else's guest work. Keep the generated username and private recovery key safely; unlinked accounts cannot be recovered from an avatar or username alone.

## Connect after signup

1. Child signs in and opens **My profile → Connect my grown-up → Make a linking code**.
2. Child shows their username and linking code to their own grown-up. This eight-digit linking code is separate from the six-digit sign-in code.
3. Parent signs in on their own device and chooses **Grown-ups → Link an existing child**, then enters the child username and linking code.
4. Child returns to the connection screen and selects **Check for a connection request**. The screen names the parent account and explains progress access and code reset.
5. Child confirms **Yes, connect my grown-up**, or declines. Parent uses **Refresh** to see the confirmed child.

The invitation expires after 10 minutes and works once. A successful parent request consumes it and gives the child 10 minutes to confirm. Creating a fresh invitation cancels the previous code and pending request. A username alone does not allow linking. Pending requests do not grant progress access or code-reset authority. An account already linked cannot be transferred by this flow. The old parent-password-on-child-device endpoint has been removed.

Existing saved lessons/projects stay in the same account with the same ID and save revision. Their completion appears in the parent dashboard after linking. Active time is collected only after linking; prior unlinked or guest time is not reconstructed.

## Optional signup shortcut

Parent chooses **Make a family code** and gives it privately to their own children. A child enters this optional 12-digit code during account creation. Entering the code connects the new account directly to that parent; the form explains this before submission. Leaving it empty creates an unlinked account.

Family codes expire after one hour and support up to 20 successful signups. Generating a new code invalidates the previous one. **Cancel this family code** prevents future use without unlinking existing children. Invalid, expired, revoked or exhausted codes do not create an orphan account. Account creation and code-use consumption happen in the same SQLite transaction.

Both code types are stored as SHA-256 hashes, never as plaintext in the database. Expired invitations/requests are cleaned up during linking operations. Role checks, authenticated ownership, attempt limits, one-time consumption and transaction locks protect the linking flow. Recovery invalidates the account's outstanding invitations/requests. Existing account capacity limits still apply; there is no automatic orphan-account purge.

## VPS deployment

1. Back up the private SQLite database using the existing backup procedure before this backend/schema update. Preserve the data directory, secrets and existing accounts.
2. Pull the latest `main` from https://github.com/MarvinAi5/pixel-quest-club and follow `DEPLOYMENT.md`. Include the new `family_links.py` module, rebuild static files, and restart this site's backend through the established VPS procedure.
3. In the existing private environment file, set `PQC_OPEN_CHILD_SIGNUP=1`. Keep `PQC_PARENT_SIGNUP=0` if parent setup is complete; existing parent accounts can issue codes and link children while registration is closed. Preserve other private settings and assigned ports.
4. Server startup automatically adds `family_codes` and `family_requests` tables using `CREATE TABLE IF NOT EXISTS`. Existing user/save/activity tables and data are preserved. Confirm the backend starts successfully before declaring deployment complete.
5. Verify public HTTPS `/api/session` reports `openChildSignup:true`, existing parent sign-in works, and the homepage/sign-in dialog offers **Create my account**. Do not expose credentials, linking codes, cookies or recovery keys in public logs/reports.

## Live acceptance with disposable accounts

- Create a guest note/completion, then sign up as a child. Confirm PIN mismatch validation, selected avatar/path/world, recovery-key display, preserved guest work and save/reload.
- Make a child linking code. Parent submits username/code. Confirm the parent cannot see/reset the child while pending. Child declines; verify the account remains unlinked.
- Repeat with a fresh code and child confirmation. Refresh parent dashboard; verify existing completion/projects remain, only this parent sees progress, and code reset still works.
- Verify code reuse and stale/expired codes fail. Do not delete or modify real children's work.
- Generate a family code, create a second disposable child with it, verify immediate linking, then cancel the code and verify it no longer permits new connections.
- On actual Fire tablets, check signup form scrolling, avatar taps, PIN keyboard, portrait/landscape and both linking screens. Simulated browser viewports are separate evidence.
- Delete only disposable test children afterward, record deployed SHA/results and verify other hosted sites stay healthy. No public load flood is needed.

Automated coverage: `tests/test_family_links.py` exercises real HTTP signup/linking, role and family isolation, confirmation/decline, expiry/replay, hashes, guessing limits, cancellation and concurrent last-use consumption. `tests/link_browser.cjs` exercises signup and linking through real Chromium UI, guest preservation, reload and desktop/narrow/tablet screenshots. Both use disposable local databases, not production accounts.
