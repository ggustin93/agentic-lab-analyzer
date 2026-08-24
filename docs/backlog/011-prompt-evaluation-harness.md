# 011 — Prompt evaluation harness

- Severity: Medium · Priority: Could · Labels: responsible-ai, testing

## Context

Two non-trivial prompts (extraction, insights) evolve with no measurement:
a prompt edit that degrades extraction quality would today be invisible.
A modest, honest harness is more valuable than none; research-grade
evaluation directions are discussed separately in
`docs/research-notes.md`.

## Expected behavior

A small fixture set of synthetic/anonymized OCR outputs with expected
extractions, and a pytest-marked evaluation that scores extraction quality
and fails under a threshold.

## Business rules

- Fixtures are fully synthetic or irreversibly anonymized — no real
  documents (see `docs/ai-workflow.md` guardrails).
- Metrics: per-marker precision/recall (name matching), exact-match on
  value/unit/range, date accuracy.
- Runs on demand and on prompt changes (marker `@pytest.mark.evals`,
  excluded from the default CI job to keep it hermetic and free of API
  keys); results recorded alongside the prompt version (010).

## Validation intent (acceptance criteria)

- Given the fixture set and the current prompt, then the harness produces a
  scored report and passes at the agreed threshold (proposal: ≥ 0.95
  precision and recall on marker extraction — to calibrate on the first run
  rather than asserted in advance).
- Given a deliberately degraded prompt, then the harness fails.

## Out of scope (deliberate)

LLM-as-judge scoring of the insight prose; statistical significance across
runs (sample size is too small at PoC scale to claim it).

## Assumptions / open questions

Fixture count: 5–10 to start — enough to catch gross regressions, too few
for fine-grained claims; this limitation should be stated in the report the
harness produces.
