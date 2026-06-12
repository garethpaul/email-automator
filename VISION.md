## Email Automator Vision

This document explains the current state and direction of the project.
Project overview and developer docs: [`README.md`](README.md)

Email Automator is a Google App Engine and Gmail API prototype for scanning an
inbox, processing incoming email text, and sending automated replies.

The repository is useful as a historical email automation experiment with task
queues, cron, Gmail authorization, local rule data, and vendored App Engine-era
libraries. Setup notes live in [`README.md`](README.md).

The goal is to preserve the prototype while making authorization, privacy, and
deployment boundaries explicit.

The current focus is:

Priority:

- Keep Gmail authorization and automated reply flow understandable
- Avoid committing OAuth credentials, app secrets, or private mailbox data
- Preserve cron/task-queue intent for retrieval and processing
- Keep App Engine setup requirements visible
- Keep GitHub Actions aligned with the local `make check` baseline

Current baseline:

- `mail.rules` can be imported and tested offline without App Engine or Gmail
  modules.
- Duplicate message IDs are cached in the offline rule baseline so approved
  messages are sent only once.
- Unknown automated replies avoid emergency-service language.
- `scripts/check-baseline.sh` runs deterministic rule tests that do not access
  Gmail, OAuth, or real inbox data.
- App Engine debug mode defaults off, auth/mail routes require HTTPS/login, and
  `/mail/me` is reserved for admin/cron access.
- OAuth and automation mailbox placeholders are environment-backed instead of
  committed query parameters.
- Automation recipient checks compare normalized recipient addresses only, not
  display names.
- Configured sender and recipient email addresses are validated before rule
  checks use them.
- Inbound malformed sender metadata is rejected before message reservation or
  delivery.
- Outbound automation From addresses are validated before generated Gmail
  messages are created.
- The core `valid_email` send decision also requires the message to be
  addressed to the automation mailbox.
- Automated reply subjects collapse line breaks and cap length before sending.
- Rule matching is limited to the first 10000 characters of an inbound body.
- Message IDs are normalized and length-bounded before duplicate-send cache keys
  are built.
- Valid message IDs are atomically reserved before outbound sends, preventing
  concurrent workers from sending the same automated reply; failed sends
  release their reservation for retry.
- GitHub Actions runs the offline `make check` baseline on Python 3.10, 3.12,
  and 3.14 for pushes, pull requests, and manual dispatches.

Next priorities:

- Document credential files, scopes, and safe local setup
- Modernize App Engine and Google API dependencies in a dedicated pass
- Add tests around email stripping, rule matching, and reply generation
- Make opt-in and failure behavior clear before any real mailbox use

Contribution rules:

- One PR = one focused auth, mail processing, deployment, or documentation topic.
- Run `scripts/check-baseline.sh` before pushing reply-rule, auth, or App
  Engine routing changes.
- Keep `.github/workflows/check.yml` in sync with the local `make check`
  contract.
- Do not mix platform migration with reply behavior changes unless required.
- Keep vendored dependency changes reviewable.
- Verify behavior against test fixtures rather than real inbox data where possible.
- Keep recipient and sender matching in offline-testable helpers before wiring
  them into App Engine handlers.

## Security And Privacy

Canonical security policy and reporting:

- [`SECURITY.md`](SECURITY.md)

Email contents, sender identities, OAuth tokens, and generated replies are
sensitive. Do not commit credentials, mailbox exports, or real message samples.

Automation should remain explicit and opt-in; future changes should avoid
surprising auto-replies or broad mailbox access.

## What We Will Not Merge (For Now)

- Real OAuth credentials, mailbox data, or private reply corpora
- Silent auto-reply behavior without opt-in controls
- Broad Google platform migrations bundled with behavior changes
- Tests that require access to a real Gmail inbox by default

This list is a roadmap guardrail, not a permanent rule.
Strong user demand and strong technical rationale can change it.
