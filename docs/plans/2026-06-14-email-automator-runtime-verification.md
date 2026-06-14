---
title: Email Automator Runtime Verification Matrix
type: reliability
status: in_progress
date: 2026-06-14
---

# Email Automator Runtime Verification Matrix

## Status: In Progress

## Problem Frame

Portable tests cover rule normalization, text decoding, sender and recipient
metadata, configured mailbox identity, message deduplication, and self-reply
prevention. The host has Python 2.7 but no App Engine development server, so
OAuth, Gmail API, memcache, cron, inbound handlers, and outbound delivery
remain unexecuted.

## Scope Boundaries

- Do not change application, rules, handlers, dependencies, App Engine config,
  OAuth, Gmail, memcache, cron, or delivery behavior.
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
