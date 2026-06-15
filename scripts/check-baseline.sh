#!/usr/bin/env sh
set -eu

ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
CHECK_PLAN="$ROOT_DIR/docs/plans/2026-06-08-email-check-wrapper.md"
VALID_EMAIL_PLAN="$ROOT_DIR/docs/plans/2026-06-09-email-valid-email-recipient-guard.md"
SUBJECT_PLAN="$ROOT_DIR/docs/plans/2026-06-09-email-reply-subject-normalization.md"
CONFIG_ADDRESS_PLAN="$ROOT_DIR/docs/plans/2026-06-09-email-config-address-validation.md"
FROM_ADDRESS_PLAN="$ROOT_DIR/docs/plans/2026-06-09-email-outbound-from-address-validation.md"
BODY_LIMIT_PLAN="$ROOT_DIR/docs/plans/2026-06-09-email-rule-body-length-limit.md"
MESSAGE_ID_PLAN="$ROOT_DIR/docs/plans/2026-06-09-email-message-id-cache-guard.md"
CI_PLAN="$ROOT_DIR/docs/plans/2026-06-10-ci-baseline.md"
ATOMIC_DEDUP_PLAN="$ROOT_DIR/docs/plans/2026-06-10-atomic-message-deduplication.md"
MALFORMED_SENDER_PLAN="$ROOT_DIR/docs/plans/2026-06-12-001-fix-malformed-sender-metadata-plan.md"
GMAIL_MESSAGE_ID_PLAN="$ROOT_DIR/docs/plans/2026-06-12-gmail-message-id-fetch-cache.md"
SENDER_REFRESH_PLAN="$ROOT_DIR/docs/plans/2026-06-12-approved-sender-config-refresh.md"
SELF_REPLY_PLAN="$ROOT_DIR/docs/plans/2026-06-13-email-self-reply-guard.md"
TEXT_BOUNDARY_PLAN="$ROOT_DIR/docs/plans/2026-06-13-email-text-boundary.md"
SENDER_CARDINALITY_PLAN="$ROOT_DIR/docs/plans/2026-06-13-email-sender-cardinality.md"
MIME_CHARSET_PLAN="$ROOT_DIR/docs/plans/2026-06-13-email-mime-charset-fallback.md"
LOCATION_INDEPENDENT_MAKE_PLAN="$ROOT_DIR/docs/plans/2026-06-13-location-independent-make.md"
RECIPIENT_METADATA_PLAN="$ROOT_DIR/docs/plans/2026-06-14-email-recipient-metadata-boundary.md"
CONFIGURED_USER_ID_PLAN="$ROOT_DIR/docs/plans/2026-06-14-configured-user-id-authority.md"
CONFIGURED_USER_ID_WHITESPACE_PLAN="$ROOT_DIR/docs/plans/2026-06-14-configured-user-id-whitespace.md"
RUNTIME_VERIFICATION="$ROOT_DIR/RUNTIME_VERIFICATION.md"
RUNTIME_VERIFICATION_PLAN="$ROOT_DIR/docs/plans/2026-06-14-email-automator-runtime-verification.md"
CONFIGURED_USER_ID_CHECK="$ROOT_DIR/scripts/check-configured-user-id.py"
RAW_MESSAGE_CHECK="$ROOT_DIR/scripts/check-raw-message-boundary.py"
RAW_MESSAGE_PLAN="$ROOT_DIR/docs/plans/2026-06-15-raw-gmail-mime-boundary.md"
CANONICAL_BASE64URL_PLAN="$ROOT_DIR/docs/plans/2026-06-15-canonical-gmail-base64url.md"
DEPENDENCY_PLAN="$ROOT_DIR/docs/plans/2026-06-12-patched-legacy-runtime-requirements.md"
CI_WORKFLOW="$ROOT_DIR/.github/workflows/check.yml"
REQUIREMENTS="$ROOT_DIR/requirements.txt"

cleanup_bytecode() {
  find "$ROOT_DIR" -maxdepth 1 -type f -name "*.pyc" -delete 2>/dev/null || true
  find "$ROOT_DIR/mail" "$ROOT_DIR/tests" -type d -name "__pycache__" -prune -exec rm -rf {} + 2>/dev/null || true
  find "$ROOT_DIR/mail" "$ROOT_DIR/tests" -type f -name "*.pyc" -delete 2>/dev/null || true
}

trap cleanup_bytecode EXIT

require_file() {
  path=$1
  if [ ! -f "$ROOT_DIR/$path" ]; then
    printf '%s\n' "Required file is missing: $path" >&2
    exit 1
  fi
}

for path in \
  "README.md" \
  "RUNTIME_VERIFICATION.md" \
  "SECURITY.md" \
  "requirements.txt" \
  "Makefile" \
  "VISION.md" \
  "CHANGES.md" \
  "app.yaml" \
  "cron.yaml" \
  ".github/workflows/check.yml" \
  "main.py" \
  "mail/auth.py" \
  "mail/check.py" \
  "mail/list.py" \
  "mail/raw_message.py" \
  "mail/rules.py" \
  "mail/text_payload.py" \
  "tests/test_rules.py" \
  "tests/test_raw_message.py" \
  "tests/test_text_payload.py" \
  "docs/plans/2026-06-09-email-recipient-address-guard.md" \
  "docs/plans/2026-06-09-email-config-address-validation.md" \
  "docs/plans/2026-06-09-email-outbound-from-address-validation.md" \
  "docs/plans/2026-06-09-email-message-id-cache-guard.md" \
  "docs/plans/2026-06-10-ci-baseline.md" \
  "docs/plans/2026-06-10-atomic-message-deduplication.md" \
  "docs/plans/2026-06-12-001-fix-malformed-sender-metadata-plan.md" \
  "docs/plans/2026-06-12-gmail-message-id-fetch-cache.md" \
  "docs/plans/2026-06-12-approved-sender-config-refresh.md" \
  "docs/plans/2026-06-13-email-self-reply-guard.md" \
  "docs/plans/2026-06-13-email-text-boundary.md" \
  "docs/plans/2026-06-13-email-sender-cardinality.md" \
  "docs/plans/2026-06-13-email-mime-charset-fallback.md" \
  "docs/plans/2026-06-13-location-independent-make.md" \
  "docs/plans/2026-06-14-email-recipient-metadata-boundary.md" \
  "docs/plans/2026-06-14-configured-user-id-authority.md" \
  "docs/plans/2026-06-14-configured-user-id-whitespace.md" \
  "docs/plans/2026-06-14-email-automator-runtime-verification.md" \
  "scripts/check-configured-user-id.py" \
  "scripts/check-raw-message-boundary.py" \
  "docs/plans/2026-06-15-raw-gmail-mime-boundary.md" \
  "docs/plans/2026-06-15-canonical-gmail-base64url.md" \
  "docs/plans/2026-06-12-patched-legacy-runtime-requirements.md" \
  "docs/plans/2026-06-09-email-rule-body-length-limit.md" \
  "docs/plans/2026-06-09-email-reply-subject-normalization.md" \
  "docs/plans/2026-06-09-email-valid-email-recipient-guard.md" \
  "docs/plans/2026-06-08-email-check-wrapper.md" \
  "docs/plans/2026-06-08-email-approved-sender-normalization.md" \
  "docs/plans/2026-06-08-email-rule-baseline.md" \
  "docs/plans/2026-06-08-app-engine-safety-baseline.md"; do
  require_file "$path"
