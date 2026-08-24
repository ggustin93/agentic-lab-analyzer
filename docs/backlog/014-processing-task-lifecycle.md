# 014 — Processing task lifecycle

- Severity: Medium · Priority: Could · Labels: reliability, backend

## Context

The pipeline is launched with a fire-and-forget `asyncio.create_task` whose
reference is not retained: tasks are garbage-collectable mid-flight, and a
process restart silently loses in-flight work — the "stuck document"
symptom that the retry endpoint and the dashboard poll then compensate for.
ADR-002 records why a full workflow engine is not (yet) the answer.

## Expected behavior

In-flight work is tracked, and interrupted work is detected and recoverable
without user intervention.

## Business rules

- Task references retained in a set (removal on completion) — the minimal
  correctness fix.
- On startup, documents left in `processing` beyond a threshold are marked
  `error` with a "interrupted" message, making the failure explicit instead
  of silent.

## Validation intent (acceptance criteria)

- Given a pipeline task in flight, then a strong reference to it exists
  until completion (no GC-collectable task).
- Given a process restart with a document mid-processing, then within one
  startup pass the document is in a terminal, retryable state — not stuck.

## Out of scope (deliberate)

A real queue or checkpointed workflow — explicitly deferred with migration
triggers in ADR-002.

## Assumptions / open questions

Threshold for "interrupted" detection; reuse the 5-minute stuck heuristic
already used by the frontend for consistency.
