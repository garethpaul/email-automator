# Email Message ID Cache Guard

Status: Completed
Date: 2026-06-09

## Goal

Prevent malformed inbound Gmail message IDs from becoming duplicate-send
memcache keys or triggering automated replies.

## Changes

- Added a message ID allow-list and length bound before cache-key construction.
- Normalized message IDs before duplicate-send checks in `valid_email`.
- Added offline tests for malformed and overlong message IDs.
- Extended the source baseline, README, security notes, changelog, and vision
  with the message ID cache-key contract.

## Verification

- `python3 -m unittest discover -s tests -p "test*.py"`
- `scripts/check-baseline.sh`
- `make check`
- `git diff --check`
