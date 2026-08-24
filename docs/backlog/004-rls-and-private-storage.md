# 004 — Row Level Security & private storage

- Severity: Critical · Priority: Could (prerequisite to any deployment) ·
  Labels: security, database

## Context

No RLS policy exists in `supabase/migrations/`, and files live in a public
bucket with permanent URLs (`storage_manager.py` uses `get_public_url`).
On Supabase, tables without RLS are reachable through the public REST
endpoint by anyone holding the anon key; ADR-005 records why RLS is
non-optional with this platform choice.

## Expected behavior

Defense in depth independent of the API layer: RLS on every table and on
`storage.objects`; a private bucket; short-lived signed URLs generated
server-side on demand.

## Business rules

- RLS policies: a row is visible/mutable only by its `user_id` (depends on
  003 for the identity).
- Bucket private; document access via `create_signed_url` with TTL ≤ 15 min.
- The service-role key remains server-side only.

## Edge cases

The frontend PDF viewer consumes the URL directly — it must request a fresh
signed URL rather than persist one; retry pipeline reads `public_url` from
the database and must switch to signed access.

## Validation intent (acceptance criteria)

- Given the anon key used directly against Supabase REST, then zero rows
  are readable on all three tables.
- Given a stored document URL older than the TTL, then access returns 403.
- Given migration + rollback scripts, then both apply cleanly (repo
  convention: every migration ships its rollback).

## Out of scope (deliberate)

Encryption at rest beyond what Supabase provides; audit logging of access.

## Assumptions / open questions

Signed-URL TTL of 15 minutes balances viewer sessions against exposure;
to validate against actual reading time.
