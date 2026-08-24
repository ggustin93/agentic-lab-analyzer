# 010: Analysis provenance metadata

- Severity: Medium · Priority: Should · Labels: responsible-ai,
  data-quality, backend

## Context

Stored analyses record nothing about how they were produced: `mistral-large-
latest` is a moving alias, prompts live inline in code, token usage is
discarded. "Which configuration produced this result?" cannot be answered:
a basic requirement in any regulated-adjacent domain, and a prerequisite for
meaningful prompt evaluation (011).

## Expected behavior

Every analysis persists its provenance: model identifiers (pinned, dated
versions rather than aliases), a prompt version, timestamps per stage, and
token counts.

## Business rules

- Prompts move to versioned files (`backend/prompts/`) with an explicit
  version string included in provenance.
- A JSONB `provenance` column on `analysis_results` (migration + rollback,
  per repo convention).

## Validation intent (acceptance criteria)

- Given a completed analysis, then its record contains model ids, prompt
  version, and token counts for both LLM stages.
- Given a prompt file change without a version bump, then a unit test fails
  (checksum pinned to version).

## Out of scope (deliberate)

Full tracing/observability platform (Langfuse, OpenTelemetry), noted as a
roadmap item; cost dashboards.

## Assumptions / open questions

Whether provenance should also capture the OCR model version: yes if the
API exposes it reliably.
