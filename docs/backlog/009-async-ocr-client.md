# 009: Non-blocking OCR HTTP client

- Severity: High · Priority: Should · Labels: reliability, backend · Status: Done

## Context

`mistral_ocr_service.py` uses synchronous `requests` (file download up to
30 s, OCR call up to 120 s) invoked from the async pipeline: while it runs,
the whole FastAPI event loop is blocked: no request is served, SSE included.
The two other agents already use `httpx.AsyncClient`, which makes the
inconsistency easy to miss and easy to fix.

## Expected behavior

No blocking I/O on the event loop; the API stays responsive during OCR.

## Validation intent (acceptance criteria)

- Given a document being OCR-processed (mock with a 5 s async delay), when
  `GET /` is called concurrently, then it responds in < 100 ms.
- The `httpx` client is closed on application shutdown (FastAPI lifespan),
  which also fixes the never-closed clients of the two other agents.

## Out of scope (deliberate)

Retry/backoff policies on OCR calls (worth a follow-up once latency data
exists).

## Assumptions / open questions

None; mechanical change with an existing in-repo pattern to follow.