done

for python2_test_contract in \
  'class CompatibleTestCase(unittest.TestCase):' \
  'if not hasattr(unittest.TestCase, "subTest"):' \
  'def subTest(self, **params):' \
  '# -*- coding: utf-8 -*-' \
  'from __future__ import unicode_literals' \
  'except ImportError:' \
  'imp.load_source("text_payload", TEXT_PAYLOAD_PATH)'; do
  if ! grep -Fq "$python2_test_contract" "$ROOT_DIR/tests/test_rules.py" "$ROOT_DIR/tests/test_text_payload.py"; then
    printf '%s\n' "Python 2 offline test compatibility contract is missing: $python2_test_contract" >&2
    exit 1
  fi
done

for runtime_contract in \
  "Commit: pending implementation commit" \
  "Pull request: pending" \
  "Evidence status: not run" \
  "isolated App Engine-compatible environment" \
  "Required sanitized evidence" \
  "Use only \`pass\`, \`fail\`, \`blocked\`, or \`not run\`" \
  "A unit test, source compile, or static checker cannot mark an integration" \
  "No App Engine server, OAuth flow, Gmail API call, memcache service, cron route,"; do
  if ! grep -Fq "$runtime_contract" "$RUNTIME_VERIFICATION"; then
    printf '%s\n' "Runtime verification matrix contract is missing: $runtime_contract" >&2
    exit 1
  fi
done

if [ "$(grep -Ec '^\| [0-9]+ \|' "$RUNTIME_VERIFICATION")" -ne 14 ] ||
  [ "$(grep -Ec '^\| [0-9]+ \|.*\| not run \|$' "$RUNTIME_VERIFICATION")" -ne 14 ]; then
  printf '%s\n' "Runtime verification matrix must retain 14 explicitly not-run scenarios." >&2
  exit 1
fi

for runtime_scenario in \
  "Legacy runtime setup" \
  "App and cron configuration" \
  "OAuth authorization start" \
  "OAuth callback" \
  "Gmail mailbox listing" \
  "Gmail MIME fetch and decode" \
  "Inbound mail handler" \
  "Approved sender authorization" \
  "Recipient and mailbox identity" \
  "Rule matching and reply construction" \
  "Atomic message deduplication" \
  "Automated self-reply prevention" \
  "Outbound delivery" \
  "Cron and restart behavior"; do
  if [ "$(grep -Fc "| $runtime_scenario |" "$RUNTIME_VERIFICATION")" -ne 1 ]; then
    printf '%s\n' "Runtime verification scenario is missing or duplicated: $runtime_scenario" >&2
    exit 1
  fi
done

for runtime_guidance in \
  "RUNTIME_VERIFICATION.md" \
  "synthetic mailboxes and messages" \
  "sanitized results"; do
  if ! grep -Fq "$runtime_guidance" "$ROOT_DIR/README.md"; then
    printf '%s\n' "README runtime verification guidance is missing: $runtime_guidance" >&2
    exit 1
  fi
done

if ! grep -Fq "Keep exact-head App Engine, OAuth, Gmail, memcache, cron, and delivery" "$ROOT_DIR/VISION.md" ||
  ! grep -Fq "App Engine, OAuth, Gmail, memcache, cron, inbound-mail, and delivery claims" "$ROOT_DIR/SECURITY.md" ||
  ! grep -Fq "Added an exact-head Email Automator runtime verification matrix" "$ROOT_DIR/CHANGES.md"; then
  printf '%s\n' "Project guidance must retain the Email Automator runtime evidence boundary." >&2
  exit 1
fi

for runtime_plan_contract in \
  "status: completed" \
  "## Status: Completed" \
  "## Work Completed" \
  "## Verification Completed" \
  "Python 2.7.18 and Python 3.12.8" \
  "Fourteen isolated hostile documentation and test-compatibility mutations" \
  "14 runtime scenarios remain"; do
  if ! grep -Fq "$runtime_plan_contract" "$RUNTIME_VERIFICATION_PLAN"; then
    printf '%s\n' "Runtime verification plan must record completed evidence: $runtime_plan_contract" >&2
    exit 1
  fi
done

python3 "$CONFIGURED_USER_ID_CHECK" "$ROOT_DIR/mail/list.py" "$ROOT_DIR/mail/check.py"
python3 "$RAW_MESSAGE_CHECK" "$ROOT_DIR/mail/raw_message.py" "$ROOT_DIR/mail/list.py" "$ROOT_DIR/tests/test_raw_message.py"

for raw_message_doc in AGENTS.md README.md SECURITY.md VISION.md CHANGES.md; do
  grep -Fq "Raw Gmail MIME values are strictly base64url-validated and capped at 25 MiB before MIME parsing." "$ROOT_DIR/$raw_message_doc" || exit 1
  grep -Fq "Raw Gmail MIME values reject noncanonical pad bits before MIME parsing." "$ROOT_DIR/$raw_message_doc" || exit 1
done

for raw_message_plan_contract in \
  "status: completed" \
  "## Work Completed" \
  "## Verification Completed" \
  "Python 2.7.18 and Python 3.12.8" \
  "all 58 offline tests" \
  "Ten isolated hostile mutations were rejected"; do
  grep -Fq "$raw_message_plan_contract" "$RAW_MESSAGE_PLAN" || exit 1
