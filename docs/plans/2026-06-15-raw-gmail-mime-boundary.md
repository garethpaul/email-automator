---
title: Raw Gmail MIME Boundary
type: security
status: completed
date: 2026-06-15
---

# Raw Gmail MIME Boundary

## Problem Frame

`GetMimeMessage` base64url-decodes and parses the complete Gmail API `raw`
value before the existing 10,000-character rule-input bound applies. A large,
malformed, or non-string value can therefore consume memory or raise outside
the maintained offline boundary before sender, recipient, and rule checks run.

## Scope Boundaries

- Add a dependency-free Python 2/3 helper for the Gmail `raw` field and use it
  before MIME parsing.
- Cap decoded raw MIME messages at 25 MiB and reject impossible encoded lengths
  before allocating the decoded body.
- Reject non-string, empty, malformed base64url, invalid padding, and decoded
  over-limit values by returning no parsed message.
- Do not change Gmail queries, OAuth, memcache, sender/recipient policy,
  attachment behavior below the limit, delivery, dependencies, or App Engine
  configuration.
- Do not claim live Gmail, OAuth, App Engine, cron, or outbound-delivery
  execution from offline tests.

## Requirements

1. Validate the raw value type and base64url alphabet without silently ignoring
   invalid characters or whitespace.
2. Normalize only omitted trailing padding and reject impossible padding or
   encoded lengths.
3. Enforce the encoded preflight and decoded 25 MiB ceiling before MIME parser
   construction.
4. Contain malformed and oversized raw values inside `GetMimeMessage` without
   caching, rule evaluation, reservation, or delivery.
5. Add focused Python 2/3 tests, static contracts, documentation, completed
   evidence, and hostile mutations.

## Verification Plan

- Run the focused helper tests first and prove the integration contract fails
  before production wiring.
- Run the full Python 2.7 and Python 3 offline package gates from repository and
  external working directories.
- Compile maintained source/checker files and run `git diff --check`.
- Reject mutations for type, alphabet, padding, encoded and decoded size,
  integration containment, documentation, and completed-plan evidence.
- Audit generated artifacts, vendored files, secrets, and exact intended paths.

## Work Completed

- Added a dependency-free Python 2/3 decoder that validates raw value type,
  ASCII base64url alphabet, padding, encoded length, and decoded size.
- Capped decoded MIME input at 25 MiB and rejects impossible encoded sizes
  before allocating the decoded body.
- Routed Gmail raw values through the helper before `message_from_string` and
  contained invalid values as an unparseable message.
- Added focused tests, a source-order checker, build coverage, and synchronized
  repository guidance.
- Narrowed the configured-user-ID checker to the actual function boundary so
  independent `return None` containment does not weaken its identity contract.

## Verification Completed

- Python 2.7.18 and Python 3.12.8 each passed `make check` from the repository
  and from an external working directory with all 58 offline tests.
- Both focused raw-message suites passed all five cases; maintained source and
  tests compiled, both static checkers passed, shell syntax passed, and
  `git diff --check` passed.
- Ten isolated hostile mutations were rejected for type, alphabet, padding,
  encoded and decoded size, integration call and containment, configured-ID
  checker scope, documentation, and reopened plan status.
- No App Engine server, OAuth flow, Gmail API call, memcache service, cron
  route, live mailbox, or outbound delivery was executed or claimed.
