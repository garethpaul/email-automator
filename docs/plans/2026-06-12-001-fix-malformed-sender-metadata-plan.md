---
title: Malformed Sender Metadata Guard
type: fix
date: 2026-06-12
---

# Malformed Sender Metadata Guard

## Summary

Make the automated-send authorization path reject malformed inbound sender
metadata instead of raising while destructuring untrusted address entries.

## Problem Frame

`approved_sender` assumes every item in `msg['from']` is a two-item sequence.
A missing entry, short tuple, long tuple, or other malformed value can raise
`TypeError` or `ValueError` before the message is safely rejected.

## Prioritized Engineering Backlog

1. Guard malformed sender metadata in the authorization path and add offline
   regressions in this change.
2. Remove import-time caching of `AUTOMATION_APPROVED_SENDERS` so configuration
   reads have one consistent lifecycle in a future focused change.
3. Plan the App Engine `webapp2`, vendored OAuth, and Gmail client migration as
   a separate compatibility project with deployment-level verification.

## Requirements

- R1. `approved_sender` must ignore malformed sender entries without raising.
- R2. A later valid approved sender entry must still be recognized after an
  earlier malformed entry.
- R3. `valid_email` must reject malformed-only sender metadata without
  reserving a message ID or invoking the outbound sender.
- R4. Existing address normalization and approved-sender behavior must remain
  unchanged for valid two-item entries.
- R5. Tests, the maintenance baseline, README, SECURITY, VISION, and CHANGES
  must preserve the defensive sender-metadata contract.

## Key Technical Decisions

- **Validate entry shape before use:** Extract the address with indexed access
  inside a narrow exception guard, matching the existing recipient parser.
- **Ignore malformed entries rather than rejecting the whole list:** Gmail
  metadata may contain multiple parsed addresses, so a valid later entry should
  remain eligible.
- **Keep authorization failure closed:** A malformed-only sender list returns
  `None`, causing `valid_email` to stop before deduplication or delivery.

## Implementation Units

### U1. Harden approved sender extraction

- **Goal:** Skip entries that cannot provide a usable address value.
- **Files:** `mail/rules.py`
- **Verification:** Focused `approved_sender` unit tests.

### U2. Cover authorization-path behavior

- **Goal:** Test malformed values, a valid entry after malformed metadata, and
  a full `valid_email` rejection with no side effects.
- **Files:** `tests/test_rules.py`, `scripts/check-baseline.sh`
- **Verification:** `python3 -m unittest discover -s tests -p "test*.py"` and
  `make check`.

### U3. Document malformed metadata handling

- **Goal:** Keep public security and maintenance guidance aligned with the
  fail-closed behavior.
- **Files:** `README.md`, `SECURITY.md`, `VISION.md`, `CHANGES.md`
- **Verification:** `make check` and `git diff --check`.

## Acceptance Examples

- AE1. Given `from: [None, ("Only",)]`, when `approved_sender` runs, then it
  returns `None` without raising. Covers R1.
- AE2. Given a malformed entry followed by an approved two-item entry, when
  authorization runs, then the approved address is returned. Covers R2.
- AE3. Given malformed-only sender metadata and a valid message ID, when
  `valid_email` runs, then it returns false, sends nothing, and leaves the ID
  unreserved. Covers R3.

## Scope Boundaries

- Do not change the configured approved-sender allowlist lifecycle in this
  pass.
- Do not broaden the accepted configured email syntax.
- Do not modernize App Engine, OAuth, or Gmail dependencies in this change.

## Risks And Mitigations

- Overly broad exception handling could hide unrelated bugs. Catch only entry
  indexing and normalization shape errors.
- Treating arbitrary strings as address pairs could authorize character-based
  data. Require a two-item non-string sequence before comparing the address.
