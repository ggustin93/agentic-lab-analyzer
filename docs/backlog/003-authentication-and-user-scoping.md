# 003 — Authentication & per-user scoping

- Severity: Critical · Priority: Could (prerequisite to any deployment) ·
  Labels: security, backend, frontend

## Context

No endpoint requires authentication; `GET /api/v1/documents` returns every
document in the system. The schema has a `user_id` column that is never
populated or filtered on. Acceptable only while the project runs locally
with synthetic data — stated openly in README section 8.

## Expected behavior

Every request is authenticated (Supabase Auth JWT verified by a FastAPI
dependency) and every query is scoped to the authenticated user.

## Business rules

- No anonymous access to any document endpoint.
- `user_id` is set at upload from the verified token, never from the client
  payload.
- Cross-user access to a document id returns `404` (not `403`), to avoid
  confirming existence.

## Edge cases

Expired/malformed token; token for a deleted user; documents created before
this change (migration: assign or purge).

## Validation intent (acceptance criteria)

- Given no token, then `401` on all document endpoints.
- Given user A's token, when listing, then only A's documents.
- Given A's token and B's document id, then `404`.

## Out of scope (deliberate)

Roles/permissions beyond single-user ownership; organization sharing; MFA.

## Assumptions / open questions

Whether the demo deployment keeps a public "sandbox" mode (auto-created
anonymous session) or requires sign-in — a product decision to make before
implementation.
