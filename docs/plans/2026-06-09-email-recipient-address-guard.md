---
title: Email Recipient Address Guard
date: 2026-06-09
status: completed
execution: code
---

## Context

The `/mail/me` cron handler decides whether an incoming Gmail message should be
processed by comparing parsed `To:` header tuples against the automation
mailbox. It previously accepted either tuple element, which meant a display
name matching the configured mailbox could trigger automation even when the
actual recipient address was different.

## Goals

- Match automation recipients by normalized email address only.
- Keep the recipient decision importable and testable without App Engine,
  Gmail, OAuth, or a real mailbox.
- Preserve environment-backed `AUTOMATION_TO_EMAIL` configuration.
- Keep static baseline coverage for the App Engine handler path.

## Implementation

- Added `configured_to_email` and `message_addressed_to_automation` to
  `mail.rules`.
- Updated `mail/list.py` to call the shared recipient guard before sending
  automated replies.
- Added offline tests for case-insensitive address matches and display-name
  false positives.
- Extended `scripts/check-baseline.sh` to keep the new guard and tests in
  place.

## Verification

- `python3 -m unittest discover -s tests -p "test*.py"`
- `scripts/check-baseline.sh`
- `make check`
- `git diff --check`

Python 2/App Engine syntax checks are skipped locally when `python2` is not
installed.
