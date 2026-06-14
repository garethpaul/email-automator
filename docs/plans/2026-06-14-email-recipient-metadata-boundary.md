---
title: Email Recipient Metadata Boundary
type: reliability
date: 2026-06-14
status: completed
execution: code
---

# Email Recipient Metadata Boundary

## Summary

Fail closed when inbound recipient metadata is not a mapping-backed message,
list or tuple collection, address pair, or string-like address. Preserve valid
multi-recipient matching without letting malformed metadata crash automation.

## Requirements

- R1. `message_addressed_to_automation` must return `False` for non-dictionary
  messages and non-list/tuple recipient collections.
- R2. Malformed recipient entries and non-string-like addresses must be ignored
  without raising.
- R3. A later valid automation address in an otherwise parseable collection must
  continue to match case-insensitively.
- R4. `valid_email` must reject malformed recipient metadata before reserving a
  message ID or sending a reply.
- R5. Add executable and static contracts, completed evidence, and project
  guidance without changing sender, subject, body, MIME, or deduplication rules.

## Work Completed

- Added fail-closed message and recipient-container validation.
- Ignored malformed recipient entries and non-string-like addresses without
  preventing a later valid automation address from matching.
- Added direct helper regressions and a full `valid_email` no-side-effect case.
- Extended the static baseline and project guidance.

## Verification

- Python 3.12.8: focused rule discovery passed 47 tests; the full repository
  gate passed 53 tests including MIME payload regressions.
- Six hostile mutations were rejected: message-container guard removal,
  address guard removal, valid-tail regression removal, side-effect regression
  removal, documentation removal, and planned-status restoration.
- Full location-independent `make check` passed 53 tests on Python 3.12.8 and
  Python 3.14.0, and passed through the absolute Makefile path from an external
  working directory.
- Exact intended-path, artifact, whitespace, conflict-marker, and changed-line
  credential-pattern audits passed before commit.
