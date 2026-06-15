# email-automator

Raw Gmail MIME values are strictly base64url-validated and capped at 25 MiB before MIME parsing.
Raw Gmail MIME values reject noncanonical pad bits before MIME parsing.

<!-- README-OVERVIEW-IMAGE -->
![Project overview](docs/readme-overview.svg)

## Overview

`garethpaul/email-automator` is a legacy Python 2 Google App Engine prototype
for scanning Gmail messages and generating automated replies from local rules.
The live app paths require App Engine services and OAuth credentials; the
default repository verification path only exercises offline rule behavior.

## Repository Contents

- `README.md` - project overview and local usage notes
- `requirements.txt` - exact patched legacy Python 2 runtime pins
- `app.yaml` and `cron.yaml` - App Engine routing and scheduled check config
- `database/` - App Engine credential model helpers
- `Makefile` - repository-level verification wrapper
- `mail/` - Gmail auth, listing, send, and reply-rule modules
- `main.py` - App Engine webapp route registration
- `SECURITY.md` - security reporting and disclosure guidance
- `VISION.md` - project direction and maintenance guardrails

## Getting Started

### Prerequisites

- Git
- Google App Engine Python 2 SDK for the deployed prototype
- Python 3.10, 3.12, or 3.14 for the offline rule tests

### Setup

```bash
git clone https://github.com/garethpaul/email-automator.git
cd email-automator
make check
```

Live Gmail/App Engine paths require local OAuth client configuration and App
Engine credentials that must not be committed. The default local test path below
does not access Gmail, OAuth, App Engine, or real mailbox data.

`requirements.txt` belongs only to the legacy Python 2/App Engine runtime. Do
not install it into the modern offline-test environment. It pins patched WebOb
1.8.10 and excludes virtualenv because environment creation is tooling, not an
application dependency, and patched virtualenv releases require modern Python.

The setup commands above are derived from repository files. Legacy mobile, Python, or JavaScript samples may require older SDKs or package versions than a modern workstation uses by default.

## Running or Using the Project

- `main.py` defines the App Engine webapp routes for `/auth`, `/mail/check`,
  `/mail/list`, and `/mail/me`.
- `app.yaml` requires HTTPS for app routes, requires login for auth/mail
  handlers, and restricts `/mail/me` to admin/cron access.
- `cron.yaml` schedules `/mail/me`; the automation user id comes from
  `AUTOMATION_USER_ID` instead of a committed or request-supplied query
  parameter. Mail handlers do not let request input select another stored Gmail
  credential key.
- `mail/rules.py` contains the offline-testable automated reply rule logic,
  including recipient-address checks for the automation mailbox and single-line
  reply subject normalization.
- Automated reply rule matching scans only the first 10000 characters of an
  inbound body before generating response text.
- Malformed non-string body and subject values normalize to empty text before
  rule matching or reply-subject generation.
- Missing, unknown, and malformed MIME text charsets use replacement decoding
  so one message cannot abort inbox processing.
- Message IDs are normalized and length-bounded before duplicate-send cache keys
  are built.
- Valid messages reserve their normalized ID with atomic memcache `add` before
  the Gmail send; concurrent workers stop before the side effect, while failed
  sends release the reservation for retry.
- Gmail list summaries are fetched and cached by validated message `id`, not
  `threadId`, so later messages in an existing thread cannot reuse stale MIME
  content.

## Testing and Verification

Run the offline rule tests:

```bash
make check
python3 -m unittest discover -s tests -p "test*.py"
```

Run the full local baseline gate:

```bash
make check
scripts/check-baseline.sh
```

`make check` runs the baseline gate and offline unittest discovery. These tests
use deterministic fixtures, assert atomic duplicate-message reservation and
failed-send release behavior, verify
automation recipient matching by address in the handler and core send decision,
verify reply subject normalization, compile the rule module and tests through
`make build`, cover bounded inbound body matching, and do not access Gmail or a
real inbox.

The Makefile resolves verification paths from its own location, so the same
gate can be invoked from another directory with `make -f /path/to/Makefile check`.

GitHub Actions runs the same offline `make check` baseline on Python 3.10,
3.12, and 3.14 for pushes, pull requests, and manual dispatches. The workflow
pins its actions by commit, grants read-only repository access, and does not
install the obsolete App Engine deployment requirements. A separate Python
3.12 job audits the exact legacy pins with dependency resolution disabled, so
the audit does not claim the Python 2 application stack runs on the hosted
Python 3 worker.

When the required SDK or runtime is unavailable, use static checks and source review first, then verify on a machine that has the matching platform toolchain.

## Configuration and Secrets

- The scan found credential-adjacent names. Review configuration paths before running against real accounts.
- Keep OAuth client IDs, OAuth client secrets, App Engine credentials, Gmail
  tokens, and real mailbox samples out of git.
