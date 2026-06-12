# Patched Legacy Runtime Requirements

status: planned

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
