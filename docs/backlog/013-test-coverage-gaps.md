# 013 — Close targeted test coverage gaps

- Severity: Medium · Priority: Should · Labels: testing

## Context

The suites that exist are genuine, but coverage is uneven and the highest-
value gaps are precisely the clinically relevant paths:
`reference-range-parser.service.ts` (untested), `document.store.ts`,
`document-api.service.ts`, and all SSE handling. Coverage is also never
measured in CI, so claims about it are unverifiable. The 80/20 disclaimer in
README section 5 stays; this issue narrows the 20 that matters.

## Expected behavior

The clinically-relevant units are tested, SSE handling has at least one
automated test, and CI measures coverage so the number is a fact rather
than a statement.

## Business rules

- Priority order: range parser (table-driven cases incl. malformed ranges)
  → store (mutations + computed selectors) → API service → SSE message
  handling (mock `EventSource`).
- CI runs `--code-coverage` and enforces a modest, honest threshold
  (proposal: start at the measured baseline, ratchet up, rather than assert
  an aspirational number).
- Remove the `try/catch` around `httpMock.verify()` in
  `document-analysis.service.spec.ts` that currently downgrades leak
  failures to warnings.

## Validation intent (acceptance criteria)

- Given the new parser suite, then boundary values, open ranges (`< x`,
  `> x`) and malformed inputs each have explicit cases.
- Given a mocked `EventSource` emitting a terminal event, then the store is
  updated and the per-document connection is closed (regression test for
  the concurrent-uploads fix).
- Given CI on a PR, then a coverage summary is produced and the threshold
  is enforced.

## Out of scope (deliberate)

E2E expansion (tracked separately if it earns its cost); mutation testing.

## Assumptions / open questions

Karma remains for now; the Jest migration stays a roadmap item and would not
change these tests' substance.
