# Changes

## 2026-06-08

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
