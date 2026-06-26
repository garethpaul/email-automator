# Changes

## 2026-06-26 07:25 PDT - P1 - Isolate malformed Gmail get responses

### Summary

Prevented malformed Gmail per-message get responses from raising before raw MIME
validation and aborting the remaining mailbox scan.

### Work completed

- Added a dependency-free helper that exposes `raw` only from mapping responses.
- Routed `GetMimeMessage` through the helper and the existing strict base64url
  decoder, preserving per-message `ValueError` rejection.
- Added pure Python 2/3 response-shape tests and an integration source contract.
- Added plan, source, test, and guidance preservation contracts.

### Threads

- Started: Gmail get response boundary — malformed per-message isolation.
- Continued: existing strict raw MIME and mailbox fail-closed boundaries.
- Stopped: none.

### Files changed

- `mail/raw_message.py` — validates get response container shape.
- `mail/list.py` — removes the direct unvalidated `message.get('raw')` access.
- `tests/test_raw_message.py` and `tests/test_integration_contracts.py` — cover
  helper behavior and handler integration.
- Repository guidance, plans, and baseline contracts — preserve the boundary.

### Validation

- Red phase: focused tests failed on the missing helper and direct response
  dereference.
- Green phase: 13 focused raw-message and integration tests passed.
- Local and external-directory `make check` passed with 97 tests and all 77
  authoritative Python files verified.
- The pinned Python 2.7.18 container passed 97 tests with one expected skip and
  verified all 77 authoritative Python files.
- Two isolated hostile mutations removing the mapping guard or restoring the
  direct response dereference were rejected.
- Push and pull-request Check runs `28244650357` and `28244652748` passed
  Python 3.10/3.12/3.14, the pinned Python 2.7.18 suite, and dependency audit on
  `e8334ecb5f3623becdd1a50e39c20a25a6a6d232`.
- CodeQL Actions and Python analysis passed in run `28244650912` on the same
  implementation head.
- `codex review --base origin/master` was attempted and skipped after the Codex
  API returned HTTP 401 for both WebSocket and HTTPS transports.

### Bugs / findings

- P1: a non-mapping Gmail `messages.get` result raised `AttributeError` before
  existing raw MIME guards and stopped processing later mailbox messages.

### Blockers

- Live App Engine, OAuth, Gmail, and mailbox behavior remains outside the
  credential-free offline suite. Codex review authentication is unavailable;
  local, mutation, and hosted checks provide closeout evidence.

### Next action

- Push this evidence-only closeout and merge PR #24 only after its exact final
  head passes hosted checks.

## 2026-06-25 21:45 PDT - P1 - Bound Gmail list response shapes

### Summary

Made mailbox scans fail closed with a stable empty iterable when Gmail returns
a malformed list response or the existing HTTP error boundary is reached.

### Work completed

- Added a dependency-free Python 2/3 helper that accepts only a mapping with a
  list or tuple `messages` field and preserves the existing 30-message bound.
- Routed `ListMessagesWithLabels` through the helper before message-ID, cache,
  MIME, and reply processing.
- Made the handled Gmail `HttpError` branch return `[]` instead of implicit
  `None`.
- Added executable shape regressions, integration contracts, and synchronized
  repository guidance.

### Threads

- Continued: credential opt-in setup — reviewed and allowed isolated PR #22 to
  merge before rebasing this runtime change onto its exact master commit.

### Files changed

- `mail/list_response.py` — dependency-free response validation and bound.
- `mail/list.py` — validated iteration and stable HTTP-error return.
- `tests/test_list_response.py` and `tests/test_integration_contracts.py` —
  offline regressions and handler integration contracts.
- Repository plans, guidance, and baseline contracts — preserve the boundary.

### Validation

- Focused helper tests failed first because the module did not exist.
- The integration contract then failed on the direct unvalidated response
  dereference and implicit `None` error return.
- The full local gate passed with 94 tests and 77 authoritative Python files.
- The pinned Python 2.7.18 container passed the same 94-test suite with one
  expected skip and verified all 77 source entries.
- Hostile removal of the response mapping guard, 30-message bound, and stable
  HTTP-error iterable were each rejected by focused tests.

### Bugs / findings

- P1: malformed Gmail list responses or handled list HTTP failures could abort
  cron/mail handlers before per-message fail-closed guards ran.

### Blockers

- Live App Engine, OAuth, Gmail, and memcache behavior remains outside the
  credential-free offline suite.

### Next action

- Complete mutation, full runtime-matrix, hosted, and exact-head review gates.

## 2026-06-25

- Added a canonical credential and opt-in guide covering platform credentials,
  OAuth client values, datastore-owned tokens, all automation settings, and the
  exact Gmail modify/send scopes requested by the application.
- Added an ignored `app.local.yaml` convention with a required
  `git check-ignore` preflight so tracked `app.yaml` retains empty placeholders.
- Documented explicit authorization and synthetic-mailbox checks that must pass
  before cron is enabled, without claiming any live legacy runtime execution.

## 2026-06-25

- Fixed the tracked cache helper's Python 2/3 syntax and duration forwarding.
- Added authoritative tracked/deployed Python surface verification across the
  required Python 2 and Python 3 runtime families.
- Updated worktree discovery to honor Git ignore rules while still rejecting
  unignored, undeclared Python source files.
- Stopped deleting ignored local bytecode during checks and made mutation
  fixtures copy only tracked or unignored repository files.
- Cleared inherited Make control variables before isolated runtime checks so
  command-line Python overrides do not leak into their sanitized PATHs.
