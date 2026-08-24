# 002 — Bounded SSE streams

- Severity: High · Priority: Should · Labels: security, backend, reliability · Status: Done

## Context

`GET /api/v1/documents/{id}/stream` (`main.py`) loops forever for an unknown
`document_id`: no existence check, no lifetime bound, no disconnect
detection — each such stream polls the database every 2 s indefinitely.

## Expected behavior

A stream exists only for a real document, ends deterministically, and stops
consuming resources as soon as the client goes away.

## Business rules

- Unknown id → `404` immediately, no stream.
- Terminal states (`complete`, `error`) close the stream (already the case).
- A stream still open after N minutes (proposal: 15) closes with a final
  `timeout` event.

## Edge cases

Client disconnects mid-stream; document deleted while streamed; document
stuck in `processing` forever.

## Validation intent (acceptance criteria)

- Given a random UUID, when the stream endpoint is called, then `404` with
  no polling loop started.
- Given a connected client that disconnects, then the generator stops within
  one polling interval (verify via `request.is_disconnected()`).
- Given a document stuck in `processing`, then the stream closes with a
  `timeout` event after the bound.

## Out of scope (deliberate)

Replacing polling with push-based updates (see ADR-004's upgrade path);
authentication of the stream (belongs to 003).

## Assumptions / open questions

The 15-minute bound assumes worst-case pipeline latency well under that;
to revisit if OCR latency observations say otherwise.
