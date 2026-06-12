---
title: Approved Sender Configuration Refresh
type: fix
status: completed
date: 2026-06-12
---

# Approved Sender Configuration Refresh

## Summary

Read the approved-sender allow-list at authorization time instead of caching it
when `mail.rules` is imported.

## Problem Frame

`configured_to_email` and `configured_from_email` read environment-backed
configuration for each send decision, but `AUTOMATION_APPROVED_SENDERS` is
copied into the global `from_users` list at import time. A process therefore
continues authorizing removed senders and rejecting newly approved senders
until it restarts, which makes security configuration changes inconsistent and
hard to reason about.

## Prioritized Engineering Work

1. **Refresh approved senders per authorization decision (this change).** Remove
   the import-time snapshot, call the existing validated configuration helper
   from `approved_sender`, and prove rotations take effect immediately.
2. **Bound raw Gmail MIME parsing (follow-up).** The live message path decodes
   and parses the complete API `raw` body before the existing 10,000-character
   rule-body bound. Add a separate size and malformed-payload boundary in an
   offline-testable helper.
3. **Modernize the App Engine/Gmail stack (follow-up).** Migrate Python 2,
   `webapp2`, vendored OAuth, and the old discovery client only as a dedicated
   compatibility project with deployment-level verification.

## Requirements

- R1. `approved_sender` must call `configured_from_users` for the current
  decision and must not depend on a module-level sender snapshot.
- R2. Replacing the environment allow-list must immediately reject a removed
  sender and accept a newly approved sender without reimporting the module.
- R3. Invalid configured addresses must continue to fail closed.
- R4. Existing case-insensitive sender matching and malformed metadata handling
  must remain unchanged.
- R5. Tests, the static baseline, README, SECURITY, VISION, and CHANGES must
  preserve the configuration-lifecycle contract.

## Verification

- `make check` passes with 34 offline tests and Python 3 compilation.
- The 34-test suite and compile gate pass on Python 3.10.20, 3.12.8, and
  3.14.6, matching the hosted matrix.
- `git diff --check` passes.
- Restoring the import-time `from_users` snapshot fails the rotation regression
  and the static baseline.

## Work Completed

- Removed the module-level `from_users` snapshot.
- Loaded the validated approved-sender set inside each `approved_sender`
  decision.
- Simplified test setup so environment changes exercise production behavior
  directly rather than mutating a module global.
- Added a rotation regression plus executable documentation guards.
