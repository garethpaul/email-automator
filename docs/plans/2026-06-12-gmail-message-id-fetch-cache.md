# Gmail Message-ID Fetch And Cache

status: completed

## Context

Gmail list responses contain both a message `id` and a `threadId`. The current
listing flow passes `threadId` to `messages().get`, whose `id` parameter expects
a message ID, and caches parsed MIME content under that thread ID.

Using thread identity for message retrieval can fail the API call. Reusing the
thread cache entry can also hide later messages added to an existing thread,
preventing eligible new mail from reaching the automation rules.

## Priority

Correct message identity is required before sender, recipient, deduplication,
and reply controls can run. A stale or invalid fetch key can cause silent mail
processing gaps and unpredictable retries.

## Prioritized Engineering Backlog

1. Fetch and cache Gmail MIME content by validated message ID now.
2. Return stable empty collections when Gmail list/fetch calls fail so handler
   iteration cannot crash.
3. Add bounded cache expiration if the deployed prototype remains active.

## Requirements

- R1. Gmail message summaries must derive identity only from the `id` field,
  never from `threadId`.
- R2. Missing, malformed, or oversized message IDs must be skipped before
  cache access or Gmail MIME fetches.
- R3. MIME cache keys must be message-specific so a later message in the same
  thread cannot reuse stale parsed content.
- R4. Existing send deduplication keys and public rule behavior must remain
  unchanged.
- R5. Offline tests and static repository contracts must detect thread-ID fetch
  or cache regressions.
- R6. Maintenance docs must explain the message/thread identity boundary.

## Implementation Units

### U1. Add an offline-tested summary identity helper

- **Files:** `mail/rules.py`, `tests/test_rules.py`
- Validate dictionary summaries and normalize only the Gmail `id` field using
  the existing message-ID constraints.

### U2. Correct Gmail list retrieval and caching

- **Files:** `mail/list.py`
- Skip malformed summaries and use the validated message ID for cache lookup,
  `GetMimeMessage`, and cache insertion.

### U3. Extend contracts and documentation

- **Files:** `scripts/check-baseline.sh`, `README.md`, `SECURITY.md`,
  `VISION.md`, `CHANGES.md`
- Preserve message-ID keyed retrieval and record verification.

## Scope Boundaries

- Do not migrate the legacy App Engine Python 2 runtime.
- Do not change Gmail OAuth scopes, reply generation, or send deduplication.
- Do not add live Gmail tests or credentials.
- Do not change thread APIs that explicitly operate on thread IDs.

## Verification

- `make check`
- `python3 -m unittest discover -s tests -p "test*.py"`
- `python3 -m py_compile mail/rules.py tests/test_rules.py`
- `git diff --check`
- Mutations restoring `threadId` as the MIME fetch or cache identity must fail
  the repository contract.

Completed on 2026-06-12 with `make check`, the focused offline unittest suite,
Python 3 compilation, and diff hygiene checks passing.
