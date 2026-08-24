# ADR-003 — Extraction and insights as two separate LLM calls

- Status: Accepted
- Date: 2025-07 (recorded retroactively)

## Context

After OCR, the system must (a) turn markdown tables into structured health
markers and (b) produce a human-readable clinical summary. One large prompt
could do both in a single call, at half the latency and cost.

## Options considered

1. **Single call** — one prompt returns markers + summary together. Cheaper,
   but a failure in either half invalidates both, the prompt mixes two very
   different skills (table parsing vs. clinical prose), and the structured
   half cannot be validated independently before the prose half consumes it.
2. **Two calls** — `ExtractionAgent` (deterministic-leaning, table-focused)
   then `InsightAgent` (prose, fed only the *validated* structured data).

## Decision

Two calls. The extraction output is validated (Pydantic) before insight
generation ever sees it, so the prose stage works from clean structured data
rather than from raw OCR — which also narrows the prompt-injection surface of
the second stage to fields we control.

## Consequences

- Each stage is independently testable and replaceable (see `agents/base.py`).
- Progress reporting maps naturally to stages (30% / 50%).
- Double latency and token cost per document — acceptable at PoC volume;
  revisit with batching if volume grows.
