---
title: Configured Automation User ID Authority
type: security
date: 2026-06-14
status: completed
execution: code
---

# Configured Automation User ID Authority

## Summary

Make deployment configuration authoritative for the Gmail credential key used
by mail routes. Logged-in request input must not override `AUTOMATION_USER_ID`
and select credentials stored for another mailbox identity.

## Requirements

- R1. Read the automation user ID only from `AUTOMATION_USER_ID` in both mail
  handler modules.
- R2. Preserve the existing HTTP 400 response when deployment configuration is
  missing.
- R3. Preserve the configured identity return path and existing Gmail call
  behavior.
- R4. Add a mutation-sensitive static contract covering both duplicate helpers.
- R5. Run the full offline gate on maintained Python versions without making
  Gmail, OAuth, or App Engine runtime calls.

## Non-Goals

- Changing App Engine login/admin route policy.
- Migrating stored OAuth credentials or changing their datastore schema.
- Modernizing the Python 2 application runtime.

## Work Completed

- Removed request-query identity selection from both mail handler helpers.
- Kept the existing missing-configuration response and configured success path.
- Added a focused source contract and wired it into the full maintenance gate.
- Updated contributor, operator, security, vision, and change guidance.

## Verification

- Python 3.12.8 and Python 3.14.0: the focused identity contract passed for
  both mail handler modules.
- Six hostile source mutations were rejected: request override in each module,
  duplicated configuration lookup, removed missing-config failure, removed
  absent return, and reversed failure/success ordering.
- Python 3.12.8 and Python 3.14.0: all 53 offline tests passed and `make check`
  completed the source baseline plus bytecode build.
- The Python 3.12.8 full gate also passed through the absolute Makefile path
  from an external working directory.
- No Gmail, OAuth, or App Engine runtime calls were made.
- Exact intended-path, generated-artifact, whitespace, conflict-marker, and
  changed-line credential-pattern audits passed before commit.
