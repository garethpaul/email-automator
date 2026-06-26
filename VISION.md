## Email Automator Vision

Whitespace-only AUTOMATION_USER_ID values are rejected as missing configuration.
Raw Gmail MIME values are strictly base64url-validated and capped at 25 MiB before MIME parsing.
Raw Gmail MIME values reject noncanonical pad bits before MIME parsing.

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
- Keep credential categories, exact Gmail scopes, ignored local configuration,
  and authorization-before-cron opt-in documented

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
- Keep exact-head App Engine, OAuth, Gmail, memcache, cron, and delivery
  evidence sanitized and separate from portable Python verification.
- OAuth and automation mailbox placeholders are environment-backed instead of
  committed query parameters.
- Mailbox credential identity is deployment-owned through `AUTOMATION_USER_ID`
  and cannot be selected by request parameters.
- Automation recipient checks compare normalized recipient addresses only, not
  display names.
- Configured sender and recipient email addresses are validated before rule
  checks use them.
- Approved senders are loaded from validated environment configuration at
  authorization time rather than cached when the module imports.
- The current outbound automation address is rejected as an inbound sender at
  authorization time, preventing self-generated reply loops before side
  effects.
- Inbound malformed sender metadata is rejected before message reservation or
  delivery.
- Inbound malformed recipient metadata fails closed before message reservation
  or delivery while valid later recipients remain matchable.
- Inbound authorization requires one structurally valid sender identity;
  ambiguous multi-sender metadata is rejected before side effects.
- MIME text decoding fails closed without allowing malformed charset metadata to
  abort sender and rule processing.
- Automated reply content uses only inline MIME text parts; attachments and
  named file parts are excluded.
- Encapsulated message descendants are excluded from automated reply content.
- Multipart/related resources are excluded from automated reply content; only the MIME-defined root is traversed.
- MIME traversal and decoded-text extraction remain explicitly bounded, and
  ambiguous or recursively hostile messages fail closed without affecting the
  rest of the mailbox scan.
- Reply construction owns Gmail base64url serialization and header-injection
  rejection at one dependency-free boundary.
- Outbound automation From addresses are validated before generated Gmail
  messages are created.
- The core `valid_email` send decision also requires the message to be
  addressed to the automation mailbox.
- Automated reply subjects collapse line breaks and cap length before sending.
- Rule matching is limited to the first 10000 characters of an inbound body.
- Malformed non-string body and subject values normalize to empty text before
  rule matching or reply-subject generation.
- Message IDs are normalized and length-bounded before duplicate-send cache keys
  are built.
- Valid message IDs are atomically reserved before outbound sends, preventing
  concurrent workers from sending the same automated reply; failed sends
  release their reservation for retry.
- Gmail message IDs identify MIME fetches and cache entries; thread IDs are not
  reused as message identity, and malformed summaries are skipped.
- GitHub Actions runs the offline `make check` baseline on Python 3.10, 3.12,
  and 3.14 for pushes, pull requests, and manual dispatches.
- Makefile verification resolves repository paths independently of the caller's
  working directory.
- The exact legacy runtime manifest keeps patched WebOb and excludes unused
  virtualenv tooling.
- A separate hosted dependency audit checks the explicit pins without
  installing or claiming Python 3 compatibility for the Python 2 stack.

Next priorities:

- Keep credential files, scopes, and safe local opt-in setup aligned with the
  checked-in auth and deployment configuration
- Migrate App Engine, Python 2, webapp2, OAuth, and Google API dependencies in
  one dedicated compatibility pass
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
