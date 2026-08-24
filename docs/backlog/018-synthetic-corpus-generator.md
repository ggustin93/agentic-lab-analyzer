# 018: Synthetic lab-report corpus generator

- Severity: Medium · Priority: Should · Labels: responsible-ai, testing,
  data-quality

## Context

Every measurement this project wants to make: prompt evaluation (011),
quality-gate calibration (015), the local-OCR bake-off (017), noise
robustness (research notes §4); it needs labeled documents, and real lab
reports are GDPR Article 9 data this project must not collect. Generation
solves both problems at once: a *generated* document's expected extraction
is known **by construction**, so ground truth is perfect, free, and
committable.

## Expected behavior

A seeded, versioned generator (`backend/evals/generator/`) that produces
(document, expected-extraction) pairs in two modalities from the same
truth: native PDF, and a degraded scan/photo variant.

## Business rules

- 2–3 fictitious laboratory templates (distinct column orders, ↗/↘
  conventions, DD/MM dates, French units), *inspired by* Belgian layouts,
  imitating no real brand, name, or logo.
- Content sampled from the repository's own marker catalog
  (`src/app/data/lab-markers.data.ts` reference ranges), with in/out-of-
  range proportions controlled per run: the expected `is_out_of_range`
  flags fall out of the sampling.
- Rendering: HTML/CSS → PDF (e.g. WeasyPrint); degraded variant via
  rasterization + parameterized noise (slight rotation, blur, JPEG
  artifacts, contrast), the noise level is an input, enabling degradation
  curves.
- Patient identities via Faker, deliberately implausible; fixed seed and a
  generator version string embedded in each corpus manifest, so any clone
  reproduces the exact corpus.
- Corpus manifest declares the dev/held-out split **by template** (at least
  one template reserved for held-out; see 011 for why splitting by
  document leaks layout knowledge).

## Edge cases to generate on purpose

Multi-page tables; historical-results columns to be ignored; malformed
reference ranges (`<6 - 6.0`); qualitative results; missing units; a
partial-text-layer PDF (some pages native, some rasterized) for the
modality router (017).

## Validation intent (acceptance criteria)

- Given a seed and generator version, then two runs produce byte-identical
  manifests (rendering may differ at pixel level; the extraction truth may
  not).
- Given a generated corpus, then every document has a paired
  `expected.json` conforming to `HealthDataExtraction`, and a sanity test
  round-trips one clean native document through the extraction prompt.
- Given the noise parameter, then the scan variant is produced from the
  same truth file: one truth, two modalities.

## Out of scope (deliberate)

Photorealistic scan simulation; handwriting; generating *insight* prose
ground truth (011 scores extraction, not prose); any real document.

## Assumptions / open questions

Whether the marker catalog needs enriching (aliases, French marker names)
before sampling from it; how many documents per template before returns
diminish (start ~10, observe).
