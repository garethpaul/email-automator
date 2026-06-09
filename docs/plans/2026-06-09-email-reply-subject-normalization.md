---
title: Email Reply Subject Normalization
type: security
status: completed
date: 2026-06-09
---

# Email Reply Subject Normalization

## Summary

Normalize incoming message subjects before using them in automated reply
headers, preventing line breaks from being copied into outgoing `Re:` subjects.

## Requirements

- R1. Collapse CR/LF subject breaks into spaces before sending automated
  replies.
- R2. Cap normalized reply subjects so unusually long incoming subjects do not
  create oversized outbound headers.
- R3. Keep empty subjects valid by sending a minimal `Re:` subject.
- R4. Add offline rule tests for subject normalization and the `valid_email`
  send path.
- R5. Update README, VISION, CHANGES, and the baseline guard.

## Verification

- `python3 -m unittest discover -s tests -p "test*.py"`
- `scripts/check-baseline.sh`
- `make check`
- `git diff --check`