done

for canonical_base64url_plan_contract in \
  "status: completed" \
  "repository-root and external-directory make check passed" \
  "hostile mutations" \
  "No App Engine, OAuth, Gmail, mailbox, cron, or delivery integration was executed"; do
  if ! grep -Fqi "$canonical_base64url_plan_contract" "$CANONICAL_BASE64URL_PLAN"; then
    printf '%s\n' "Canonical Gmail base64url plan must record completion evidence: $canonical_base64url_plan_contract" >&2
    exit 1
  fi
done

for configured_user_id_doc in AGENTS.md README.md SECURITY.md VISION.md CHANGES.md; do
  grep -Fq "Whitespace-only AUTOMATION_USER_ID values are rejected as missing configuration." "$ROOT_DIR/$configured_user_id_doc" || exit 1
done

for mime_decoder_contract in \
  'TEXT_TYPE = unicode' \
  'charset = part.get_content_charset() or "utf-8"' \
  'payload.decode(charset, errors="replace")' \
  'except (LookupError, TypeError):' \
  'payload.decode("utf-8", errors="replace")' \
  'decode_text_payload(html[0])' \
  'decode_text_payload(text[0])'; do
  if ! grep -Fq "$mime_decoder_contract" "$ROOT_DIR/mail/text_payload.py" "$ROOT_DIR/mail/list.py"; then
    printf '%s\n' "MIME text decoding contract is missing: $mime_decoder_contract" >&2
    exit 1
  fi
done

for mime_test_contract in \
  "test_uses_valid_declared_charset" \
  "test_missing_charset_uses_utf8_replacement" \
  "test_unknown_charset_uses_utf8_replacement" \
  "test_malformed_declared_charset_bytes_are_replaced" \
  "test_string_payload_is_preserved" \
  "test_absent_payload_becomes_empty_text"; do
  if ! grep -Fq "$mime_test_contract" "$ROOT_DIR/tests/test_text_payload.py"; then
    printf '%s\n' "MIME decoder test contract is missing: $mime_test_contract" >&2
    exit 1
  fi
done

if ! grep -Fq "malformed MIME text charsets" "$ROOT_DIR/README.md" ||
  ! grep -Fq "malformed MIME text charsets" "$ROOT_DIR/SECURITY.md" ||
  ! grep -Fq "MIME text decoding fails closed" "$ROOT_DIR/VISION.md" ||
  ! grep -Fq "Normalized missing, unknown, and malformed MIME charsets" "$ROOT_DIR/CHANGES.md" ||
  ! grep -Fq "unknown MIME text charsets" "$ROOT_DIR/AGENTS.md"; then
  printf '%s\n' "MIME charset fallback documentation must remain synchronized." >&2
  exit 1
fi

for mime_plan_contract in \
  "status: completed" \
  "## Status: Completed" \
  "6 focused tests" \
  "make verify" \
  "isolated hostile mutations were rejected" \
  "No live Gmail or App Engine execution is claimed"; do
  if ! grep -Fq "$mime_plan_contract" "$MIME_CHARSET_PLAN"; then
    printf '%s\n' "MIME charset plan must record completed verification: $mime_plan_contract" >&2
    exit 1
  fi
done

for sender_cardinality_contract in \
  "if len(normalized_senders) != 1" \
  "normalized_address, address = normalized_senders[0]" \
  "test_approved_sender_rejects_duplicate_valid_entries" \
  "test_approved_sender_rejects_mixed_valid_entries_in_any_order" \
  "test_valid_email_rejects_ambiguous_sender_metadata_without_side_effects"; do
  if ! grep -Fq "$sender_cardinality_contract" "$ROOT_DIR/mail/rules.py" "$ROOT_DIR/tests/test_rules.py"; then
    printf '%s\n' "Sender identity cardinality contract is missing: $sender_cardinality_contract" >&2
    exit 1
  fi
done

if ! grep -Fq "status: completed" "$SENDER_CARDINALITY_PLAN" ||
  ! grep -Fq "Python 3.12.8 and Python 3.14.0" "$SENDER_CARDINALITY_PLAN" ||
  ! grep -Fq "hostile mutations were rejected" "$SENDER_CARDINALITY_PLAN" ||
  ! grep -Fq "No OAuth" "$SENDER_CARDINALITY_PLAN"; then
  printf '%s\n' "Email sender cardinality plan must record truthful completed verification." >&2
  exit 1
fi

if ! grep -Fq 'duplicate or mixed valid `From` entries fail closed' "$ROOT_DIR/README.md" ||
  ! grep -Fq 'duplicate or mixed valid `From` entries fail closed' "$ROOT_DIR/SECURITY.md" ||
  ! grep -Fq "ambiguous multi-sender metadata is rejected" "$ROOT_DIR/VISION.md" ||
  ! grep -Fq "Ambiguous multi-sender metadata now fails closed" "$ROOT_DIR/CHANGES.md"; then
  printf '%s\n' "Project docs must preserve the sender identity cardinality boundary." >&2
  exit 1
fi

EXPECTED_REQUIREMENTS='webob==1.8.10
webapp2==2.5.2
uritemplate==0.6
webtest==2.0.21'
if [ "$(cat "$REQUIREMENTS")" != "$EXPECTED_REQUIREMENTS" ]; then
  printf '%s\n' "requirements.txt must keep the exact patched legacy runtime boundary." >&2
  exit 1
fi

if grep -Eiq '(^|[[:space:]])virtualenv([<=>[:space:]]|$)' "$REQUIREMENTS"; then
  printf '%s\n' "requirements.txt must not restore unused virtualenv tooling." >&2
  exit 1
fi

for sender_refresh_contract in \
  "allowed = set(configured_from_users())" \
  "test_approved_sender_uses_current_environment_allowlist"; do
  if ! grep -Fq "$sender_refresh_contract" "$ROOT_DIR/mail/rules.py" "$ROOT_DIR/tests/test_rules.py"; then
    printf '%s\n' "Approved-sender refresh contract is missing: $sender_refresh_contract" >&2
    exit 1
  fi
done

