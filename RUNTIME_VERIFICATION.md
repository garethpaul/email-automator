# Email Automator Runtime Verification Matrix

Use this matrix for exact-head evidence that cannot be inferred from portable
tests. Run it only in an isolated App Engine-compatible environment with
synthetic mailboxes, messages, and OAuth accounts. Record sanitized outcomes;
never retain credentials, tokens, mailbox identifiers, message contents,
addresses, cookies, datastore values, screenshots, or logs.

Commit: pending implementation commit
Pull request: pending
Evidence status: not run

| # | Scenario | Boundary | Required sanitized evidence | Status |
|---|---|---|---|---|
| 1 | Legacy runtime setup | App Engine runtime | Python release, SDK class, service-emulator classes, and startup status | not run |
| 2 | App and cron configuration | Deployment config | Route class, login policy class, secure flag, cron target, and validation result | not run |
| 3 | OAuth authorization start | OAuth sandbox | Synthetic account class, redirect status, state result, and cookie class | not run |
| 4 | OAuth callback | OAuth sandbox | Callback class, token-storage result, redirect status, and error class | not run |
| 5 | Gmail mailbox listing | Gmail sandbox | Synthetic mailbox class, page-count bucket, message-count bucket, and error class | not run |
| 6 | Gmail MIME fetch and decode | Gmail sandbox | Message-shape class, MIME class, decoded-text class, and cache result | not run |
| 7 | Inbound mail handler | App Engine runtime | Synthetic sender/recipient classes, response status, and rule-evaluation result | not run |
| 8 | Approved sender authorization | App Engine runtime | Sender-cardinality class, configuration version, and authorization result | not run |
| 9 | Recipient and mailbox identity | App Engine runtime | Recipient-shape class, configured-user class, and acceptance result | not run |
| 10 | Rule matching and reply construction | App Engine runtime | Body/subject classes, matched-rule class, and reply-shape result | not run |
| 11 | Atomic message deduplication | Memcache emulator | Message-ID class, first reservation, duplicate result, and retry result | not run |
| 12 | Automated self-reply prevention | App Engine runtime | Sender/mailbox relation class, rejection result, and send-call count | not run |
| 13 | Outbound delivery | Mail sandbox | From/to classes, send result, failure class, and dedupe-release result | not run |
| 14 | Cron and restart behavior | App Engine runtime | Admin policy, cron result, cache persistence class, restart result, and duplicate-send delta | not run |

## Evidence Rules

- Replace the pending commit and pull-request fields with the exact tested head
  before recording any scenario as `pass`, `fail`, or `blocked`.
- Use only `pass`, `fail`, `blocked`, or `not run`; explain blockers without
  embedding secrets, private identifiers, message data, or machine paths.
- Keep portable Python 2/3 tests, local App Engine evidence, OAuth/Gmail sandbox
  evidence, memcache evidence, and outbound delivery evidence separate.
- A unit test, source compile, or static checker cannot mark an integration
  scenario as passed.

No App Engine server, OAuth flow, Gmail API call, memcache service, cron route,
inbound mail handler, or outbound delivery scenario was executed for this
documentation-only change.
