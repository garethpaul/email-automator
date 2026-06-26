# Gmail List Response Boundary Design

status: completed

## Evidence

Google's `users.messages.list` response defines `messages[]` as a list of
message resources. The legacy handler currently evaluates membership on the
raw response and slices `response["messages"]` without validating either
container. A `None`, scalar, or malformed `messages` value therefore raises
before the existing message-ID validation can fail closed. The `HttpError`
branch also falls through with `None`, while both request handlers iterate the
result as a list.

Official reference:
https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.messages/list

## Options Considered

1. Add inline `dict` and list checks in `mail/list.py`. This is small but cannot
   be exercised by the maintained dependency-free suite because that module
   imports the legacy App Engine and Gmail stack at import time.
2. Catch every exception around mailbox listing. This would hide programming,
   cache, and authentication failures and make diagnosis worse.
3. Extract a Python 2/3-compatible response-shape helper and keep transport
   handling explicit. This provides executable offline coverage and preserves
   the existing per-message validation and cache behavior.

## Decision

Add a dependency-free helper that accepts only a dictionary response and a
list or tuple `messages` field, returning at most the existing 30 summaries.
Malformed response shapes return an empty list. `ListMessagesWithLabels` uses
that helper and explicitly returns an empty list after its existing
`HttpError` diagnostic, preserving a stable iterable result for both handlers.

## Validation

Add Python 2/3-compatible tests for absent, malformed, tuple, and oversized
message collections, plus an integration source contract for the `HttpError`
return. Run the full source-authority and offline matrix, then require hosted
Python 2/3 and CodeQL gates before merge. The completed implementation passes
`make check` before publication.
