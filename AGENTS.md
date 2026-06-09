# AGENTS.md

## Repository purpose

`garethpaul/email-automator` is a legacy Python 2 Google App Engine prototype for scanning Gmail messages and generating automated replies from local rules. The live app paths require App Engine services and OAuth credentials; the default repository verification path only exercises offline rule behavior.

## Project structure

- `Makefile` - repository verification targets
- `scripts` - baseline checks and helper scripts
- `docs` - plans, notes, and generated README assets
- `tests` - tests and fixtures
- `requirements.txt` - Python runtime dependencies
- `libs` - checked-in runtime libraries or binary assets
- `database` - repository source or sample assets
- `googleapiclient` - repository source or sample assets
- `mail` - repository source or sample assets
- `oauth2client` - repository source or sample assets

## Development commands

- Install dependencies: `python3 -m pip install -r requirements.txt`
- Full baseline: `make check`
- Combined verification: `make verify`
- Lint/static checks: `make lint`
- Tests: `make test`
- Build: `make build`
- If a command above skips because a platform toolchain is missing, verify on a machine with that SDK before claiming platform behavior is tested.

## Coding conventions

- Prefer dependency-free tests or stdlib checks when legacy packages are unavailable.

## Testing guidance

- Test-related files detected: `libs/bs4/testing.py`, `libs/bs4/tests/`, `libs/bs4/tests/test_builder_registry.py`, `libs/bs4/tests/test_docs.py`, `libs/bs4/tests/test_html5lib.py`, `libs/bs4/tests/test_htmlparser.py`, `libs/bs4/tests/test_lxml.py`, `libs/bs4/tests/test_soup.py`, `libs/bs4/tests/test_tree.py`, `test.py`
- Start with the narrowest relevant test or Make target, then run `make check` before handing off if the change is not documentation-only.
- Keep README verification notes in sync when commands, fixtures, or supported toolchains change.

## PR / change guidance

- Keep diffs focused on the requested repository and avoid unrelated modernization or formatting churn.
- Preserve public APIs, sample behavior, file formats, and documented environment variables unless the task explicitly changes them.
- Update tests, README notes, or docs/plans when behavior, security posture, or validation commands change.
- Call out skipped platform validation, legacy toolchain assumptions, and any risky files touched in the final summary.

## Safety and gotchas

- The scan found credential-adjacent names. Review configuration paths before running against real accounts.
- Keep OAuth client IDs, OAuth client secrets, App Engine credentials, Gmail tokens, and real mailbox samples out of git.
- `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `AUTOMATION_USER_ID`, `AUTOMATION_TO_EMAIL`, `AUTOMATION_FROM_EMAIL`, and `AUTOMATION_APPROVED_SENDERS` are deployment/local configuration values.
- Configured sender and recipient email addresses are validated before reply rules use them; malformed values are ignored instead of triggering replies.
- Outbound `AUTOMATION_FROM_EMAIL` is validated before `CreateMessage` is called, and invalid From configuration prevents automated sends.
- Automated reply rule matching scans only a bounded inbound body prefix before generating response text.

## Agent workflow

1. Inspect the README, Makefile, manifests, and the files directly related to the request.
2. Make the smallest source or docs change that satisfies the task; avoid generated, vendored, or local-environment files unless required.
3. Run the narrowest useful validation first, then `make check` or the documented package/platform gate when available.
4. If a required SDK, service credential, or external runtime is unavailable, record the skipped command and why.
5. Summarize changed files, commands run, and remaining risks or follow-up validation.
