.PHONY: build lint test verify check

override ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))
PYTHON ?= python3
PYTHON2 ?= python2
PYTHON3 ?= python3

lint:
	"$(ROOT)/scripts/check-baseline.sh"

test:
	cd "$(ROOT)" && $(PYTHON) -m unittest discover -s tests -p "test*.py"

build:
	$(PYTHON) "$(ROOT)/scripts/verify-python-surface.py" "$(ROOT)" "$(ROOT)/scripts/python-surface-scopes.txt" "$(PYTHON2)" "$(PYTHON3)"

verify: lint test build

check: verify
