# ADR-005 — Supabase (BaaS) over self-managed Postgres + object storage

- Status: Accepted
- Date: 2025-07 (recorded retroactively)

## Context

The project needs a Postgres database, binary file storage, and versioned
schema migrations — with zero ops budget (solo, proof-of-concept).

## Options considered

1. **Self-managed Postgres + S3-compatible storage** — full control, real ops
   burden (backups, TLS, users), nothing reusable for a PoC portfolio.
2. **Supabase** — managed Postgres with a storage API, SQL migrations kept in
   the repo (`supabase/migrations/`, including rollback scripts), generous
   free tier.

## Decision

Supabase, with migrations under version control as the single source of truth
for the schema.

## Consequences — the one that matters

Choosing Supabase makes **Row Level Security non-optional**: tables without
RLS are reachable through Supabase's public REST endpoint by anyone holding
the anon key. The current schema has no RLS policies and the backend uses the
service-role key — acceptable only while the project runs locally with demo
data, and documented as the top item of the security backlog (see README
"Known limitations"). Enabling RLS + per-user policies + a private storage
bucket with signed URLs is the prerequisite to any deployment.
