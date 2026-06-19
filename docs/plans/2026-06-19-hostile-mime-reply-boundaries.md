# Hostile MIME and Reply Construction Boundaries

status: completed

## Scope

Review the aggregate PR #3-#17 Gmail MIME and reply path while reconciling the
separate debug-mode PR #2. Preserve the legacy Python 2 App Engine surface and
keep all verification credential-free.

## Findings

- Recursive MIME traversal accepted unbounded nesting and part counts, allowing
  a small hostile message to exhaust the Python call stack or accumulate a large
  candidate body set.
- `multipart/related` accepted the first matching `Content-ID`, so duplicate root
  identifiers made ownership ambiguous instead of failing closed.
- Only `message/rfc822` was excluded; other encapsulated `message/*` media types
  could contribute attacker-controlled descendants to automated reply rules.
- MIME parser recursion and messages without a selected inline body could escape
  the per-message boundary and abort the mailbox scan.
- Outbound replies used standard Base64 rather than Gmail's base64url wire format,
  and MIME header safety depended on upstream normalization instead of the reply
  construction boundary.

## Implementation

- Use iterative MIME traversal with explicit depth and part-count caps.
- Reject ambiguous related roots and all `message/*` descendants.
- Bound decoded text before HTML extraction or rule parsing.
- Isolate raw MIME parsing and convert parser recursion into message rejection.
- Centralize reply MIME construction, base64url encoding, and CR/LF/NUL header
  rejection in a dependency-free Python 2/3-compatible helper.

## Verification

- Added hostile raw MIME fixtures for deep nesting, excessive parts, duplicate
  related roots, `message/global`, and parser recursion exhaustion.
- Added offline reply encoding/header-injection tests and integration contracts.
- Repository-root and external-directory `make check` passed.
- Python 2.7 container and local Python 3 matrices passed.
- Eight isolated hostile source mutations were rejected.
- The exact legacy dependency pins were audited without resolving or installing
  the Python 2 application stack.
- Hosted pull-request and post-merge gates are recorded in the final PR outcome.

## Runtime Boundary

No App Engine server, OAuth flow, Gmail API request, live mailbox, memcache,
cron route, or outbound delivery was executed. The hosted and offline evidence
proves parser/rule/construction behavior only.
