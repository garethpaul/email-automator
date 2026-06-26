# Credential And Opt-In Setup

The maintained repository gate is intentionally credential-free. Use
`make check` for normal development. The steps below describe the boundaries
that an authorized operator must satisfy before attempting the historical live
App Engine/Gmail flow; they do not claim that the Python 2 runtime is currently
deployable.

## Credential Categories

- **Google Cloud/App Engine CLI credentials** belong to the operator's platform
  configuration outside this repository. Do not copy account credential files
  into the checkout.
- **OAuth client configuration** is supplied through `GOOGLE_CLIENT_ID` and
  `GOOGLE_CLIENT_SECRET`. This application does not require a checked-in client
  secrets JSON file.
- **OAuth access and refresh tokens** are managed by the legacy oauth2client
  App Engine datastore flow after `/auth`; do not export or commit them.
- **Mailbox policy** is supplied through `AUTOMATION_USER_ID`,
  `AUTOMATION_TO_EMAIL`, `AUTOMATION_FROM_EMAIL`, and
  `AUTOMATION_APPROVED_SENDERS`.

The OAuth decorator in `mail/auth.py` requests exactly these Gmail scopes:

- `https://www.googleapis.com/auth/gmail.modify`
- `https://www.googleapis.com/auth/gmail.send`

Both scopes permit mailbox side effects. Use a dedicated test mailbox and a
least-privilege OAuth client owned by the authorized Google Cloud project.

## Local Manifest Preflight

Tracked `app.yaml` contains empty placeholders only. Never add secrets to that
file. In an isolated legacy test checkout, create an ignored local copy:

```bash
cp app.yaml app.local.yaml
git check-ignore app.local.yaml
```

The second command must print `app.local.yaml` before any value is added. Stop
if it does not. Populate only the ignored copy, keep its permissions limited to
the operator, and delete it after the authorized test.

| Variable | Purpose |
| --- | --- |
| `GOOGLE_CLIENT_ID` | OAuth web client identifier for the authorized project. |
| `GOOGLE_CLIENT_SECRET` | OAuth web client secret; never log or commit it. |
| `AUTOMATION_USER_ID` | Deployment-owned key used to select stored Gmail credentials. It must match the isolated runtime's actual stored credential key. |
| `AUTOMATION_TO_EMAIL` | Mailbox address that inbound messages must target. |
| `AUTOMATION_FROM_EMAIL` | Validated address used for generated replies and rejected as an inbound sender. |
| `AUTOMATION_APPROVED_SENDERS` | Comma-separated allow-list of validated sender addresses. Start with one synthetic test sender. |

Do not use real customer, employer, or personal mailbox content as a fixture.

## Explicit Opt-In Order

1. Run `make check` from a clean exact-head checkout.
2. Create and verify ignored `app.local.yaml` as described above.
3. Use a dedicated test mailbox and synthetic messages only.
4. Deploy or run only inside an isolated App Engine-compatible environment
   whose platform credentials and callback URL are already authorized.
5. Visit `/auth` over HTTPS while logged in as the intended test operator and
   verify sanitized evidence that credentials were stored under the expected
   key before setting `AUTOMATION_USER_ID`.
6. Exercise `/mail/check` or `/mail/list` manually with cron disabled and verify
   that no reply is sent for an unapproved sender.
7. Add one synthetic approved sender and verify at most one expected reply.
8. Do not enable the cron schedule before authorization, mailbox identity,
   recipient matching, sender allow-list, duplicate reservation, and delivery
   evidence all pass for the exact commit.

Keep all live outcomes in `RUNTIME_VERIFICATION.md` as `not run` until sanitized
exact-head evidence exists. Never record tokens, mailbox identifiers, message
contents, recipient addresses, sender addresses, or local credential paths.

## Current Evidence

No OAuth, Gmail, App Engine, memcache, cron, or delivery flow was executed for
this documentation change. Portable verification proves only source contracts
and offline fixtures.
