---
title: Email Automation Self-Reply Guard
type: reliability
status: completed
date: 2026-06-13
---

# Email Automation Self-Reply Guard

## Summary

Reject inbound messages whose normalized sender address equals the configured
automation `From` address, even when that address is accidentally included in
the approved-sender allow-list. This prevents the automator from replying to
its own outbound messages and forming a reply loop.

## Priority

1. Prevent self-generated delivery loops before any message reservation or
   Gmail send side effect.
2. Preserve authorization-time environment refresh for both the approved
   sender list and automation `From` address.
3. Keep the maintained rule decision dependency-free and covered by offline
   tests on modern Python.

## Requirements

- R1. Sender authorization must compare normalized sender addresses against
  the current configured automation `From` address.
- R2. A sender equal to the automation address must fail closed even when it is
  present in `AUTOMATION_APPROVED_SENDERS`.
- R3. Self-sender rejection must occur before message-ID reservation and
  outbound delivery.
- R4. Case and surrounding whitespace must not bypass the comparison.
- R5. Other approved senders must retain existing authorization behavior.
- R6. The offline tests, static baseline, and project guidance must preserve
  the loop-prevention contract.

## Non-Goals

- Migrating the Python 2 App Engine or Gmail API runtime.
- Exercising a live mailbox, OAuth flow, memcache service, or outbound send.
- Changing reply content, subject normalization, recipient checks, or message
  deduplication semantics.
- Altering the conflict-stale debug-mode pull request.

## Implementation Units

### 1. Authorization-Time Self-Sender Rejection

Files: `mail/rules.py`

- Read the current validated automation `From` address during sender
  authorization.
- Reject the sender collection when any normalized address matches that
  automation address.
- Preserve the original approved sender address for legitimate replies.

### 2. Offline Regression Coverage

Files: `tests/test_rules.py`

- Cover direct authorization rejection when the automation address is
  accidentally approved.
- Cover the full `valid_email` decision and prove no reservation or send side
  effect occurs.
- Cover case and whitespace normalization while retaining a positive control
  for another approved sender.

### 3. Durable Contracts and Guidance

Files: `scripts/check-baseline.sh`, `README.md`, `SECURITY.md`, `VISION.md`,
`CHANGES.md`

- Add source/test contracts for the self-reply guard.
- Require completed plan status and actual verification evidence.
- Document the operational configuration boundary and remaining live-runtime
  limitations.

## Verification

- Python 3.12.8 with `PYTHONPATH` cleared: all 39 offline tests passed.
- Python 3.12.8 and 3.14.0: `make check` passed the static baseline, all 39
  tests, and bytecode compilation.
- Removing the self-sender comparison failed three executable regressions.
- Replacing validated normalized configuration with a raw environment read
  failed the static baseline.
- `git diff --check` passed.

## Work Completed

- Read the validated outbound address during each sender authorization check.
- Rejected matching normalized senders before message reservation or delivery.
- Added direct, both multi-sender orderings, authorization-refresh,
  normalization, positive-control, and no-side-effect regression coverage.
- Updated static contracts and project security and maintenance guidance.
