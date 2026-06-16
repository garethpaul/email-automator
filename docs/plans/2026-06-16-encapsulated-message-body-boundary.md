# Encapsulated Message Body Boundary

## Status: Planned

## Context

The inline MIME selector rejects explicit attachments and named parts, but it
still traverses an undecorated `message/rfc822` container because Python's email
parser reports it as multipart. Nested HTML from an encapsulated message can
therefore outrank the legitimate outer plain-text body and become automated
reply input.

## Objectives

- Treat every encapsulated `message/rfc822` part as a nested message boundary,
  regardless of disposition or filename.
- Preserve selection of ordinary inline `text/plain` and `text/html` body parts.
- Preserve existing attachment, named-part, raw-message, canonical base64url,
  text decoding, sender, recipient, and configured-identity boundaries.
- Keep the change compatible with the repository's Python 2 and Python 3 test
  matrix.

## Scope

- Update `mail/body_parts.py` before generic multipart traversal.
- Add a real MIME regression to `tests/test_body_parts.py`.
- Extend `scripts/check-baseline.sh` and maintained repository guidance.
- Do not change Gmail API requests, message schemas, reply rules, dependencies,
  App Engine configuration, or outbound delivery.

## Verification

- Reproduce nested HTML selection with an undecorated encapsulated message
  before the fix.
- Run the focused body-part tests under available Python interpreters.
- Run repository-root and external-directory `make check`.
- Reject hostile mutations that remove or reorder the encapsulated-message
  guard, weaken the fixture or expected result, remove guidance, or revert plan
  completion.
- Run whitespace, artifact, sensitive-value, dependency, and exact-path audits.

No App Engine, OAuth, Gmail, cron, memcache, browser, live mailbox, or outbound
delivery integration is available in this environment.
