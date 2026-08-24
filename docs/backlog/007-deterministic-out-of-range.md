# 007 — Deterministic out-of-range flag

- Severity: High · Priority: Should · Labels: responsible-ai, data-quality,
  backend

## Context

`is_out_of_range` is currently asserted by the extraction model (the prompt
even delegates the comparison), with a silent `False` default in
`health_models.py` when the field is missing. For a clinically meaningful
flag, this places too much trust in generation: the model should extract,
reviewed code should judge.

## Expected behavior

The stored flag is computed by deterministic, unit-tested code comparing the
extracted value against the parsed reference range; the model's own flag is
at most a hint, never the source of truth.

## Business rules

- A parser handles the common range shapes (`a - b`, `< b`, `> a`, `≤`, `≥`)
  — logic comparable to the frontend's `reference-range-parser.service.ts`,
  implemented and tested backend-side where the data is persisted.
- Unparseable range or non-numeric value → status `indeterminate`, displayed
  as such; never a silent `false`/normal.
- The Pydantic default changes accordingly (`None` = indeterminate rather
  than `False` = normal).

## Edge cases

Trend arrows and thousands separators in values; ranges with units embedded;
qualitative results ("negative", "positive"); multiple sub-ranges.

## Validation intent (acceptance criteria)

- Given value `1.4` and range `0.70 - 1.30`, then the stored flag is `true`
  regardless of what the model returned.
- Given a range the parser cannot interpret, then the marker is
  `indeterminate` and rendered as such in the UI.
- Property (table-driven test): for every fixture row, final flag =
  f(value, range), independent of the model's field.

## Out of scope (deliberate)

Age/sex-specific reference ranges from an authoritative source — a research
direction, see `docs/research-notes.md`.

## Assumptions / open questions

Whether to unify the parser (shared spec, two implementations, one fixture
set) or expose the backend's verdict to the frontend and delete the
duplicate — leaning toward the latter.
