# Make Offline Verification Location Independent

status: in progress

## Context

The Makefile invokes the checker and Python paths relative to the caller, so an
absolute `make -f` invocation outside the repository fails before the offline
test suite runs.

## Requirements

- Resolve the repository root from the loaded Makefile.
- Root checker, unittest discovery, and bytecode compilation paths.
- Preserve the selected Python interpreter and all 50 offline tests.
- Add mutation-sensitive contracts and actual `/tmp` verification.
- Do not alter Gmail, OAuth, App Engine, dependencies, workflows, or mail rules.

## Verification

- Run `make check` on Python 3.12 and 3.14 from the repository.
- Run the absolute Makefile from `/tmp`.
- Run hostile path mutations, shell syntax, whitespace, exact-path, secret, and
  artifact checks.

## Risks

- Live legacy services remain unverified; this change only fixes local path
  resolution for the maintained offline boundary.
