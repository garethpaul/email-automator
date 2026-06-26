# Credential And Opt-In Setup Implementation Plan

Status: Completed

> **For Claude:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task.

**Goal:** Document safe credential handling, Gmail scopes, and explicit opt-in setup without changing the legacy runtime.

**Architecture:** Add one canonical setup guide and an ignored local App Engine manifest convention. Protect the guide with the existing static baseline while leaving OAuth, Gmail, App Engine, and reply behavior unchanged.

**Tech Stack:** Markdown, POSIX shell contracts, Git ignore rules, legacy App Engine Python 2 configuration.

---

### Task 1: Add the failing setup contract

**Files:**
- Modify: `scripts/check-baseline.sh`

1. Require `CREDENTIAL_SETUP.md` and the ignored `app.local.yaml` convention.
2. Require the exact Gmail scopes, all configuration variables, explicit opt-in
   order, and truthful no-runtime evidence.
3. Run `scripts/check-baseline.sh` and observe failure before the guide exists.

### Task 2: Add the canonical setup guide

**Files:**
- Create: `CREDENTIAL_SETUP.md`
- Modify: `.gitignore`
- Modify: `README.md`
- Modify: `SECURITY.md`
- Modify: `VISION.md`
- Modify: `CHANGES.md`

1. Document credential categories and exact Gmail scopes.
2. Document the ignored local manifest preflight and explicit authorization order.
3. State that no live OAuth, Gmail, App Engine, cron, or delivery flow was run.
4. Close the roadmap item without claiming platform migration or live support.

### Task 3: Verify and publish

**Files:**
- Modify: `docs/plans/2026-06-25-credential-opt-in-setup.md`

1. Run isolated hostile documentation mutations.
2. Run repository and external-directory `make check`.
3. Commit, push a focused PR, run Codex review, wait for hosted checks, and merge
   only the exact green head.

## Completion Evidence

- Thirteen isolated hostile mutations were rejected for the guide, ignore rule,
  exact scopes, configuration variables, opt-in boundary, and truthful runtime
  evidence.
- Repository and external-directory `make check` passed.
- No OAuth, Gmail, App Engine, memcache, cron, or delivery flow was executed.
