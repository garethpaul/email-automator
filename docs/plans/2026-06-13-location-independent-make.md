# Make Offline Verification Location Independent

status: completed

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

- `make check PYTHON=python3` passed all 50 tests and the compile gate.
- `make check PYTHON=python3.14` passed all 50 tests and the compile gate.
- `make -f /absolute/path/to/Makefile check PYTHON=python3` passed from /tmp.
- Six hostile path and documentation mutations were rejected by the baseline
  checker; shell syntax, whitespace, exact-path, secret, and artifact checks
  also passed.

## Risks

- Live legacy services remain unverified; this change only fixes local path
  resolution for the maintained offline boundary.