for self_reply_contract in \
  "automation_address = configured_from_email()" \
  "normalized_address == automation_address" \
  "test_approved_sender_fails_closed_when_self_address_precedes_allowed_address" \
  "test_approved_sender_fails_closed_when_self_address_follows_allowed_address" \
  "test_approved_sender_rejects_configured_automation_address" \
  "test_approved_sender_refreshes_automation_address" \
  "test_valid_email_rejects_automation_sender_before_reservation"; do
  if ! grep -Fq "$self_reply_contract" "$ROOT_DIR/mail/rules.py" "$ROOT_DIR/tests/test_rules.py"; then
    printf '%s\n' "Automation self-reply guard is missing: $self_reply_contract" >&2
    exit 1
  fi
done

if ! grep -Fq "status: completed" "$SELF_REPLY_PLAN" ||
  ! grep -Fq "all 39 offline tests passed" "$SELF_REPLY_PLAN" ||
  ! grep -Fq "Removing the self-sender comparison failed" "$SELF_REPLY_PLAN" ||
  ! grep -Fq "raw environment read" "$SELF_REPLY_PLAN" ||
  ! grep -Fq "git diff --check" "$SELF_REPLY_PLAN"; then
  printf '%s\n' "Email self-reply guard plan must record completed verification." >&2
  exit 1
fi

if grep -Fq "from_users = configured_from_users()" "$ROOT_DIR/mail/rules.py"; then
  printf '%s\n' "Approved senders must not be cached at module import time." >&2
  exit 1
fi

if ! grep -Fq "status: completed" "$SENDER_REFRESH_PLAN" ||
  ! grep -Fq 'Local Python 3.12.8 and 3.14.0: `make check` passed all 34 offline tests and' "$SENDER_REFRESH_PLAN" ||
  ! grep -Fq "Five isolated hostile mutations were rejected" "$SENDER_REFRESH_PLAN"; then
  printf '%s\n' "Approved-sender refresh plan must remain completed and verified." >&2
  exit 1
fi

for document in "$ROOT_DIR/README.md" "$ROOT_DIR/SECURITY.md" "$ROOT_DIR/VISION.md" "$ROOT_DIR/CHANGES.md"; do
  if ! grep -Fq "authorization time" "$document"; then
    printf '%s\n' "$document must document approved-sender refresh at authorization time." >&2
    exit 1
  fi
done

for document in "$ROOT_DIR/README.md" "$ROOT_DIR/SECURITY.md" "$ROOT_DIR/VISION.md" "$ROOT_DIR/CHANGES.md"; do
  if ! grep -Fq "self-generated reply loops" "$document"; then
    printf '%s\n' "$document must document automation self-sender rejection." >&2
    exit 1
  fi
done

for document in "$ROOT_DIR/README.md" "$ROOT_DIR/SECURITY.md" "$ROOT_DIR/VISION.md" "$ROOT_DIR/CHANGES.md"; do
  if ! grep -Fq "WebOb" "$document" || ! grep -Fq "virtualenv" "$document"; then
    printf '%s\n' "$document must document patched WebOb and removed virtualenv tooling." >&2
    exit 1
  fi
done

if [ "$(grep -Fci 'status: completed' "$DEPENDENCY_PLAN")" -ne 1 ] ||
  ! grep -Fq "## Work Completed" "$DEPENDENCY_PLAN" ||
  ! grep -Fq "## Verification Results" "$DEPENDENCY_PLAN" ||
  ! grep -Fq "no known" "$DEPENDENCY_PLAN" ||
  ! grep -Fq "34 offline tests" "$DEPENDENCY_PLAN" ||
  ! grep -Fq "330cab60f6c2cf4dca878519563ec8517d37e1d2" "$DEPENDENCY_PLAN" ||
  ! grep -Fq "27430550372" "$DEPENDENCY_PLAN" ||
  ! grep -Fq "27430552862" "$DEPENDENCY_PLAN" ||
  ! grep -Fq "27430550455" "$DEPENDENCY_PLAN"; then
  printf '%s\n' "Patched legacy requirements plan must remain completed and verified." >&2
  exit 1
fi

if grep -Eiq '\b(planned|pending|todo|tbd)\b' "$DEPENDENCY_PLAN"; then
  printf '%s\n' "Patched legacy requirements plan must not retain unfinished markers." >&2
  exit 1
fi

for gmail_message_contract in \
  "def gmail_message_id" \
  "message_id = rules.gmail_message_id(msg)" \
  'cache_key = "messageId_" + message_id' \
  "GetMimeMessage(service, user_id, message_id)" \
  "test_gmail_message_id_uses_message_id_not_thread_id" \
  "test_gmail_message_id_rejects_malformed_summaries"; do
  if ! grep -Fq "$gmail_message_contract" "$ROOT_DIR/mail/rules.py" "$ROOT_DIR/mail/list.py" "$ROOT_DIR/tests/test_rules.py"; then
    printf '%s\n' "Gmail message-ID fetch/cache contract is missing: $gmail_message_contract" >&2
    exit 1
  fi
done

if grep -Fq 'GetMimeMessage(service, user_id, threadId)' "$ROOT_DIR/mail/list.py" ||
  grep -Fq 'memcache.get("threadId_"' "$ROOT_DIR/mail/list.py"; then
  printf '%s\n' "Gmail MIME retrieval and caching must not use threadId as message identity." >&2
  exit 1
fi

for document in "$ROOT_DIR/README.md" "$ROOT_DIR/SECURITY.md" "$ROOT_DIR/VISION.md" "$ROOT_DIR/CHANGES.md"; do
  if ! grep -Fq "Gmail message IDs" "$document"; then
    printf '%s\n' "$document must document message-ID keyed Gmail fetches and caching." >&2
    exit 1
  fi
done

for sender_contract in \
  "senders = msg.get('from') or []" \
  "not isinstance(senders, (list, tuple))" \
  "not isinstance(sender, (list, tuple))" \
  "len(sender) != 2" \
  "test_approved_sender_ignores_malformed_entries" \
  "test_approved_sender_rejects_malformed_sender_collections" \
  "test_approved_sender_accepts_valid_entry_after_malformed_entries" \
  "test_valid_email_rejects_malformed_sender_metadata_without_side_effects"; do
  if ! grep -Fq "$sender_contract" "$ROOT_DIR/mail/rules.py" "$ROOT_DIR/tests/test_rules.py"; then
    printf '%s\n' "Malformed sender metadata contract is missing: $sender_contract" >&2
    exit 1
  fi
