# 005: Rate limiting & processing locks

- Severity: High · Priority: Should · Labels: security, backend, cost

## Context

Upload and retry endpoints trigger paid OCR/LLM calls without any
throttling, and `retry` has no guard against concurrent re-processing of the
same document. Until 003 lands, both are callable anonymously: a direct
cost-amplification vector.

## Expected behavior

Request rates are bounded per client, and a document is processed by at most
one pipeline run at a time.

## Business rules

- Rate limits (proposal, to tune): 10 uploads/hour and 20 retries/hour per
  client identity (IP until 003, user afterwards).
- A retry on a document already being processed is a no-op with an explicit
  `409` response.

## Validation intent (acceptance criteria)

- Given the limit is reached, then `429` with a `Retry-After` header and no
  pipeline invocation.
- Given two concurrent retries on one document, then exactly one pipeline
  run starts.

## Out of scope (deliberate)

Global spend budgets and billing alerts (operational, not code); queue-based
back-pressure (see 014).

## Assumptions / open questions

`slowapi` is the candidate library; verify its behavior behind a reverse
proxy (client IP extraction) before relying on IP-based identity.
