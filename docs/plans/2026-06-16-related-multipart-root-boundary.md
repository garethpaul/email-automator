# Related Multipart Root Boundary

## Status: In Progress

## Context

`select_inline_body_parts` traverses every child of `multipart/related` as if
each child were independent message body content. A later related `text/html`
resource can therefore enter the HTML candidate list and outrank the legitimate
plain-text root because `GetMimeMessage` prefers HTML candidates.

MIME related containers define one root body: the child referenced by the
`start` parameter, or the first child when `start` is absent. Other children are
related resources and must not become automated-reply input.

## Objectives

- Traverse only the MIME-defined root of each `multipart/related` container.
- Use the first child when no `start` parameter is present.
- Match an explicit `start` value to the child `Content-ID` before traversal.
- Fail closed when an explicit root cannot be resolved.
- Preserve nested `multipart/alternative`, ordinary inline body selection,
  attachment rejection, and encapsulated-message rejection.

## Scope

- Update `mail/body_parts.py` with a small related-root selector.
- Add real MIME regressions to `tests/test_body_parts.py` for implicit,
  explicit, and unresolved roots.
- Extend `scripts/check-baseline.sh` and maintained guidance.
- Do not change Gmail requests, reply rules, text decoding, dependencies,
  App Engine configuration, or outbound delivery.

## Verification

- Reproduce the related-resource override before implementation.
- Run focused body-part tests under available Python 2 and Python 3 runtimes.
- Run repository-root and external-directory `make check`.
- Reject isolated mutations covering implicit-root selection, explicit-root
  matching, unresolved-root failure, regression expectations, guidance, and
  completed-plan evidence.
- Audit exact paths, generated artifacts, credentials, dependency drift,
  conflict markers, file modes, and whitespace.

## Runtime Boundary

No App Engine, OAuth, Gmail, cron, memcache, browser, live mailbox, paired
provider, or outbound-delivery integration is available. This change is
stacked on PR #16 and must retain base-first merge ordering.