done

if ! grep -Fq "Malformed Sender Metadata Guard" "$MALFORMED_SENDER_PLAN" ||
  ! grep -Fq "make check" "$MALFORMED_SENDER_PLAN"; then
  printf '%s\n' "Malformed sender metadata plan must document repository verification." >&2
  exit 1
fi

for document in "$ROOT_DIR/README.md" "$ROOT_DIR/SECURITY.md" "$ROOT_DIR/VISION.md" "$ROOT_DIR/CHANGES.md"; do
  if ! grep -Fq "malformed sender metadata" "$document"; then
    printf '%s\n' "$document must document malformed sender metadata rejection." >&2
    exit 1
  fi
done

(cd "$ROOT_DIR" && python3 -m py_compile mail/rules.py tests/test_rules.py)
(cd "$ROOT_DIR" && python3 -m unittest discover -s tests -p "test*.py")

if command -v python2 >/dev/null 2>&1; then
  python2 -m py_compile \
    "$ROOT_DIR/main.py" \
    "$ROOT_DIR/mail/auth.py" \
    "$ROOT_DIR/mail/check.py" \
    "$ROOT_DIR/mail/list.py" \
    "$ROOT_DIR/mail/rules.py"
else
  printf '%s\n' "Skipping Python 2 syntax check: python2 is not installed."
fi

if ! grep -Fq "status: completed" "$ROOT_DIR/docs/plans/2026-06-08-email-rule-baseline.md" ||
  ! grep -Fq "status: completed" "$ROOT_DIR/docs/plans/2026-06-08-app-engine-safety-baseline.md" ||
  ! grep -Fq "status: completed" "$ROOT_DIR/docs/plans/2026-06-08-email-approved-sender-normalization.md" ||
  ! grep -Fq "status: completed" "$ROOT_DIR/docs/plans/2026-06-09-email-recipient-address-guard.md" ||
  ! grep -Fq "status: completed" "$VALID_EMAIL_PLAN" ||
  ! grep -Fq "status: completed" "$CONFIG_ADDRESS_PLAN" ||
  ! grep -Fq "status: completed" "$FROM_ADDRESS_PLAN" ||
  ! grep -Fq "status: completed" "$BODY_LIMIT_PLAN" ||
  ! grep -Fq "Status: Completed" "$MESSAGE_ID_PLAN" ||
  ! grep -Fqi "status: completed" "$CI_PLAN" ||
  ! grep -Fq "status: completed" "$SUBJECT_PLAN" ||
  ! grep -Fq "status: completed" "$CHECK_PLAN"; then
  printf '%s\n' "Plans must be marked completed." >&2
  exit 1
fi

if ! grep -Fq "make check" "$CI_PLAN"; then
  printf '%s\n' "CI baseline plan must record make check verification." >&2
  exit 1
fi

if ! grep -Fq "Status: Completed" "$ATOMIC_DEDUP_PLAN" ||
  ! grep -Fq "make check" "$ATOMIC_DEDUP_PLAN"; then
  printf '%s\n' "Atomic message deduplication plan must remain completed with verification recorded." >&2
  exit 1
fi

if ! grep -Fq "status: completed" "$GMAIL_MESSAGE_ID_PLAN" ||
  ! grep -Fq "make check" "$GMAIL_MESSAGE_ID_PLAN"; then
  printf '%s\n' "Gmail message-ID fetch/cache plan must remain completed with verification recorded." >&2
  exit 1
fi

if ! grep -Fq "actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10" "$CI_WORKFLOW" ||
  ! grep -Fq "actions/setup-python@a309ff8b426b58ec0e2a45f0f869d46889d02405" "$CI_WORKFLOW" ||
  ! grep -Fq 'python-version: ["3.10", "3.12", "3.14"]' "$CI_WORKFLOW" ||
  ! grep -Fq 'python-version: ${{ matrix.python-version }}' "$CI_WORKFLOW" ||
  ! grep -Fq 'python-version: "3.12"' "$CI_WORKFLOW" ||
  ! grep -Fq "run: make check" "$CI_WORKFLOW" ||
  ! grep -Fq "dependency-audit:" "$CI_WORKFLOW" ||
  ! grep -Fq "python -m pip install pip-audit==2.10.0" "$CI_WORKFLOW" ||
  ! grep -Fq "pip-audit --disable-pip --no-deps -r requirements.txt" "$CI_WORKFLOW" ||
  [ "$(grep -Fc 'persist-credentials: false' "$CI_WORKFLOW")" -ne 2 ] ||
  [ "$(grep -Fc 'runs-on: ubuntu-24.04' "$CI_WORKFLOW")" -ne 2 ] ||
  ! grep -Fq "permissions:" "$CI_WORKFLOW" ||
  ! grep -Fq "contents: read" "$CI_WORKFLOW" ||
  ! grep -Fq "workflow_dispatch:" "$CI_WORKFLOW" ||
  ! grep -Fq "cancel-in-progress: true" "$CI_WORKFLOW" ||
  ! grep -Fq "timeout-minutes: 5" "$CI_WORKFLOW"; then
  printf '%s\n' "GitHub Actions workflow must run the pinned, read-only make check matrix." >&2
  exit 1
fi

if ! grep -Fq "make check" "$SUBJECT_PLAN"; then
  printf '%s\n' "Reply subject normalization plan must record make check verification." >&2
  exit 1
fi

if ! grep -Fq "make check" "$CONFIG_ADDRESS_PLAN"; then
  printf '%s\n' "Config address validation plan must record make check verification." >&2
  exit 1
fi

if ! grep -Fq "make check" "$FROM_ADDRESS_PLAN"; then
  printf '%s\n' "Outbound From address validation plan must record make check verification." >&2
  exit 1
fi

if ! grep -Fq "make check" "$BODY_LIMIT_PLAN"; then
  printf '%s\n' "Email rule body length limit plan must record make check verification." >&2
  exit 1
fi

if ! grep -Fq "make check" "$MESSAGE_ID_PLAN"; then
  printf '%s\n' "Message ID cache guard plan must record make check verification." >&2
  exit 1
fi

