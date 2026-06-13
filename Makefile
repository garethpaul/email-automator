.PHONY: build lint test verify check

PYTHON ?= python3

lint:
	./scripts/check-baseline.sh

test:
	$(PYTHON) -m unittest discover -s tests -p "test*.py"

build:
	$(PYTHON) -m py_compile mail/rules.py mail/text_payload.py tests/test_rules.py tests/test_text_payload.py

verify: lint test build

check: verify
