---
title: Email Automator Text Input Boundary
type: reliability
date: 2026-06-13
status: planned
---

# Email Automator Text Input Boundary

## Summary

Make rule matching and reply-subject generation fail closed for malformed
non-string Gmail metadata while preserving Python 2 string and Unicode input.

## Problem Frame

Sender, recipient, message-ID, and configured-address boundaries already reject
malformed structures before side effects. `bounded_email_body` still slices any
truthy object, and `reply_subject` calls `splitlines` on any truthy value. A
malformed decoded payload can therefore raise before the established offline
automation decision completes. The vision explicitly prioritizes more coverage
around email stripping, rule matching, and reply generation.

## Requirements

- R1. String and Unicode bodies must remain bounded to the first 10,000
  characters before tokenization.
- R2. Missing or non-string bodies must produce no tokens and a deterministic
  unknown reply instead of raising.
- R3. String and Unicode subjects must retain line-collapse and 200-character
  limits.
- R4. Missing or non-string subjects must produce the safe `Re:` fallback.
- R5. The implementation must stay compatible with Python 2 `basestring` and
  modern Python 3 offline tests.
- R6. Tests, source contracts, documentation, and completed verification must
  remain enforced by `make check`.

## Implementation Units

### U1. Normalize Rule Text Inputs

- **Files:** `mail/rules.py`, `tests/test_rules.py`
- **Goal:** Add one compatibility-aware text predicate and regressions for
  malformed bodies and subjects without changing valid reply output.
- **Covers:** R1, R2, R3, R4, R5

### U2. Enforce And Document The Boundary

- **Files:** `scripts/check-baseline.sh`, `README.md`, `SECURITY.md`, `VISION.md`,
  `CHANGES.md`, `AGENTS.md`
- **Goal:** Keep fail-closed text normalization and truthful verification
  evidence mandatory in the repository gate.
- **Covers:** R6

## Verification Plan

- Run focused rule tests and full `make check` on available Python 3.12 and
  Python 3.14 environments.
- Apply isolated mutations for removed type checks, restored unsafe slicing or
  `splitlines`, removed regressions, documentation drift, and incomplete plan
  evidence.
- Inspect exact paths, dependency files, credential-like additions, generated
  artifacts, and staged files before committing.
- Do not use OAuth credentials, Gmail APIs, App Engine services, or real inbox
  data.

## Risks

- Malformed values that previously crashed will now be treated as empty text,
  which intentionally favors no keyword match and a sanitized fallback subject.
- Live Gmail decoding and App Engine behavior remain outside the offline test
  boundary.