if ! grep -Fq "scripts/check-baseline.sh" "$ROOT_DIR/README.md" ||
  ! grep -Fq "make check" "$ROOT_DIR/README.md" ||
  ! grep -Fq "GitHub Actions" "$ROOT_DIR/README.md" ||
  ! grep -Fq "offline" "$ROOT_DIR/README.md" ||
  ! grep -Fq "OAuth" "$ROOT_DIR/README.md" ||
  ! grep -Fq "Gmail" "$ROOT_DIR/README.md"; then
  printf '%s\n' "README must document make check, offline tests, and Gmail/OAuth boundaries." >&2
  exit 1
fi

if ! grep -Fq "reply subject normalization" "$ROOT_DIR/README.md"; then
  printf '%s\n' "README must document reply subject normalization." >&2
  exit 1
fi

if ! grep -Fq "Configured sender and recipient email addresses are validated" "$ROOT_DIR/README.md"; then
  printf '%s\n' "README must document configured email address validation." >&2
  exit 1
fi

if ! grep -Fq "Outbound \`AUTOMATION_FROM_EMAIL\` is validated" "$ROOT_DIR/README.md"; then
  printf '%s\n' "README must document outbound From address validation." >&2
  exit 1
fi

if ! grep -Fq "Automated reply rule matching scans only the first 10000 characters" "$ROOT_DIR/README.md"; then
  printf '%s\n' "README must document the rule body length limit." >&2
  exit 1
fi

if ! grep -Fq "Message IDs are normalized and length-bounded" "$ROOT_DIR/README.md"; then
  printf '%s\n' "README must document message ID cache-key validation." >&2
  exit 1
fi

if ! grep -Fq "single-line and length-bounded" "$ROOT_DIR/SECURITY.md"; then
  printf '%s\n' "SECURITY must document reply subject header handling." >&2
  exit 1
fi

if ! grep -Fq "Configured automation email addresses" "$ROOT_DIR/SECURITY.md"; then
  printf '%s\n' "SECURITY must document configured email address validation." >&2
  exit 1
fi

if ! grep -Fq "Outbound automation From addresses" "$ROOT_DIR/SECURITY.md"; then
  printf '%s\n' "SECURITY must document outbound From address validation." >&2
  exit 1
fi

if ! grep -Fq "Automated reply rule matching is limited to the first 10000 characters" "$ROOT_DIR/SECURITY.md"; then
  printf '%s\n' "SECURITY must document the rule body length limit." >&2
  exit 1
fi

if ! grep -Fq "Message IDs are normalized and length-bounded" "$ROOT_DIR/SECURITY.md"; then
  printf '%s\n' "SECURITY must document message ID cache-key validation." >&2
  exit 1
fi

if ! grep -Fq "GitHub Actions" "$ROOT_DIR/SECURITY.md" ||
  ! grep -Fq "make check" "$ROOT_DIR/SECURITY.md"; then
  printf '%s\n' "SECURITY must document the hosted CI verification boundary." >&2
  exit 1
fi

if ! grep -Fq "GitHub Actions" "$ROOT_DIR/VISION.md" ||
  ! grep -Fq "docs/plans/2026-06-10-ci-baseline.md" "$ROOT_DIR/README.md" ||
  ! grep -Fq "GitHub Actions" "$ROOT_DIR/CHANGES.md"; then
  printf '%s\n' "Project docs must record the GitHub Actions CI baseline." >&2
  exit 1
fi

if ! grep -Fq "check: verify" "$ROOT_DIR/Makefile"; then
  printf '%s\n' "Makefile must expose make check as the repository verification wrapper." >&2
  exit 1
fi

if ! grep -Fq "build:" "$ROOT_DIR/Makefile" ||
  ! grep -Fq "verify: lint test build" "$ROOT_DIR/Makefile"; then
  printf '%s\n' "Makefile must expose make build and include it in verification." >&2
  exit 1
fi

if ! grep -Fq 'ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))' "$ROOT_DIR/Makefile" ||
  ! grep -Fq '"$(ROOT)/scripts/check-baseline.sh"' "$ROOT_DIR/Makefile" ||
  ! grep -Fq 'cd "$(ROOT)" && $(PYTHON) -m unittest discover' "$ROOT_DIR/Makefile" ||
  ! grep -Fq '"$(ROOT)/mail/rules.py"' "$ROOT_DIR/Makefile" ||
  ! grep -Fq '"$(ROOT)/tests/test_text_payload.py"' "$ROOT_DIR/Makefile"; then
  printf '%s\n' "Makefile verification commands must resolve paths from the loaded Makefile." >&2
  exit 1
fi

if ! grep -Eq '^\(cd "\$ROOT_DIR" && python3 -m py_compile mail/rules\.py tests/test_rules\.py\)$' "$ROOT_DIR/scripts/check-baseline.sh" ||
  ! grep -Eq '^\(cd "\$ROOT_DIR" && python3 -m unittest discover -s tests -p "test\*\.py"\)$' "$ROOT_DIR/scripts/check-baseline.sh"; then
  printf '%s\n' "Baseline checker Python probes must run from the repository root." >&2
  exit 1
fi

if ! grep -Fq "status: completed" "$LOCATION_INDEPENDENT_MAKE_PLAN" ||
  ! grep -Fq "from /tmp" "$LOCATION_INDEPENDENT_MAKE_PLAN"; then
  printf '%s\n' "Location-independent Make plan must record completed status and external verification." >&2
  exit 1
fi

if grep -R "dial 911" "$ROOT_DIR/mail" "$ROOT_DIR/tests" >/dev/null; then
  printf '%s\n' "Automated fallback replies must not mention dialing 911." >&2
  exit 1
fi

if ! grep -Fq "_LocalMemcache" "$ROOT_DIR/mail/rules.py" ||
  ! grep -Fq "cache_key" "$ROOT_DIR/mail/rules.py" ||
  ! grep -Fq "normalize_email_address" "$ROOT_DIR/mail/rules.py" ||
  ! grep -Fq "test_valid_email_sends_approved_message_once" "$ROOT_DIR/tests/test_rules.py" ||
  ! grep -Fq "test_approved_sender_matches_address_case_insensitively" "$ROOT_DIR/tests/test_rules.py" ||
  ! grep -Fq "test_configured_from_users_reads_environment" "$ROOT_DIR/tests/test_rules.py"; then
  printf '%s\n' "Offline rules baseline must keep local cache and duplicate-send coverage." >&2
  exit 1
