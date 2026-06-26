# Gmail List Response Boundary Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task.

**Goal:** Keep Gmail mailbox scans iterable and fail closed when the list response has a malformed shape or an HTTP transport failure.

**Architecture:** Add a dependency-free Python 2/3 helper for the documented `messages[]` response boundary. Integrate it into the legacy App Engine handler without changing message fetch, cache, rule, or reply behavior.

**Tech Stack:** Python 2.7-compatible application code, modern Python offline unittest, Google Gmail API response schema, shell static contracts.

status: completed

---

### Task 1: Add response-shape regressions

**Files:**
- Create: `tests/test_list_response.py`

**Steps:**
1. Write tests for absent, malformed, tuple, and over-limit message collections.
2. Run the focused test and verify it fails because the helper is missing.

### Task 2: Implement the response helper

**Files:**
- Create: `mail/list_response.py`
- Modify: `scripts/python-surface-scopes.txt`

**Steps:**
1. Implement a Python 2/3-compatible bounded list extractor.
2. Run the focused test and verify all cases pass.

### Task 3: Integrate stable handler results

**Files:**
- Modify: `mail/list.py`
- Modify: `tests/test_integration_contracts.py`

**Steps:**
1. Add a failing source integration contract for helper use and `HttpError` returning `[]`.
2. Import and use the helper in `ListMessagesWithLabels`.
3. Return `[]` explicitly after the existing HTTP diagnostic.

### Task 4: Preserve repository contracts

**Files:**
- Modify: `scripts/check-baseline.sh`
- Modify: `README.md`
- Modify: `SECURITY.md`
- Modify: `VISION.md`
- Modify: `AGENTS.md`
- Modify: `CHANGES.md`

**Steps:**
1. Add required-file, implementation, test, and documentation contracts.
2. Document the stable iterable and malformed response boundary.
3. Run focused hostile mutations and the full Make matrix.

### Task 5: Review and merge

**Steps:**
1. Commit and push the focused branch.
2. Open a pull request against `master`.
3. Run `codex review --base origin/master` and resolve accepted findings.
4. Require all hosted checks before merging.

## Verification Completed

- The helper test failed first because `mail/list_response.py` did not exist.
- The integration test then failed on the direct unvalidated response access and
  implicit `None` HTTP-error return.
- Focused helper and integration tests pass after implementation.
- `make check` covers the full offline suite, source-authority matrix, and
  repository contracts.
- Hostile removal of the response mapping guard, 30-message bound, and stable
  HTTP-error return were each rejected by focused tests.
- The pinned Python 2.7.18 container passed 94 tests and verified all 77 tracked
  Python source entries.
