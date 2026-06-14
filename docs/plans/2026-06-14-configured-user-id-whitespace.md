---
title: Configured Automation User ID Whitespace Boundary
type: reliability
date: 2026-06-14
status: completed
execution: code
---

# Configured Automation User ID Whitespace Boundary

## Summary

Treat whitespace-only `AUTOMATION_USER_ID` values as missing configuration in
both mail handlers instead of attempting credential lookup with a blank key.

## Requirements

- R1. Continue reading mailbox identity only from deployment configuration.
- R2. Strip surrounding whitespace before the existing missing-value check.
- R3. Return the same HTTP 400 and JSON error for absent or whitespace-only IDs.
- R4. Preserve nonblank configured IDs and existing Gmail API call behavior.
- R5. Extend the mutation-sensitive duplicate-helper contract.
- R6. Run the maintained offline matrix without live Gmail, OAuth, or App Engine
  calls.

## Non-Goals

- Changing request authentication, credential storage, Gmail API user IDs, or
  OAuth scopes.
- Imposing an email-address schema on an otherwise opaque credential key.
- Modernizing the Python 2 deployment runtime.

## Verification Plan

- Focused configured-user-id static contract on Python 3.12 and Python 3.14
- Full `make check` on Python 3.12 and Python 3.14
- External-working-directory `make check`
- `git diff --check`
- Hostile mutations for each helper, normalization ordering, missing handling,
  documentation, completion status, and verification evidence

## Work Completed

- Normalized the deployment-owned `AUTOMATION_USER_ID` with an empty fallback
  and surrounding-whitespace removal in both mail handlers.
- Preserved the existing HTTP 400 JSON response for missing configuration and
  every nonblank configured credential key.
- Strengthened the duplicate-helper source contract and maintenance guidance.

## Verification Completed

- Python 3.12.8 and Python 3.14.0: the focused configured-user-id contract
  passed for both mail handler modules.
- Python 3.12.8 and Python 3.14.0: all 53 offline tests passed and `make check`
  completed the source baseline plus bytecode build.
- External-working-directory `make check` passed on Python 3.12.8.
- Eight hostile mutations were rejected: missing normalization in each helper,
  missing empty fallback, weakened missing-value handling, request identity
  override, missing documentation, stale plan status, and missing verification
  evidence.
- No Gmail, OAuth, or App Engine runtime calls were made.
