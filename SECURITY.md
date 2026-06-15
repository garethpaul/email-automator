# Security Policy

Raw Gmail MIME values are strictly base64url-validated and capped at 25 MiB before MIME parsing.
Raw Gmail MIME values reject noncanonical pad bits before MIME parsing.

## Supported Versions

The supported security scope for `email-automator` is the current default branch, `master`. Older commits, tags, branches, forks, demos, and generated artifacts are not actively supported unless the repository explicitly marks them as maintained.

Project summary: Email Automator for Gmail

## Reporting a Vulnerability

Please report suspected vulnerabilities through GitHub's private vulnerability reporting or by opening a draft GitHub Security Advisory for `garethpaul/email-automator` when that option is available. If GitHub does not show a private reporting option for this repository, contact the repository owner through GitHub and avoid posting exploit details publicly until the issue can be assessed.

Do not open a public issue that includes exploit code, secrets, personal data, or detailed reproduction steps for an unpatched vulnerability.

## What to Include

Helpful reports include:

- the affected file, endpoint, permission, dependency, or workflow
- a concise impact statement explaining what an attacker could do
- reproduction steps using test data and accounts you control
- the branch, commit SHA, platform version, device, runtime, or dependency versions used
- logs, screenshots, or proof-of-concept snippets that demonstrate impact without exposing private data

## Project Security Posture

- This repository appears to be a Python project or notebook workflow. The active security scope is the code and documentation on the default branch.
- Review found authentication, token, or session-related code paths; changes in those areas should receive security-focused review before merge.
- Review found external API integrations or credential-adjacent configuration; changes in those areas should receive security-focused review before merge.
- Review found network clients, sockets, web APIs, or service endpoints; changes in those areas should receive security-focused review before merge.
- Review found mobile permission or privacy-sensitive data handling; changes in those areas should receive security-focused review before merge.
- Review found file, document, data, or media parsing flows; changes in those areas should receive security-focused review before merge.
- Review found database, model, query, or persistence-related code; changes in those areas should receive security-focused review before merge.
- Review found secret-like configuration names that require careful review before use; changes in those areas should receive security-focused review before merge.
- `requirements.txt` is an exact legacy Python 2/App Engine runtime boundary.
  Keep WebOb at 1.8.10 or newer within Python 2 compatibility, do not restore
  virtualenv as an application dependency, and avoid adding packages without a
  demonstrated deployed import.
- GitHub Actions runs the offline `make check` matrix on Python 3.10, 3.12, and
  3.14 with pinned actions, read-only repository access, and bounded jobs.
- App Engine, OAuth, Gmail, memcache, cron, inbound-mail, and delivery claims
  require the exact-head runtime verification matrix with synthetic accounts
  and sanitized evidence.

## Service and API Notes

For web services, APIs, sockets, or scraping workflows, prioritize reports involving authentication bypass, authorization errors, injection, server-side request forgery, unsafe deserialization, credential leakage, data exposure, or denial-of-service conditions. Use test accounts and minimal proof-of-concept traffic only.

Generated automated reply subjects should stay single-line and length-bounded
before sending so mailbox header handling is not exposed to raw inbound subject
text.
Malformed non-string body and subject values normalize to empty text before
rule matching or reply-subject generation, preventing decoded metadata shape
errors from crashing the offline automation decision.
Missing, unknown, and malformed MIME text charsets use UTF-8 replacement
fallback before automated rules consume HTML or plain text; attachments remain
outside automated rule input.

Configured automation email addresses should be validated before matching
senders or recipients so malformed environment values cannot trigger replies.
The approved-sender allow-list is read at authorization time so removing an
address does not depend on recycling the current process.
The validated outbound automation address is rejected as an inbound sender at
authorization time, even when accidentally allow-listed, preventing
self-generated reply loops before message reservation or Gmail delivery.

Mail routes select the stored Gmail credential key only from the deployment's
`AUTOMATION_USER_ID`; logged-in request input cannot override mailbox identity.
Whitespace-only AUTOMATION_USER_ID values are rejected as missing configuration.

Inbound malformed sender metadata should fail closed before duplicate-message
reservation or outbound delivery.
Inbound malformed recipient metadata is ignored or rejected before
duplicate-message reservation or outbound delivery.
Inbound authorization also requires exactly one structurally valid sender
identity; duplicate or mixed valid `From` entries fail closed before side
effects.

Outbound automation From addresses should be validated before creating Gmail
messages so malformed environment values cannot reach generated headers.

Automated reply rule matching is limited to the first 10000 characters of an
inbound body so unusually large messages do not drive unbounded local parsing.

Message IDs are normalized and length-bounded before duplicate-send cache keys
are used.

Normalized message IDs are atomically reserved in memcache before an automated
reply is sent. Concurrent processing of the same ID must stop before the Gmail
side effect, and failed sends must release their reservation for retry.

Gmail message IDs, not thread IDs, identify MIME fetches and parsed-message
cache entries. Missing or malformed summary IDs are skipped before cache or API
access so stale thread content cannot replace a later message.

## Dependency and Supply Chain Security

Dependency updates should come from trusted package managers and should keep lockfiles in sync when lockfiles exist. Do not commit credentials, private keys, tokens, generated secrets, or machine-local configuration. If a vulnerability depends on a compromised package, typosquatting risk, insecure transitive dependency, or unsafe build step, include the package name, affected version, and the path through which it is used.

Hosted dependency auditing checks the explicit legacy pins without resolving or
installing them on Python 3. This verifies known advisory status while keeping
the separate Python 2/App Engine runtime limitation explicit. The modern
offline rule matrix must remain dependency-free.

## Safe Research Guidelines

Good-faith research is welcome when it stays within these boundaries:

- use only accounts, devices, data, and infrastructure that you own or have explicit permission to test
- avoid destructive actions, persistence, spam, phishing, social engineering, or denial-of-service testing
- minimize access to personal data and stop testing immediately if private data is exposed
- do not exfiltrate secrets or third-party data; report the minimum evidence needed to verify impact
- keep vulnerability details confidential until the maintainer has assessed the report

## Maintainer Response

The maintainer will review complete reports as availability allows, prioritize issues by exploitability and impact, and coordinate a fix or mitigation when the affected code is still maintained. For sample, archived, or educational repositories, the likely remediation may be documentation, dependency updates, or clearly marking unsupported code rather than a production-style patch release.
