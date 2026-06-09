---
title: Email Configuration Address Validation
type: security
status: completed
date: 2026-06-09
---

# Email Configuration Address Validation

## Summary

Validate configured automation sender and recipient email addresses before they
participate in reply-rule decisions.

## Requirements

- R1. Ignore malformed `AUTOMATION_APPROVED_SENDERS` entries.
- R2. Reject malformed `AUTOMATION_TO_EMAIL` by disabling recipient matches.
- R3. Prevent CR/LF-injected configured addresses from reaching sender or
  recipient checks.
- R4. Keep the validation offline-testable without Gmail, OAuth, or App Engine.
- R5. Expose a `make build` compile gate for the rule module and tests.
- R6. Update README, VISION, CHANGES, SECURITY, and the baseline guard.

## Verification

- `python3 -m unittest discover -s tests -p "test*.py"`
- `scripts/check-baseline.sh`
- `make build`
- `make check`
- `git diff --check`
