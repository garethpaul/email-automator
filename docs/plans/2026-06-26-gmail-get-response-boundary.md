# Gmail Get Response Boundary Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task.

**Goal:** Drop malformed Gmail per-message get responses without aborting the mailbox scan.

**Architecture:** Add a dependency-free response-shape helper next to the existing strict raw-message decoder. Route `GetMimeMessage` through that helper so malformed containers become the decoder's existing `ValueError` rejection path.

**Tech Stack:** Python 2.7/3.10/3.12/3.14, unittest, Google App Engine legacy handlers, GNU Make.

---

status: completed

### Task 1: Prove malformed response failure

**Files:**
- Modify: `tests/test_raw_message.py`
- Modify: `tests/test_integration_contracts.py`

1. Add pure tests requiring malformed response containers to return `None` and mappings to expose `raw` unchanged.
2. Add an integration contract requiring `GetMimeMessage` to call the helper instead of dereferencing `message.get('raw')`.
3. Run the two focused test modules and verify failure on the missing helper and direct dereference.

### Task 2: Add response boundary

**Files:**
- Modify: `mail/raw_message.py`
- Modify: `mail/list.py`

1. Add `gmail_raw_value(response)` accepting mappings only.
2. Import the helper with the existing package/script fallback pattern.
3. Pass its result to `decode_raw_message` inside the existing `ValueError` boundary.
4. Rerun focused tests and verify green.

### Task 3: Preserve maintained contracts

**Files:**
- Modify: `scripts/check-baseline.sh`
- Modify: `README.md`
- Modify: `SECURITY.md`
- Modify: `VISION.md`
- Modify: `AGENTS.md`
- Modify: `CHANGES.md`

1. Require the plan, helper, integration use, tests, and fail-closed guidance.
2. Record red/green, runtime-matrix, mutation, hosted, and review evidence.

### Task 4: Validate and merge

**Files:**
- Verify only.

1. Run focused tests, `make check`, `make verify`, and external Make.
2. Reject helper and integration hostile mutations.
3. Push a focused PR and attempt Codex review.
4. Merge only the exact final head after hosted checks pass.

## Verification Completed

- The red phase produced two missing-helper errors and one direct-dereference
  integration failure.
- The green phase passed 13 focused tests with the dependency-free helper and
  existing strict decoder composed together.
- Local and external-directory `make check` passed with 97 tests and all 77
  authoritative Python files verified.
- The pinned Python 2.7.18 container passed 97 tests with one expected skip and
  verified all 77 files.
- Two isolated hostile mutations were rejected: helper mapping-guard removal
  and restoration of the direct `message.get('raw')` dereference.
- Hosted checks and exact-head review remain the final closeout work.
