---
title: Email Sender Identity Cardinality
type: security
date: 2026-06-13
status: planned
execution: code
---

# Email Sender Identity Cardinality

## Summary

Authorize an inbound email only when its parsed `From` metadata resolves to one
structurally valid sender identity. Multiple valid entries are ambiguous and
must fail closed instead of allowing the first allowlisted address to win.

## Requirements

- R1. Continue ignoring malformed sender entries so a later single valid entry
  remains eligible under the existing metadata-recovery contract.
- R2. Reject two or more structurally valid sender entries before allow-list
  matching, including duplicate addresses and approved-plus-unknown mixtures.
- R3. Preserve case-insensitive allow-list matching, authorization-time
  configuration refresh, and automation self-sender rejection.
- R4. Ensure ambiguous sender metadata reaches no message-ID reservation or
  outbound delivery side effect.
- R5. Add focused regressions and a mutation-sensitive baseline contract.

## Acceptance Examples

- A duplicate approved sender pair returns `None`.
- An approved sender paired with an unknown sender returns `None` in either
  order.
- Malformed entries followed by one approved sender still return that sender.
- `valid_email` rejects ambiguous sender metadata before reservation or send.

## Verification Plan

- Run the focused sender authorization and `valid_email` tests.
- Run the complete offline suite and `make check` on Python 3.12 and 3.14.
- Reject hostile mutations that restore first-match behavior, weaken the
  cardinality regressions, or remove completed plan evidence.
- Inspect exact paths, generated artifacts, dependency/workflow drift, and
  credential-like additions before commit.

## Non-Goals

- Changing the approved-sender configuration format or address syntax.
- Rejecting malformed entries when exactly one later valid sender is present.
- Exercising OAuth, Gmail, App Engine, or real mailbox data.
