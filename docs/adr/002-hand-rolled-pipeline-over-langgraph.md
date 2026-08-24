# ADR-002 — Hand-rolled agent pipeline over LangGraph/PydanticAI

- Status: Accepted (with explicit migration triggers)
- Date: 2025-07 (recorded retroactively)

## Context

The backend chains three AI steps: OCR → structured extraction → insight
generation, with per-stage progress tracking. Orchestration frameworks exist
that provide this out of the box: LangGraph (stateful graph, checkpointing,
per-node retry policies) and PydanticAI (typed agents with validation-driven
retries).

## Options considered

1. **LangGraph** — checkpointing would eliminate the "stuck document" class
   of bugs (a crashed worker resumes from the last saved state) and replace
   the manual retry endpoint. Cost: a significant dependency and its
   abstractions for what is today a 3-node linear chain.
2. **PydanticAI** — typed outputs with automatic retry-on-validation-error;
   would replace the hand-rolled JSON parsing. Same trade-off at lower cost.
3. **Plain Python pipeline** — three explicit stages in
   `services/processing_pipeline.py`, typed against the Protocols in
   `agents/base.py`.

## Decision

Plain Python for the proof-of-concept: the pipeline is linear, the stages are
few, and keeping the orchestration visible in ~200 lines is worth more
(including as a portfolio artifact) than the framework features we are not
yet using.

## Consequences — and migration triggers

We knowingly accept: fire-and-forget `asyncio.create_task` (in-flight work is
lost on restart, mitigated by the retry endpoint and stuck-document
detection), and no per-node retry policies.

Re-evaluate this decision when any of these happens:

- the pipeline gains branching or human-in-the-loop steps;
- "stuck document" recovery becomes a real operational burden (checkpointing
  then pays for itself);
- a second model provider per stage is needed (PydanticAI's model abstraction
  becomes the cheaper path).
