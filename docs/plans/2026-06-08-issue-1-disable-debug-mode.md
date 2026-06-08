---
title: Issue 1 Disable Debug Mode
type: fix
status: active
date: 2026-06-08
origin: https://github.com/garethpaul/email-automator/issues/1
execution: code
---

# Issue 1 Disable Debug Mode

## Summary

Disable webapp2 debug mode by default and require an explicit local-development environment flag to enable it.

## Problem Frame

Issue #1 was filed from the public repository review because `main.py` constructs the deployed `webapp2.WSGIApplication` with `debug=True`. In deployed web apps, debug mode can expose stack traces, configuration details, and development-only behavior.

## Requirements

- R1. `main.py` must not pass `debug=True` unconditionally to `webapp2.WSGIApplication`.
- R2. Debug mode must default to false.
- R3. Debug mode may be enabled only by an explicit local-development environment variable.
- R4. The PR must reference `https://github.com/garethpaul/email-automator/issues/1`.

## Implementation Unit

### U1. Environment-Gated Debug Mode

- **Goal:** Add a small `debug_enabled` helper, use it for the WSGI app, document the local development flag, and test the default/explicit behavior with fake App Engine dependencies.
- **Files:** `main.py`, `main_tests.py`, `README.md`
- **Test Scenarios:** Default debug false, truthy env enables debug, falsey env remains false, and source no longer contains unconditional `debug=True`.
- **Verification:** `python3 main_tests.py`, `python3 -m py_compile main.py main_tests.py`, `git diff --check`, and `rg -n "debug=True|EMAIL_AUTOMATOR_DEBUG|debug_enabled" main.py main_tests.py README.md`.

## Risks

- Existing local workflows that relied on debug mode being always enabled must now opt in with `EMAIL_AUTOMATOR_DEBUG=1`.
