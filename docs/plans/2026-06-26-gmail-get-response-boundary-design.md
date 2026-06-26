# Gmail Get Response Boundary Design

status: completed

## Problem

`GetMimeMessage` assumes Gmail `messages.get(...).execute()` returns a mapping
and calls `message.get('raw')` directly. A malformed `None`, sequence, or scalar
response raises `AttributeError` before the existing base64url and MIME guards,
which aborts the whole mailbox scan instead of dropping one message.

## Evidence

- `mail/list.py` validates list-response shape but directly dereferences the
  per-message get response.
- `mail/raw_message.py` already owns dependency-free validation of the raw Gmail
  MIME value and rejects absent or malformed values with `ValueError`.
- The maintained suite can execute pure helpers on Python 2 and current Python 3
  without App Engine or Gmail credentials.

## Options Considered

1. Catch `AttributeError` around `message.get`. This hides unrelated attribute
   failures and leaves response policy embedded in the handler.
2. Add an inline `isinstance(message, dict)` check. This is small but duplicates
   response-shape policy outside the dependency-free boundary.
3. Add a pure `gmail_raw_value(response)` helper beside `decode_raw_message` and
   feed its result into the existing decoder.

## Decision

Use option 3. The helper accepts only mappings and returns the `raw` field or
`None`. The existing decoder remains authoritative for raw-value type,
base64url, canonical padding, and size validation. `GetMimeMessage` continues to
convert `ValueError` into per-message rejection.

## Validation

- Add failing pure helper tests for malformed response shapes and raw passthrough.
- Add an integration contract proving `GetMimeMessage` uses the helper before
  MIME parsing.
- Run focused tests, the full Python 2/3 verification gate, hostile mutations,
  hosted checks, and exact-head review.

## Verification Completed

- The focused suite failed first because `gmail_raw_value` did not exist and
  `GetMimeMessage` still dereferenced `message.get('raw')` directly.
- Thirteen focused raw-message and integration tests passed after routing the
  response through the helper.
- Local and external-directory `make check` passed with 97 tests and all 77
  authoritative Python files verified.
- The pinned Python 2.7.18 container passed the same 97-test suite with one
  expected skip and verified all 77 files.
- Removing the mapping guard and restoring the direct response dereference were
  both rejected by focused hostile mutations.
- Push and pull-request Check runs `28244650357` and `28244652748` passed all
  Python and dependency jobs on implementation head
  `e8334ecb5f3623becdd1a50e39c20a25a6a6d232`; CodeQL run `28244650912` passed.
- `codex review --base origin/master` was attempted and skipped after HTTP 401
  responses from both Codex API transports.
