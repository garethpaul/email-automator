---
title: Email Automator Runtime Verification Matrix
type: reliability
status: completed
date: 2026-06-14
---

# Email Automator Runtime Verification Matrix

## Status: Completed

## Problem Frame

Portable tests cover rule normalization, text decoding, sender and recipient
metadata, configured mailbox identity, message deduplication, and self-reply
prevention. The host has Python 2.7 but no App Engine development server, so
OAuth, Gmail API, memcache, cron, inbound handlers, and outbound delivery
remain unexecuted.

## Scope Boundaries

- Do not change application, rules, handlers, dependencies, App Engine config,
  OAuth, Gmail, memcache, cron, or delivery behavior. Test-only compatibility
  shims may be added to execute the existing offline suite on Python 2.7.
- Do not add OAuth credentials, tokens, mailbox identifiers, message contents,
  addresses, cookies, datastore data, screenshots, or logs.
- Do not claim App Engine, OAuth, Gmail, memcache, cron, or outbound delivery
  execution from portable unit, compile, or static checks.
- Do not merge or close stacked pull requests without explicit authorization.

## Requirements

- R1. Add an exact-commit matrix for legacy runtime setup, app configuration,
  OAuth start/callback, mailbox listing, inbound mail, rule matching, dedupe,
  self-reply prevention, outbound delivery, cron, memcache, and restart behavior.
- R2. Require isolated synthetic mailboxes and messages, sanitized evidence,
  and explicit `pass`, `fail`, `blocked`, or `not run` status.
- R3. Keep portable Python 2/3 tests, local App Engine evidence, OAuth/Gmail
  sandbox evidence, and outbound delivery evidence separate.
- R4. Add mutation-sensitive contracts for the matrix, project guidance, and
  completed plan evidence.
- R5. Make the existing offline tests executable on Python 2.7 without changing
  production behavior or weakening assertions.

## Implementation

1. Add the runtime matrix with all scenarios marked `not run`.
2. Link it from project guidance and document evidence sanitization.
3. Extend the deterministic checker with scenario, status, and plan contracts.
4. Run focused Python 2/3, external-directory, mutation, artifact, and secret
   gates.

## Verification

- `sh -n scripts/check-baseline.sh`
- Python 2.7 and Python 3 offline tests and compilation
- `make check` from repository and external working directories
- Python static checker compilation and execution
- Isolated hostile documentation mutations
- Exact diff, generated-artifact, and secret-pattern audits

## Work Completed

- Added a 14-scenario exact-head runtime matrix covering legacy setup, app and
  cron configuration, OAuth, Gmail listing and MIME fetch, inbound handling,
  sender/recipient identity, rule construction, memcache dedupe, self-reply
  prevention, outbound delivery, and restart behavior.
- Required isolated synthetic mailboxes, messages, and OAuth accounts,
  sanitized evidence, exact commit and pull-request attribution, and explicit
  `pass`, `fail`, `blocked`, or `not run` statuses.
- Kept portable Python 2/3 tests, local App Engine evidence, OAuth/Gmail
  sandbox evidence, memcache evidence, and delivery evidence separate.
- Added test-only Python 2.7 compatibility for `subTest`, dynamic module
  loading, UTF-8 source decoding, and unicode expectations.
- Added mutation-sensitive contracts without changing application, handlers,
  dependencies, configuration, OAuth, Gmail, memcache, cron, or delivery behavior.

## Verification Completed

- `sh -n scripts/check-baseline.sh` passed.
- Python 2.7.18 and Python 3.12.8 offline tests and source compilation passed.
- `make check` and direct static gates passed from repository and external
  working directories.
- The configured-user-ID Python checker compiled and passed.
- Fourteen isolated hostile documentation and test-compatibility mutations
  were rejected.
- No App Engine server, OAuth flow, Gmail API call, memcache service, cron
  route, inbound mail handler, or outbound delivery scenario was executed; all
  14 runtime scenarios remain truthfully marked `not run`.
