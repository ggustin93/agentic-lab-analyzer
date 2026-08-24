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

## Data strategy (test vs. validation)

Three distinct datasets, kept distinct on purpose:

1. **Synthetic generated corpus (the workhorse).** A seeded generator
   (`backend/evals/generator/`) renders fictitious lab reports from 2–3
   invented laboratory templates (different column orders, ↗/↘ conventions,
   DD/MM dates, French units — inspired by real Belgian layouts without
   imitating any real brand or logo), filled by sampling markers and
   reference ranges from the repository's own marker catalog and drawing
   values in/out of range in controlled proportions. Because the documents
   are *generated*, the expected extraction is known **by construction** —
   no manual annotation, perfect ground truth, committable to the repo.
   Rendering: HTML/CSS → native PDF; a degraded variant (rasterization +
   rotation, blur, JPEG artifacts) produces the scan/photo modality, so the
   same ground truth serves both routes of the OCR modality router (017)
   and the noise-robustness curves of research notes §4. Patient identities
   via Faker, deliberately implausible.
2. **Dev vs. held-out split — by template, not by document.** Prompts are
   iterated against the dev set; the held-out set (including at least one
   template never seen during prompt iteration) is touched only to produce
   the final score and to calibrate the quality-gate thresholds (015).
   Splitting by document instead of template leaks layout knowledge and
   overstates generalization.
3. **A small real anonymized set (the reality check).** Synthetic data
   validates the mechanics, not the realism — a generator only tests what
   its author thought to generate. A handful of real reports, irreversibly
   anonymized (identity header masked, PDF metadata stripped), manually
   annotated, kept strictly local and git-ignored, provides the honest
   "does this survive contact with reality" number. Public table-extraction
   datasets (PubTabNet, FinTabNet) exercise OCR structure but are not lab
   reports and do not substitute.

Honest sizes to start: ~20–30 dev / ~20 held-out / 5–10 real — enough to
catch gross regressions, too few for fine-grained claims; the evaluation
report states this limitation.

## Business rules

- Committed fixtures are fully synthetic; real anonymized documents never
  enter the repository (see `docs/ai-workflow.md` guardrails). The
  generator is seeded and versioned so the corpus is reproducible.
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
