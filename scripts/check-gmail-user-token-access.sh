#!/usr/bin/env bash
set -euo pipefail

for required in \
  "login: required" \
  "login: admin" \
  "secure: always" \
  "debug=False" \
  "current_user_id" \
  "cron_user_id" \
  "X-AppEngine-Cron"
do
  if ! rg -q "$required" app.yaml main.py mail/auth.py mail/check.py mail/list.py; then
    echo "missing Gmail token access control: $required" >&2
    exit 1
  fi
done

if rg -n 'request\.get\("userId"\)' mail/check.py mail/list.py | rg -v 'cron_user_id'; then
  echo "interactive Gmail handlers must not trust query-string userId" >&2
  exit 1
fi

if ! awk '
  /url: \/mail\/me/ { mail_me = NR }
  /login: admin/ && mail_me && !admin { admin = NR }
  /url: \/mail\/\.\*/ { mail_star = NR }
  END { exit !(mail_me && admin && mail_star && mail_me < admin && admin < mail_star) }
' app.yaml; then
  echo "/mail/me must be admin-gated before the broader /mail/.* handler" >&2
  exit 1
fi

echo "Gmail user-token access checks are present"
