# Related Multipart Root Boundary

## Status: Completed

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

## Work Completed

- Added a dedicated `multipart/related` root selector that uses the first
  child when `start` is absent, matches an explicit `start` against normalized
  child `Content-ID` values, and returns no candidate for an unresolved root.
- Kept related-root resolution ahead of generic multipart traversal while
  preserving attachment, named-part, and encapsulated-message boundaries.
- Added real MIME regressions for implicit, explicit, nested-alternative, and
  unresolved related roots, plus static contracts and synchronized guidance.

## Verification Completed

- The 8 focused body-part tests and all 68 offline tests passed under Python 2.7.18 and Python 3.12.8; byte-compilation also passed under both runtimes.
- repository-root and external-directory make check passed.
- Eight isolated hostile mutations were rejected; the mutations covered implicit-root selection,
  explicit `Content-ID` matching, unresolved-root failure, traversal ordering,
  regression expectations, maintained guidance, and completed-plan evidence.
- Exact diff, generated-artifact, credential, dependency, conflict-marker,
  file-mode, and whitespace audits passed for the intended paths.
- The implementation was committed as
  `b416487e6dd6dcb6f311d56701631a101b5b1fa1`.
- Canonical hosted verification passed on that exact implementation head:
  push run `27589720478` and pull-request run `27589725848` each completed
  successfully across Python 3.10, 3.12, and 3.14, including both dependency
  audit jobs. PR #17 remained open, clean, and mergeable, and the branch had no
  open code-scanning alerts.
- No App Engine, OAuth, Gmail, cron, memcache, browser, live mailbox, paired
  provider, or outbound-delivery integration was executed or claimed.
