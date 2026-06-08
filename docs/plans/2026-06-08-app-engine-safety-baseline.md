---
title: Email Automator App Engine safety baseline
date: 2026-06-08
status: completed
execution: code
---

## Context

`email-automator` is a Python 2 Google App Engine Gmail automation prototype.
It has OAuth storage, cron-triggered mailbox scans, approved-sender reply rules,
and vendored App Engine-era libraries. The current environment does not include
the legacy App Engine SDK, so full runtime tests are not available here.

## Goals

- Preserve the Python 2 App Engine prototype without starting a platform
  migration.
- Disable webapp debug output unless explicitly enabled.
- Require HTTPS and App Engine login boundaries for auth and mail routes.
- Restrict `/mail/me` to admin/cron access.
- Move OAuth and mailbox configuration placeholders into environment variables.
- Remove the committed cron `userId` query placeholder.
- Add static verification that can run without live Gmail credentials.

## Work Items

- Add `app.yaml` environment placeholders for OAuth, debug, and automation
  mailbox settings.
- Split App Engine handlers so `/auth`, `/mail/.*`, and `/mail/me` have
  explicit login and HTTPS requirements.
- Gate `main.py` debug mode behind `APP_DEBUG=1`.
- Read OAuth client id/secret and automation mailbox settings from environment
  variables.
- Fail clearly when a mail route has no automation user id or stored Gmail
  credentials, including `/mail/check`.
- Return JSON from the label check route instead of writing a Python list under
  an `application/json` response.
- Extend the baseline script and docs with deployment safety checks.

## Verification

- `scripts/check-baseline.sh`
- `python3 -m unittest discover -s tests -p "test*.py"`
- `python2 -m py_compile main.py mail/auth.py mail/check.py mail/list.py mail/rules.py`
- `git diff --check`

## Non-Goals

- Migrating to Python 3, App Engine second generation, or modern Google auth.
- Running Gmail API calls or requiring real OAuth credentials in default tests.
- Changing reply rules beyond the offline rule baseline.
