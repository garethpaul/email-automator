#!/usr/bin/env python3
import pathlib
import sys


def check_handler(path):
    source = pathlib.Path(path).read_text(encoding="utf-8")
    start_marker = "def request_user_id(handler):"
    end_marker = "\nclass "
    if source.count(start_marker) != 1:
        raise SystemExit(f"{path}: request_user_id boundary must remain unique.")

    handler = source.split(start_marker, 1)[1].split(end_marker, 1)[0]
    configured = 'userId = os.environ.get("AUTOMATION_USER_ID")'
    configured_lookup = 'os.environ.get("AUTOMATION_USER_ID")'
    missing = "if not userId:"
    error = "handler.error(400)"
    absent = "return None"
    present = "return userId"

    for contract in (configured, missing, error, absent, present):
        if handler.count(contract) != 1:
            raise SystemExit(
                f"{path}: configured automation identity contract must contain "
                f"exactly one {contract!r}."
            )

    if handler.count(configured_lookup) != 1:
        raise SystemExit(f"{path}: automation identity must be read exactly once.")

    if "handler.request.get" in handler or '"userId"' in handler or "'userId'" in handler:
        raise SystemExit(f"{path}: request input must not select the Gmail credential key.")

    positions = [handler.index(value) for value in (configured, missing, error, absent, present)]
    if positions != sorted(positions):
        raise SystemExit(f"{path}: configured identity failure must precede success.")


if len(sys.argv) != 3:
    raise SystemExit("usage: check-configured-user-id.py MAIL_LIST MAIL_CHECK")

for source_path in sys.argv[1:]:
    check_handler(source_path)
