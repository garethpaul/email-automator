# Email Outbound From Address Validation

status: completed

## Context

The reply-rule path already validated approved sender and automation recipient
configuration before matching inbound messages. The outbound
`AUTOMATION_FROM_EMAIL` value was still read directly before calling
`CreateMessage`, which made malformed environment values a generated-header
boundary risk.

## Objectives

- Validate outbound automation From configuration before Gmail messages are
  created.
- Keep the validation path importable and testable without App Engine or Gmail
  dependencies.
- Avoid marking a message as sent in the duplicate-send cache if the outbound
  From configuration is invalid.
- Extend docs and baseline checks so the guard remains visible.

## Work Completed

- Added `configured_from_email()` to normalize and validate
  `AUTOMATION_FROM_EMAIL`.
- Made `sendEmail()` reject invalid outbound From configuration before
  importing the Gmail send helper.
- Made `valid_email()` cache duplicate message IDs only after `sendEmail()`
  reports success.
- Added offline unit coverage for valid and invalid From configuration and the
  invalid-send decision path.
- Documented the guard in README, SECURITY, VISION, and CHANGES.

## Verification

- `sh -n scripts/check-baseline.sh`
- `scripts/check-baseline.sh`
- `python3 -m unittest discover -s tests -p "test*.py"`
- `make build`
- `make check`
- `git diff --check`