fi

if ! grep -Fq "def tokenize_email" "$ROOT_DIR/mail/rules.py" ||
  ! grep -Fq "MAX_EMAIL_BODY_LENGTH" "$ROOT_DIR/mail/rules.py" ||
  ! grep -Fq "def bounded_email_body" "$ROOT_DIR/mail/rules.py" ||
  ! grep -Fq "Gareth," "$ROOT_DIR/tests/test_rules.py"; then
  printf '%s\n' "Rule tests must cover punctuation-tolerant keyword matching." >&2
  exit 1
fi

if ! grep -Fq "test_tokenize_email_ignores_text_after_body_limit" "$ROOT_DIR/tests/test_rules.py" ||
  ! grep -Fq "MAX_EMAIL_BODY_LENGTH" "$ROOT_DIR/tests/test_rules.py" ||
  ! grep -Fq "Rule matching is limited to the first 10000 characters" "$ROOT_DIR/VISION.md"; then
  printf '%s\n' "Rule tests and docs must cover bounded inbound body matching." >&2
  exit 1
fi

if ! grep -Fq "MAX_REPLY_SUBJECT_LENGTH" "$ROOT_DIR/mail/rules.py" ||
  ! grep -Fq "def reply_subject" "$ROOT_DIR/mail/rules.py" ||
  ! grep -Fq "reply_subject(msg.get('subject', \"\"))" "$ROOT_DIR/mail/rules.py" ||
  ! grep -Fq "test_reply_subject_removes_header_breaks" "$ROOT_DIR/tests/test_rules.py" ||
  ! grep -Fq "test_valid_email_sanitizes_reply_subject" "$ROOT_DIR/tests/test_rules.py"; then
  printf '%s\n' "Rule tests must cover single-line reply subject normalization." >&2
  exit 1
fi

for text_boundary_contract in \
  "def text_value" \
  "isinstance(value, STRING_TYPES)" \
  "return text_value(txt)[:MAX_EMAIL_BODY_LENGTH]" \
  "text_value(subject).splitlines()" \
  "test_rule_matching_treats_malformed_body_values_as_empty" \
  "test_reply_subject_treats_malformed_values_as_empty"; do
  if ! grep -Fq "$text_boundary_contract" "$ROOT_DIR/mail/rules.py" "$ROOT_DIR/tests/test_rules.py"; then
    printf '%s\n' "Email text boundary contract is missing: $text_boundary_contract" >&2
    exit 1
  fi
done

if grep -Fq 'return (txt or "")[:MAX_EMAIL_BODY_LENGTH]' "$ROOT_DIR/mail/rules.py" ||
  grep -Fq '(subject or "").splitlines()' "$ROOT_DIR/mail/rules.py"; then
  printf '%s\n' "Rule text handling must not slice or split malformed values directly." >&2
  exit 1
fi

if ! grep -Fq "status: completed" "$TEXT_BOUNDARY_PLAN" ||
  ! grep -Fq "Python 3.12.8 and Python 3.14.0" "$TEXT_BOUNDARY_PLAN" ||
  ! grep -Fq "hostile mutations were rejected" "$TEXT_BOUNDARY_PLAN" ||
  ! grep -Fq "no Gmail" "$TEXT_BOUNDARY_PLAN"; then
  printf '%s\n' "Email text boundary plan must record truthful completed verification." >&2
  exit 1
fi

for document in "$ROOT_DIR/README.md" "$ROOT_DIR/SECURITY.md" "$ROOT_DIR/VISION.md" "$ROOT_DIR/CHANGES.md"; do
  if ! grep -Fq "Malformed non-string" "$document"; then
    printf '%s\n' "$document must document fail-closed malformed text handling." >&2
    exit 1
  fi
done

if ! grep -Fq "Malformed non-string body and subject values" "$ROOT_DIR/AGENTS.md"; then
  printf '%s\n' "AGENTS.md must retain the malformed text input boundary." >&2
  exit 1
fi

if ! grep -Fq "MAX_MESSAGE_ID_LENGTH" "$ROOT_DIR/mail/rules.py" ||
  ! grep -Fq "def normalize_message_id" "$ROOT_DIR/mail/rules.py" ||
  ! grep -Fq "MESSAGE_ID_RE" "$ROOT_DIR/mail/rules.py" ||
  ! grep -Fq "test_cache_key_rejects_malformed_message_ids" "$ROOT_DIR/tests/test_rules.py" ||
  ! grep -Fq "test_valid_email_rejects_invalid_message_id" "$ROOT_DIR/tests/test_rules.py" ||
  ! grep -Fq "Message IDs are normalized and length-bounded" "$ROOT_DIR/VISION.md"; then
  printf '%s\n' "Rule tests and docs must cover message ID cache-key validation." >&2
  exit 1
fi

for dedup_contract in \
  "def reserve_message_id" \
  "memcache.add(key, msgId)" \
  "def release_message_id" \
  "memcache.delete(key)" \
  "if msgId and reserve_message_id(msgId)" \
  "test_valid_email_reserves_message_before_sending" \
  "test_valid_email_releases_reservation_after_failed_send" \
  "test_valid_email_releases_reservation_after_send_exception"; do
  if ! grep -Fq "$dedup_contract" "$ROOT_DIR/mail/rules.py" "$ROOT_DIR/tests/test_rules.py"; then
    printf '%s\n' "Atomic message deduplication contract is missing: $dedup_contract" >&2
    exit 1
  fi
done

if ! grep -Fq "APP_DEBUG" "$ROOT_DIR/main.py" ||
  ! grep -Fq "debug=DEBUG" "$ROOT_DIR/main.py" ||
  ! grep -Fq "APP_DEBUG" "$ROOT_DIR/app.yaml"; then
  printf '%s\n' "App debug mode must stay environment-gated." >&2
  exit 1
fi

if ! grep -Fq "login: admin" "$ROOT_DIR/app.yaml" ||
  ! grep -Fq "secure: always" "$ROOT_DIR/app.yaml" ||
  ! grep -Fq "GOOGLE_CLIENT_ID" "$ROOT_DIR/app.yaml" ||
  ! grep -Fq "GOOGLE_CLIENT_SECRET" "$ROOT_DIR/app.yaml" ||
  ! grep -Fq "AUTOMATION_USER_ID" "$ROOT_DIR/app.yaml" ||
  ! grep -Fq "GOOGLE_CLIENT_ID" "$ROOT_DIR/mail/auth.py" ||
  ! grep -Fq "GOOGLE_CLIENT_SECRET" "$ROOT_DIR/mail/auth.py"; then
  printf '%s\n' "App Engine auth routes and OAuth config must keep safety guardrails." >&2
  exit 1
