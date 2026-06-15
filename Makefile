.PHONY: build lint test verify check

ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))
PYTHON ?= python3

lint:
	"$(ROOT)/scripts/check-baseline.sh"

test:
	cd "$(ROOT)" && $(PYTHON) -m unittest discover -s tests -p "test*.py"

build:
	$(PYTHON) -m py_compile "$(ROOT)/mail/raw_message.py" "$(ROOT)/mail/rules.py" "$(ROOT)/mail/text_payload.py" "$(ROOT)/tests/test_raw_message.py" "$(ROOT)/tests/test_rules.py" "$(ROOT)/tests/test_text_payload.py"

verify: lint test build

check: verify