- Limited recursive emergency-wording checks to Python source files so ignored
  bytecode and cache directories cannot affect repository verification.
- Passed focused authority tests after Codex identified the ignored local
  environment regression.

## 2026-06-19

- Bounded MIME traversal depth, MIME part count, and decoded text extraction.
- Rejected duplicate multipart/related roots and all encapsulated `message/*`
  descendants from automated reply content.
- Converted parser recursion and missing-safe-body failures into per-message
  rejection so one hostile message cannot abort the mailbox scan.
- Centralized reply construction with Gmail base64url serialization and CR/LF/
  NUL header rejection.
- Made the vendored httplib2 TLS socket wrapper select the TLS protocol
  explicitly instead of inheriting the interpreter default.

## 2026-06-16

- Encapsulated message descendants are excluded from automated reply content.
- Multipart/related resources are excluded from automated reply content; only the MIME-defined root is traversed.

## 2026-06-15

- Automated reply content uses only inline MIME text parts; attachments and
  named file parts are excluded.
- Raw Gmail MIME values reject noncanonical pad bits before MIME parsing.
- Raw Gmail MIME values are strictly base64url-validated and capped at 25 MiB before MIME parsing.

## 2026-06-14

- Added an exact-head Email Automator runtime verification matrix that
  separates portable tests from sanitized App Engine, OAuth, Gmail, memcache,
  cron, inbound-handler, and outbound-delivery evidence.
- Whitespace-only AUTOMATION_USER_ID values are rejected as missing configuration.
- Made `AUTOMATION_USER_ID` authoritative so request parameters cannot select
  another stored Gmail credential key.
- Made malformed recipient metadata fail closed without crashing, reserving a
  message ID, or sending an automated reply.

## 2026-06-13

- Made all Makefile verification recipes resolve paths from the loaded
  Makefile so the offline gate works outside the repository directory.
- Normalized missing, unknown, and malformed MIME charsets with UTF-8 replacement
  fallback before HTML or plain-text rule input is extracted.
- Malformed non-string message bodies and subjects now normalize to empty text
  so rule matching and reply-subject generation fail closed instead of raising.
- Ambiguous multi-sender metadata now fails closed before message reservation
  or automated reply delivery.
- Reject the current outbound automation address as an inbound approved sender
  to prevent self-generated reply loops before reservation or delivery.
- Added normalized, authorization-time refresh and no-side-effect regressions.

## 2026-06-12

- Switched Gmail MIME retrieval and parsed-message caching from thread IDs to
  validated Gmail message IDs so later messages cannot reuse stale thread
  content.
- Added offline malformed-summary tests and static contracts that reject
  thread-ID fetch/cache regressions.
- Hardened approved-sender extraction so malformed sender metadata is ignored
  instead of raising in the automated-send authorization path.
- Added offline regressions proving malformed-only messages fail closed without
  reserving their message ID or invoking delivery.
- Read validated approved-sender configuration at authorization time so
  allow-list additions and removals apply without a process restart.
- Added a rotation regression and a static guard against restoring an
  import-time sender snapshot.
- Raised WebOb to the Python 2-compatible 1.8.10 security floor and removed
  unused virtualenv tooling from the application requirements.
- Added a pinned, credential-free dependency-audit job that checks the explicit
  legacy pins without installing or resolving the Python 2 runtime on Python 3.
- Fixed both hosted checkouts to disable persisted credentials and use the
  fixed Ubuntu 24.04 runner.

## 2026-06-10

- Reserved normalized message IDs atomically before outbound Gmail sends so
  concurrent workers cannot both perform the same side effect.
- Released message reservations after false or raised send failures so later
  retries remain possible.
- Added re-entrant concurrency and failure-path regression coverage.
- Added a GitHub Actions workflow that runs the offline `make check` baseline
  on Python 3.10, 3.12, and 3.14.
- Pinned workflow actions by commit, restricted repository permissions to
  read-only, enabled stale-run cancellation, and bounded jobs to five minutes.
- Extended the baseline checker and docs to require the hosted CI verification
  path.

## 2026-06-09

- Normalized and length-bounded inbound message IDs before duplicate-send cache
  key use.
- Limited automated reply rule matching to a bounded inbound body prefix.
- Validated outbound automation From addresses before creating Gmail messages.
- Validated configured automation sender and recipient email addresses before
  reply-rule matching.
- Added a `make build` compile gate for the offline rule module and tests.
- Normalized automated reply subjects to one line before sending.
- Required `valid_email` to enforce automation recipient-address matching before
  sending replies.
- Matched automation recipients by normalized `To:` address only, preventing
  display-name matches from triggering replies.
- Added offline tests and a baseline guard for recipient-address matching.

## 2026-06-08

- Added a root `make check` wrapper for the offline rule and safety baseline.
- Matched approved sender email addresses case-insensitively while preserving
  the original sender header address for replies.
- Made reply-rule helpers importable without App Engine/Gmail dependencies.
- Added deterministic offline tests for keyword replies, unknown replies,
  approved sender checks, local cache checks, and duplicate-send prevention.
- Made keyword matching tolerate ordinary punctuation in email text.
- Removed emergency-service wording from unknown automated replies.
- Added a baseline verification script for local rule changes.
- Gated App Engine debug mode behind `APP_DEBUG=1`.
- Added HTTPS/login route guardrails for auth and mail handlers, with `/mail/me`
  restricted to admin/cron access.
- Moved OAuth and automation mailbox placeholders to environment-backed
  settings and removed the committed cron `userId` placeholder.
