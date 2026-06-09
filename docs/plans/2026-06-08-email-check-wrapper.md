---
title: Email Automator Check Wrapper
date: 2026-06-08
status: completed
execution: code
---

## Context

The App Engine email automation prototype has offline rule tests and a safety
baseline, but it lacks the repository-standard `make check` command.

## Goals

- Add a root Makefile with `lint`, `test`, `verify`, and `check` targets.
- Make `make check` run the App Engine safety baseline and offline rule tests.
- Keep the default gate free of Gmail, OAuth, App Engine runtime, and real
  mailbox data.
- Document and preserve the wrapper through README, CHANGES, and the baseline.

## Verification

- `make check`
- `scripts/check-baseline.sh`
- `git diff --check`