fi

if grep -Fq "userId=XXXXX" "$ROOT_DIR/cron.yaml"; then
  printf '%s\n' "cron.yaml must not include a committed userId query placeholder." >&2
  exit 1
fi

if ! grep -Fq "AUTOMATION_USER_ID" "$ROOT_DIR/mail/list.py" ||
  ! grep -Fq "AUTOMATION_USER_ID" "$ROOT_DIR/mail/check.py" ||
  ! grep -Fq "def configured_to_email" "$ROOT_DIR/mail/rules.py" ||
  ! grep -Fq "def message_addressed_to_automation" "$ROOT_DIR/mail/rules.py" ||
  ! grep -Fq "if not message_addressed_to_automation(msg)" "$ROOT_DIR/mail/rules.py" ||
  ! grep -Fq "message_addressed_to_automation(msg)" "$ROOT_DIR/mail/list.py" ||
  ! grep -Fq "test_message_addressed_to_automation_ignores_display_name_match" "$ROOT_DIR/tests/test_rules.py" ||
  ! grep -Fq "test_message_addressed_to_automation_matches_address_case_insensitively" "$ROOT_DIR/tests/test_rules.py" ||
  ! grep -Fq "test_valid_email_rejects_message_not_addressed_to_automation" "$ROOT_DIR/tests/test_rules.py" ||
  ! grep -Fq "AUTOMATION_FROM_EMAIL" "$ROOT_DIR/mail/rules.py" ||
  ! grep -Fq "def configured_from_email" "$ROOT_DIR/mail/rules.py" ||
  ! grep -Fq "if not from_email" "$ROOT_DIR/mail/rules.py" ||
  ! grep -Fq "test_configured_from_email_rejects_invalid_address" "$ROOT_DIR/tests/test_rules.py" ||
  ! grep -Fq "test_send_email_rejects_invalid_from_email_before_importing_sender" "$ROOT_DIR/tests/test_rules.py" ||
  ! grep -Fq "test_valid_email_rejects_invalid_from_email" "$ROOT_DIR/tests/test_rules.py" ||
  ! grep -Fq "AUTOMATION_APPROVED_SENDERS" "$ROOT_DIR/mail/rules.py" ||
  ! grep -Fq "CONFIG_EMAIL_RE" "$ROOT_DIR/mail/rules.py" ||
  ! grep -Fq "def valid_config_email" "$ROOT_DIR/mail/rules.py" ||
  ! grep -Fq "test_configured_from_users_ignores_invalid_addresses" "$ROOT_DIR/tests/test_rules.py" ||
  ! grep -Fq "test_configured_to_email_rejects_invalid_address" "$ROOT_DIR/tests/test_rules.py"; then
  printf '%s\n' "Automation mailbox settings must come from environment-backed configuration." >&2
  exit 1
fi

if ! grep -Fq "status: completed" "$CONFIGURED_USER_ID_PLAN" ||
  ! grep -Fq "Python 3.12.8 and Python 3.14.0" "$CONFIGURED_USER_ID_PLAN" ||
  ! grep -Fq "hostile source mutations were rejected" "$CONFIGURED_USER_ID_PLAN" ||
  ! grep -Fq "No Gmail, OAuth, or App Engine runtime calls" "$CONFIGURED_USER_ID_PLAN"; then
  printf '%s\n' "Configured automation user identity plan must record truthful completed verification." >&2
  exit 1
fi

if ! grep -Fq "status: completed" "$CONFIGURED_USER_ID_WHITESPACE_PLAN" ||
  ! grep -Fq "Python 3.12.8 and Python 3.14.0" "$CONFIGURED_USER_ID_WHITESPACE_PLAN" ||
  ! grep -Fq "Eight hostile mutations were rejected" "$CONFIGURED_USER_ID_WHITESPACE_PLAN" ||
  ! grep -Fq "No Gmail, OAuth, or App Engine runtime calls" "$CONFIGURED_USER_ID_WHITESPACE_PLAN"; then
  printf '%s\n' "Configured user ID whitespace plan must record completed local verification." >&2
  exit 1
fi

if grep -Fq "people[0] == my_email" "$ROOT_DIR/mail/list.py" ||
  grep -Fq "people[1] == my_email" "$ROOT_DIR/mail/list.py"; then
  printf '%s\n' "Automation recipient checks must compare normalized recipient addresses, not display names." >&2
  exit 1
fi

for recipient_metadata_contract in \
  "if not isinstance(msg, dict):" \
  "if not isinstance(recipients, (list, tuple)):" \
  "except AttributeError:" \
  "test_message_addressed_to_automation_rejects_malformed_containers" \
  "test_message_addressed_to_automation_skips_malformed_addresses" \
  "test_valid_email_rejects_malformed_recipient_metadata_without_side_effects"; do
  if ! grep -Fq "$recipient_metadata_contract" "$ROOT_DIR/mail/rules.py" "$ROOT_DIR/tests/test_rules.py"; then
    printf '%s\n' "Recipient metadata contract is missing: $recipient_metadata_contract" >&2
    exit 1
  fi
done

if ! grep -Fq "status: completed" "$RECIPIENT_METADATA_PLAN" ||
  ! grep -Fq "make check" "$RECIPIENT_METADATA_PLAN" ||
  ! grep -Fq "hostile mutations were rejected" "$RECIPIENT_METADATA_PLAN"; then
  printf '%s\n' "Recipient metadata plan must record completed verification." >&2
  exit 1
fi

for document in "$ROOT_DIR/README.md" "$ROOT_DIR/SECURITY.md" "$ROOT_DIR/VISION.md" "$ROOT_DIR/CHANGES.md" "$ROOT_DIR/AGENTS.md"; do
  if ! grep -Fq "malformed recipient metadata" "$document"; then
    printf '%s\n' "$document must document malformed recipient metadata rejection." >&2
    exit 1
  fi
done

printf '%s\n' "Email Automator maintenance baseline checks passed."
