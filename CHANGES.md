# Changes

## 2026-06-08

- Made reply-rule helpers importable without App Engine/Gmail dependencies.
- Added deterministic offline tests for keyword replies, unknown replies,
  approved sender checks, local cache checks, and duplicate-send prevention.
- Removed emergency-service wording from unknown automated replies.
- Added a baseline verification script for local rule changes.
