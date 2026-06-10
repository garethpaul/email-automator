# CI Baseline

Status: Completed

## Context

The repository had a local `make check` verification path, but no hosted
workflow that ran it for pushes and pull requests.

## Changes

- Added a GitHub Actions workflow that checks out the repository, installs
  Python 3.10, 3.12, and 3.14, and runs the offline `make check` baseline.
- Pinned actions by commit, granted read-only repository access, enabled
  stale-run cancellation, and limited jobs to five minutes.
- Kept obsolete App Engine deployment requirements outside the source
  compatibility job; the rule tests rely on checked-in compatibility shims.
- Extended the maintenance checker and project docs so future verification
  changes must keep the hosted CI path documented.

## Verification

- `make check` on Python 3.10, 3.12, and 3.14
- Workflow YAML parsing and `git diff --check`
