---
title: Email MIME Charset Fallback
type: reliability
status: completed
date: 2026-06-13
---

# Email MIME Charset Fallback

## Status: Completed

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

## Work Completed

- Added a dependency-free Python 2/3-compatible MIME text payload decoder.
- Preferred valid declared charsets and used UTF-8 replacement fallback for
  missing, unknown, malformed, string, and absent payload cases.
- Routed both HTML and plain-text extraction through the shared decoder while
  leaving attachments outside automated rule input.
- Added offline tests, Make integration, source contracts, and synchronized
  maintenance documentation without changing Gmail, OAuth, or reply logic.

## Verification Completed

- Python 3.12.8 and Python 3.14.0 each passed 6 focused tests.
- `make lint`, `make test`, `make build`, `make check`, and `make verify` passed
  under both available supported Python runtimes.
- External-working-directory `make check`, `sh -n scripts/check-baseline.sh`,
  and `git diff --check` passed.
- Six isolated hostile mutations were rejected: removed unknown-charset fallback,
  strict malformed-byte decoding, bypassed HTML integration, bypassed plain-text
  integration, stale completion status, and missing mutation evidence.
- No live Gmail or App Engine execution is claimed.