- `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `AUTOMATION_USER_ID`,
  `AUTOMATION_TO_EMAIL`, `AUTOMATION_FROM_EMAIL`, and
  `AUTOMATION_APPROVED_SENDERS` are deployment/local configuration values.
- `AUTOMATION_USER_ID` is authoritative for mail handlers; request parameters
  cannot override the stored Gmail credential key.
- Whitespace-only AUTOMATION_USER_ID values are rejected as missing configuration.
- Configured sender and recipient email addresses are validated before reply
  rules use them; malformed values are ignored instead of triggering replies.
- `AUTOMATION_APPROVED_SENDERS` is read at authorization time so allow-list
  rotations apply without waiting for an App Engine process restart.
- The current `AUTOMATION_FROM_EMAIL` is rejected as an inbound sender even if
  accidentally approved, preventing self-generated reply loops before message
  reservation or delivery.
- The authorization path ignores malformed sender metadata and fails closed
  before reserving a message ID or sending a reply.
- The recipient matcher ignores malformed recipient metadata and rejects invalid
  message or recipient containers before reservation or delivery.
- Authorization requires exactly one structurally valid sender identity;
  duplicate or mixed valid `From` entries fail closed before side effects.
- Outbound `AUTOMATION_FROM_EMAIL` is validated before `CreateMessage` is
  called, and invalid From configuration prevents automated sends.
- Automated reply rule matching scans only a bounded inbound body prefix before
  generating response text.
- Non-string bodies produce no rule tokens, and non-string subjects use the
  safe `Re:` fallback instead of raising during automation.
- Message IDs are normalized and length-bounded before memcache duplicate-send
  keys are used.
- Duplicate-message IDs are reserved atomically before outbound sends. A failed
  or raised send releases its reservation so a later retry can proceed.
- Gmail message IDs, rather than thread IDs, identify MIME fetches and parsed
  message cache entries; malformed summaries are skipped before either action.
- `APP_DEBUG` defaults off; set `APP_DEBUG=1` only for local debugging.

## Security and Privacy Notes

- Review changes touching authentication or token handling; examples from the scan include mail/auth.py, mail/check.py, mail/list.py, mail/send.py, and 2 more.
- Review changes touching external API calls or credential-adjacent configuration; examples from the scan include mail/auth.py.
- Review changes touching network requests, sockets, or service endpoints; examples from the scan include app.yaml, mail/auth.py, test.py.
- Review changes touching file, media, JSON, XML, CSV, OCR, or data parsing; examples from the scan include mail/check.py, mail/list.py, mail/rules.py, mail/send.py.
- Review changes touching database, model, or persistence code; examples from the scan include database/default.py.
- App Engine routes require HTTPS, `/mail/me` is admin-only for cron, and debug
  output is disabled unless `APP_DEBUG=1` is set for local development.

## Maintenance Notes

- See `SECURITY.md` for vulnerability reporting and safe research guidance.
- See `VISION.md` for project direction and contribution guardrails.
- See `docs/plans/2026-06-08-email-rule-baseline.md` for the current offline
  reply-rule baseline.
- See `docs/plans/2026-06-08-app-engine-safety-baseline.md` for the App Engine
  route and configuration safety baseline.
- See `docs/plans/2026-06-09-email-recipient-address-guard.md` for the
  automation recipient-address guard.
- See `docs/plans/2026-06-09-email-valid-email-recipient-guard.md` for the
  core send-decision recipient guard.
- See `docs/plans/2026-06-09-email-reply-subject-normalization.md` for the
  automated reply subject guard.
- See `docs/plans/2026-06-09-email-config-address-validation.md` for configured
  automation email address validation.
- See `docs/plans/2026-06-09-email-outbound-from-address-validation.md` for
  outbound From address validation.
- See `docs/plans/2026-06-09-email-rule-body-length-limit.md` for the inbound
  body length limit used by reply-rule matching.
- See `docs/plans/2026-06-09-email-message-id-cache-guard.md` for message ID
  cache-key validation before duplicate-send checks.
- See `docs/plans/2026-06-10-ci-baseline.md` for the hosted GitHub Actions
  baseline.
- See `docs/plans/2026-06-10-atomic-message-deduplication.md` for pre-send
  message reservation and failed-send release behavior.
- See `docs/plans/2026-06-12-gmail-message-id-fetch-cache.md` for the Gmail
  message-versus-thread identity boundary.
- See `docs/plans/2026-06-12-approved-sender-config-refresh.md` for the
  authorization-time approved-sender configuration lifecycle.
- See `docs/plans/2026-06-12-patched-legacy-runtime-requirements.md` for the
  patched WebOb, removed virtualenv, and hosted dependency-audit boundary.
- See `docs/plans/2026-06-13-email-self-reply-guard.md` for authorization-time
  self-sender rejection.
- See `docs/plans/2026-06-13-email-text-boundary.md` for fail-closed body and
  subject text normalization.
- See `docs/plans/2026-06-13-email-sender-cardinality.md` for unambiguous
  inbound sender authorization.
- See `docs/plans/2026-06-14-email-recipient-metadata-boundary.md` for fail-closed
  inbound recipient metadata handling.
- Use [`RUNTIME_VERIFICATION.md`](RUNTIME_VERIFICATION.md) for exact-head App
  Engine, OAuth, Gmail, memcache, cron, inbound-handler, and outbound-delivery
  evidence. It requires synthetic mailboxes and messages plus sanitized results.

## Contributing

Keep changes small and tied to the project that is already present in this
repository. For code changes, run `scripts/check-baseline.sh`, avoid committing
credentials or mailbox data, keep vendored dependency updates isolated, and
update this README when setup or verification steps change.
