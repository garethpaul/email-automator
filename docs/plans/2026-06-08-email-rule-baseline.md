---
title: Email Automator offline rule baseline
date: 2026-06-08
status: completed
execution: code
---

## Context

Email Automator is a Python 2 Google App Engine/Gmail API prototype. Most of the app depends on App Engine SDK modules and real OAuth credentials, but the reply-rule logic can be tested offline. The current rule module imports Gmail sending code at module import time, which makes local tests fail outside the legacy runtime, and one unknown-message fallback tells users to dial 911.

## Goals

- Make reply-rule helpers importable in modern local Python without App Engine or Gmail dependencies.
- Keep live Gmail sending behind the existing `sendEmail` path.
- Add deterministic offline tests for keyword matching, unknown replies, approved sender checks, and duplicate-cache behavior.
- Remove unsafe emergency-service language from automated fallback replies.
- Document that default tests do not access Gmail or real mailbox data.

## Scope Boundaries

- Do not migrate the app off Python 2 App Engine in this pass.
- Do not change OAuth scopes, Gmail API calls, cron behavior, or vendored dependencies.
- Do not add real credentials, mailbox fixtures, or live Gmail integration tests.

## Implementation Units

### U1: Pure rule helpers

Files: `mail/rules.py`, `tests/test_rules.py`

Approach: Defer importing `mail.send` until a live send is requested, provide a local memcache fallback for offline tests, add approved-sender helper functions, and allow deterministic choice injection for tests.

Verification: Unit tests import `mail.rules` under Python 3 without App Engine SDK modules and assert that a duplicate approved message is not sent twice.

### U2: Safe fallback language

Files: `mail/rules.py`, `tests/test_rules.py`

Approach: Replace the emergency-service fallback with neutral language and test that generated unknown replies do not mention 911.

Verification: Offline tests assert the unknown reply is deterministic and excludes emergency-service wording.

### U3: Local verification baseline

Files: `scripts/check-baseline.sh`, `README.md`, `VISION.md`, `CHANGES.md`

Approach: Add a small test runner for offline rule tests and source guards for credential and mailbox safety notes.

Verification: `scripts/check-baseline.sh`, `python3 -m unittest discover -s tests -p 'test*.py'`, and `git diff --check` pass.
