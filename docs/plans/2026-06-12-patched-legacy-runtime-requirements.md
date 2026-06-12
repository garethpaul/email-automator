# Patched Legacy Runtime Requirements

status: completed

## Context

GitHub reports four open alerts against `requirements.txt`: two WebOb redirect
normalization advisories and two virtualenv filesystem/activation advisories.
The live application is a Python 2 Google App Engine prototype, while hosted
verification intentionally exercises only dependency-free offline rule logic on
modern Python.

WebOb 1.8.10 is the first release above both recorded advisory floors and still
declares Python 2.7 support. The first virtualenv release above all recorded
floors requires Python 3.8 or newer, and virtualenv is not imported, invoked by
the Makefile, or needed by the deployed application. It is an obsolete local
tool accidentally recorded as a runtime dependency.

## Priority

Remove the known dependency exposure without broadening this focused pass into
an App Engine, webapp2, OAuth, Gmail API, or Python runtime migration.

## Requirements

- R1. Pin WebOb to 1.8.10 so both recorded redirect advisories are outside the
  installed range while preserving the declared Python 2.7 compatibility
  boundary.
- R2. Remove virtualenv from the runtime manifest because it is unused by the
  application and patched releases no longer support the legacy runtime.
- R3. Preserve exact pins for webapp2 2.5.2, uritemplate 0.6, and WebTest
  2.0.21; any migration of those packages belongs to the dedicated App Engine
  modernization effort.
- R4. Extend the dependency-free baseline checker to require the exact
  four-package manifest, reject virtualenv and floating requirements, and
  enforce completed plan evidence.
- R5. Add one bounded Python 3.12 hosted dependency-audit job that installs an
  exact `pip-audit` tool version and audits the fully pinned manifest with pip
  resolution disabled. This avoids falsely claiming that the Python 2 runtime
  is installable or executable on the hosted Python 3 runner.
- R6. Keep the existing Python 3.10/3.12/3.14 offline rule matrix unchanged and
  free of App Engine, Gmail, OAuth, and mailbox credentials.
- R7. Update README, security, vision, changes, contributor guidance, and this
  plan with the legacy dependency boundary and actual verification evidence.

## Scope Boundaries

- Do not migrate Python 2, App Engine, webapp2, vendored OAuth, or Gmail API
  clients in this pass.
- Do not install or import the legacy application stack in the modern hosted
  rule-test matrix.
- Do not add credentials, contact Gmail, or exercise real mailbox data.
- Do not merge or close the repository's open pull requests.

## Verification

- `make lint`
- `make test`
- `make build`
- `make check`
- dependency audit reports zero known vulnerabilities for the explicit pins
- hostile WebOb downgrade, virtualenv restoration, floating pin, audit removal,
  and incomplete plan mutations are rejected
- `git diff --check`
- successful exact-head push, pull-request, dependency-audit, and CodeQL runs

## Work Completed

- Raised WebOb from 1.6.1 to the Python 2.7-compatible 1.8.10 security floor.
- Removed virtualenv 15.0.2 because environment creation is not a deployed
  application dependency and patched virtualenv releases require modern
  Python.
- Preserved exact webapp2, uritemplate, and WebTest pins and kept the modern
  offline rule-test matrix free of the legacy App Engine dependency graph.
- Added a separate Python 3.12 `pip-audit` job with dependency resolution
  disabled, fixed both checkouts to avoid persisted credentials, and selected
  the fixed Ubuntu 24.04 runner.
- Updated repository contracts and maintenance, security, vision, contributor,
  and setup guidance for the explicit legacy runtime boundary.

## Verification Results

- `make lint`, `make test`, `make build`, and `make check` passed locally with
  all 34 offline tests.
- `pip-audit --disable-pip --no-deps -r requirements.txt` reported no known
  vulnerabilities without installing or resolving the Python 2 stack.
- Workflow YAML parsed with the three-version rule matrix and separate
  dependency-audit job.
- Canonical push run `27430550372` and pull-request run `27430552862` passed
  Python 3.10, 3.12, and 3.14 checks plus dependency audit at implementation
  head `330cab60f6c2cf4dca878519563ec8517d37e1d2`.
- CodeQL run `27430550455` passed Actions and Python analysis at the same head.
