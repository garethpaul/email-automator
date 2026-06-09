# Changes

## 2026-06-09

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
