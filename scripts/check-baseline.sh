#!/usr/bin/env sh
set -eu

ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
CHECK_PLAN="$ROOT_DIR/docs/plans/2026-06-08-email-check-wrapper.md"

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
  "Makefile" \
  "VISION.md" \
  "CHANGES.md" \
  "app.yaml" \
  "cron.yaml" \
  "main.py" \
  "mail/auth.py" \
  "mail/check.py" \
  "mail/list.py" \
  "mail/rules.py" \
  "tests/test_rules.py" \
  "docs/plans/2026-06-08-email-check-wrapper.md" \
  "docs/plans/2026-06-08-email-rule-baseline.md" \
  "docs/plans/2026-06-08-app-engine-safety-baseline.md"; do
  require_file "$path"
done

python3 -m py_compile "$ROOT_DIR/mail/rules.py" "$ROOT_DIR/tests/test_rules.py"
python3 -m unittest discover -s "$ROOT_DIR/tests" -p "test*.py"

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
  ! grep -Fq "status: completed" "$CHECK_PLAN"; then
  printf '%s\n' "Plans must be marked completed." >&2
  exit 1
fi

if ! grep -Fq "scripts/check-baseline.sh" "$ROOT_DIR/README.md" ||
  ! grep -Fq "make check" "$ROOT_DIR/README.md" ||
  ! grep -Fq "offline" "$ROOT_DIR/README.md" ||
  ! grep -Fq "OAuth" "$ROOT_DIR/README.md" ||
  ! grep -Fq "Gmail" "$ROOT_DIR/README.md"; then
  printf '%s\n' "README must document make check, offline tests, and Gmail/OAuth boundaries." >&2
  exit 1
fi

if ! grep -Fq "check: verify" "$ROOT_DIR/Makefile"; then
  printf '%s\n' "Makefile must expose make check as the repository verification wrapper." >&2
  exit 1
fi

if grep -R "dial 911" "$ROOT_DIR/mail" "$ROOT_DIR/tests" >/dev/null; then
  printf '%s\n' "Automated fallback replies must not mention dialing 911." >&2
  exit 1
fi

if ! grep -Fq "_LocalMemcache" "$ROOT_DIR/mail/rules.py" ||
  ! grep -Fq "cache_key" "$ROOT_DIR/mail/rules.py" ||
  ! grep -Fq "test_valid_email_sends_approved_message_once" "$ROOT_DIR/tests/test_rules.py" ||
  ! grep -Fq "test_configured_from_users_reads_environment" "$ROOT_DIR/tests/test_rules.py"; then
  printf '%s\n' "Offline rules baseline must keep local cache and duplicate-send coverage." >&2
  exit 1
fi

if ! grep -Fq "def tokenize_email" "$ROOT_DIR/mail/rules.py" ||
  ! grep -Fq "Gareth," "$ROOT_DIR/tests/test_rules.py"; then
  printf '%s\n' "Rule tests must cover punctuation-tolerant keyword matching." >&2
  exit 1
fi

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
  ! grep -Fq "AUTOMATION_FROM_EMAIL" "$ROOT_DIR/mail/rules.py" ||
  ! grep -Fq "AUTOMATION_APPROVED_SENDERS" "$ROOT_DIR/mail/rules.py"; then
  printf '%s\n' "Automation mailbox settings must come from environment-backed configuration." >&2
  exit 1
fi

printf '%s\n' "Email Automator maintenance baseline checks passed."
