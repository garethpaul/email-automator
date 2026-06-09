# Email Rule Body Length Limit

status: completed

## Context

Offline reply rules tokenize inbound message bodies before choosing automated
response text. The rule path should avoid scanning arbitrarily large payloads by
default, even when Gmail or test fixtures provide unusually large message
content.

## Objectives

- Preserve existing keyword matching inside a bounded body prefix.
- Ignore content beyond the configured body limit during local rule matching.
- Add offline unit coverage for the body length boundary.
- Extend docs and the static baseline so the limit remains visible.

## Work Completed

- Added `MAX_EMAIL_BODY_LENGTH` and `bounded_email_body()` before tokenization.
- Added offline unit coverage for ignoring keywords after the body limit.
- Extended the static baseline to require the limit, regression test, docs, and
  completed plan.
- Documented the inbound body matching limit in README, SECURITY, VISION, and
  CHANGES.

## Verification

- `sh -n scripts/check-baseline.sh`
- `scripts/check-baseline.sh`
- `python3 -m unittest discover -s tests -p "test*.py"`
- `make build`
- `make check`
- `git diff --check`
