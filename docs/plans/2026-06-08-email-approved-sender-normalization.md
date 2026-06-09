---
title: Email Approved Sender Normalization
date: 2026-06-08
status: completed
execution: code
---

## Context

The offline reply rules compare sender addresses against
`AUTOMATION_APPROVED_SENDERS` before sending an automated reply. The comparison
was case-sensitive, so a Gmail sender header with different casing could be
rejected even when the same address was configured.

## Goals

- Match approved sender email addresses case-insensitively.
- Preserve the original sender header address when building replies.
- Keep the rule logic importable and testable without App Engine or Gmail.
- Preserve duplicate-send cache coverage.

## Implementation

- Added `normalize_email_address` for configured and incoming sender addresses.
- Normalized `configured_from_users` entries at load time.
- Compared normalized sender addresses in `approved_sender`.
- Added an offline unit test for mixed-case approved sender headers.

## Verification

- `python3 -m unittest discover -s tests -p "test*.py"`
- `scripts/check-baseline.sh`
- `make check`
- `git diff --check`
