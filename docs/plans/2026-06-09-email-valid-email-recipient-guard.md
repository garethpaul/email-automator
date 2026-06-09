---
title: Email valid_email Recipient Guard
date: 2026-06-09
status: completed
execution: code
---

## Context

The `/mail/me` cron handler checked whether a message was addressed to the
automation mailbox before calling `valid_email`, but the core send-decision
helper itself only enforced approved sender and duplicate-message checks.

## Goals

- Require `valid_email` to verify the message recipient address before sending.
- Keep the recipient guard in the offline-testable rule layer.
- Preserve duplicate-send behavior for messages addressed to the automation
  mailbox.
- Add a regression test for approved senders addressed to someone else.

## Verification

- `python3 -m unittest discover -s tests -p "test*.py"`
- `scripts/check-baseline.sh`
- `make check`
- `git diff --check`
