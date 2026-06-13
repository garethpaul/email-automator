---
title: Email MIME Charset Fallback
type: reliability
status: planned
date: 2026-06-13
---

# Email MIME Charset Fallback

## Status: Planned

## Problem Frame

Inbound HTML and plain-text MIME parts are decoded directly with their declared
charset. A missing or unknown charset can raise before sender, recipient,
self-reply, deduplication, and rule guards run, allowing one malformed message
to abort inbox processing.

## Scope Boundaries

- Preserve HTML-to-text extraction, plain-text preference behavior, sender and
  recipient checks, rule matching, deduplication, and outbound replies.
- Decode only text MIME parts; do not inspect or process attachments.
- Prefer a valid declared charset and use UTF-8 replacement decoding only when
  the charset is missing, unknown, or the payload contains malformed bytes.
- Do not change Gmail API requests, OAuth, App Engine handlers, dependencies, or
  configured automation identities.
- Do not claim live Gmail or App Engine execution.

## Requirements

- R1. Byte payloads with a valid declared charset must decode with that charset.
- R2. Missing and unknown charsets must fall back to UTF-8 replacement decoding.
- R3. Malformed bytes must be replaced rather than aborting message processing.
- R4. Existing string and absent payloads must normalize without exceptions.
- R5. Both HTML and plain-text extraction must use the shared decoder.
- R6. Dependency-free tests and the static gate must protect these cases,
  completed-plan evidence, and documentation.

## Implementation

1. Add a dependency-free MIME text decoder.
2. Use it for both HTML and plain-text message parts before existing extraction.
3. Add offline tests for valid, missing, unknown, malformed, string, and absent
   payloads.
4. Extend Make, static contracts, and maintenance documentation.

## Verification

- Focused MIME decoder tests
- `make lint`
- `make test`
- `make build`
- `make check`
- `make verify`
- External-working-directory `make check`
- `sh -n scripts/check-baseline.sh`
- `git diff --check`
- Isolated hostile mutations for missing fallback, strict malformed-byte
  decoding, bypassed HTML/plain integration, stale status, and missing evidence
  must each fail the checker.
