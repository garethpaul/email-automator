# Changes

## 2026-06-16

- Encapsulated message descendants are excluded from automated reply content.

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
