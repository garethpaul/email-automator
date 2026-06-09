.PHONY: lint test verify check

PYTHON ?= python3

lint:
	./scripts/check-baseline.sh

test:
	$(PYTHON) -m unittest discover -s tests -p "test*.py"

verify: lint test

check: verify
