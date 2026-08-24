# 006 — Generic client-facing error messages

- Severity: Medium · Priority: Should · Labels: security, backend

## Context

All endpoints return `detail=f"...: {str(e)}"`, and raw exception text is
stored in `documents.error_message` then shown in the UI. Exception strings
can carry infrastructure details (hosts, buckets, table names, library
internals).

## Expected behavior

Clients receive stable, generic messages; the full exception (with stack
trace) goes to server logs only, correlated by document id.

## Business rules

- A small catalog of user-facing messages (upload failed, processing failed,
  not found, retry later) — no interpolated exception text.
- `error_message` stored in the database follows the same catalog.

## Validation intent (acceptance criteria)

- Given a storage failure with an internal URL in the exception, when the
  client receives the response, then the body contains no URL, host, bucket
  or table name — and the server log contains the full trace.

## Out of scope (deliberate)

Structured error codes for programmatic clients; i18n of messages.

## Assumptions / open questions

None significant; this is mostly mechanical.
