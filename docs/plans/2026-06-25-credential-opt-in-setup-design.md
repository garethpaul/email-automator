# Credential And Opt-In Setup Design

## Current State

- The maintained gate is credential-free and offline.
- `mail/auth.py` requests Gmail `modify` and `send` OAuth scopes.
- OAuth client values and automation mailbox settings come from environment
  variables declared as empty placeholders in tracked `app.yaml`.
- OAuth tokens are owned by the legacy App Engine oauth2client/datastore flow,
  not by a checked-in token file.

## Approaches Considered

### Recommended: documentation plus an ignored local manifest

Document the exact settings, scopes, opt-in order, and evidence boundary. Tell
operators to copy `app.yaml` to ignored `app.local.yaml` only inside an isolated
legacy environment and verify it is ignored before adding any values.

This closes the roadmap gap without expanding the frozen runtime or creating a
new secret-loading path.

### Rejected: put deployment values in tracked `app.yaml`

This is operationally simple but makes accidental credential commits likely
and conflicts with the repository's security boundary.

### Rejected: add dotenv or secret-manager integration

This would change application startup and deployment dependencies in a legacy
Python 2 runtime that cannot be exercised by the default gate. It belongs in a
dedicated platform migration, not a documentation change.

## Design

- Add `CREDENTIAL_SETUP.md` as the canonical live-setup boundary.
- Add `app.local.yaml` to `.gitignore` and require a preflight `git check-ignore`.
- Document all six configuration variables and the two exact Gmail scopes.
- Separate OAuth client configuration, platform credentials, stored OAuth
  tokens, mailbox identity, and approved-sender policy.
- Require explicit authorization before enabling cron or invoking mail routes.
- Keep every runtime row in `RUNTIME_VERIFICATION.md` as `not run` until an
  isolated exact-head environment produces sanitized evidence.

## Validation

- Mutation-sensitive static contracts protect the ignored manifest, scopes,
  variables, opt-in order, and no-live-runtime claim.
- The full offline `make check` gate remains authoritative for portable behavior.
