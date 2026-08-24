# ADR-004: SSE over WebSockets or Supabase Realtime for progress updates

- Status: Accepted
- Date: 2025-07 (recorded retroactively)

## Context

The dashboard must reflect document processing progress live (four stages,
percentage, terminal states). Communication is strictly server → client.

## Options considered

1. **WebSockets**: bidirectional, but we have no client → server traffic
   after upload, and WS adds connection-upgrade and reconnection complexity.
2. **Supabase Realtime**: DB change events pushed to the client; elegant,
   but couples the frontend directly to the database schema and to Supabase.
3. **Server-Sent Events**: one-directional HTTP streaming, native
   `EventSource` in the browser with automatic reconnection, trivially
   proxied.

## Decision

SSE (`GET /api/v1/documents/{id}/stream`), one stream per in-flight document.

## Consequences

- The current implementation polls the database every 2 s inside the stream;
  simple, but it means N clients × 1 query/2 s. Acceptable at PoC scale;
  a push-based bridge (or option 2) is the upgrade path.
- Known hardening backlog: the endpoint must 404 on unknown ids and bound the
  stream lifetime (see the security backlog in the README).
