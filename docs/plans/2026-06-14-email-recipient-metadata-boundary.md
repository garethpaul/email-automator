---
title: Email Recipient Metadata Boundary
type: reliability
date: 2026-06-14
status: planned
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

## Planned Verification

- Focused `tests.test_rules` suite.
- Full location-independent `make check` on available Python runtimes.
- Isolated hostile mutations for container, address, valid-tail, side-effect,
  documentation, and completed-plan coverage.
- Exact intended-path, artifact, whitespace, conflict-marker, and changed-line
  credential-pattern audits.
