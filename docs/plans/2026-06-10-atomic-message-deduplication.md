# Atomic Email Message Deduplication

## Status: Completed

## Goal

Prevent concurrent workers from sending duplicate automated replies for the
same inbound Gmail message ID.

## Changes

- Use memcache `add` as an atomic reservation before calling the outbound Gmail
  sender instead of recording the ID only after the side effect.
- Stop a concurrent attempt before sending when the normalized message ID is
  already reserved.
- Release the reservation when the sender returns false or raises, preserving a
  safe retry path after transient failures.
- Extend the offline memcache double with delete support.
- Add a re-entrant test that reproduces the old check-then-send race, plus false
  return and exception tests that prove failed reservations are released.
- Preserve the ordering and failure contracts in the maintenance baseline,
  README, security policy, vision, and changelog.

## Verification

- `make check`
- `python3 -m unittest discover -s tests -p "test*.py"`
- `git diff --check`
- A mutation restoring the old post-send reservation must fail the re-entrant
  concurrency regression.
- Mutations removing each release path must fail the corresponding retry test.
