# Research notes — open questions for AI-assisted lab report analysis

These notes collect directions we consider promising for improving the AI
core of this proof-of-concept, written from a research perspective rather
than as a feature list. None of them are implemented; several may prove
unnecessary at this scale. They are recorded because knowing *what one has
not validated* is part of building responsibly with LLMs — this system has,
at present, no measured claim to extraction accuracy, robustness, or
calibration, and the notes below sketch how such claims could be earned.

## 1. Evaluation methodology before optimization

Any improvement to prompts or models is currently unmeasurable (see backlog
011 for the minimal harness). A more rigorous treatment would require:

- **A gold corpus** of lab reports with reference annotations. Real
  documents raise privacy questions this project should not take on; a
  *synthetic report generator* (templates parameterized by laboratory
  format, language, units, and injected OCR-like noise) offers controlled
  difficulty and unlimited labeled data, at the cost of realism — a
  limitation to state, not hide.
- **Field-level metrics**: per-marker precision/recall for detection,
  exact-match and normalized-match for value/unit/range, and a separate
  date-accuracy figure (day/month inversion being the failure mode we have
  already met in the wild).
- **Annotation quality**: even with two annotators on a small real subset,
  reporting inter-annotator agreement would bound what "ground truth"
  means for ambiguous cells (merged columns, handwritten corrections).

## 2. Reliability of extraction

- **Constrained decoding**: schema-constrained outputs (backlog 008) remove
  a syntactic failure class; they do not address semantic errors, so they
  are a floor, not a solution.
- **Self-consistency**: sampling the extraction *n* times and keeping
  field-level majority answers is a well-known variance reducer; whether it
  pays for its n× cost at this task's error profile is an empirical
  question worth a small experiment before adopting.
- **Verification passes**: a second, cheaper model checking unit/value
  plausibility (e.g. a hemoglobin of 145 g/dL is a unit error, not a
  finding) may catch the errors the extractor cannot see in itself.
  Deterministic plausibility bounds per marker are the humbler and more
  auditable starting point.
- **Abstention as a first-class outcome**: the system already prefers
  `null` over a guessed date; extending this policy (selective prediction)
  to values and ranges, with an explicit *indeterminate* state surfaced in
  the UI, aligns the product with the model's actual competence. The
  interesting research question is the abstention threshold: risk–coverage
  curves would make that trade-off explicit.

## 3. Calibration and uncertainty

The out-of-range flag (backlog 007) becomes deterministic given a parsed
range; residual uncertainty then lives in the extraction itself. Measuring
calibration (does the pipeline's confidence — however proxied — track its
empirical accuracy?) would be a prerequisite before *any* confidence is
shown to a user, since miscalibrated confidence on medical data is worse
than none.

## 4. Robustness

- **OCR-noise sensitivity**: perturbation studies (character substitutions,
  table cell shifts, arrow/symbol corruption) would characterize how
  extraction quality degrades — the current pipeline's behavior under
  imperfect OCR is unknown.
- **Prompt-injection resistance**: a small adversarial suite (documents
  containing instructions) with a measured attack success rate, before and
  after mitigations such as delimiter framing — mitigations reduce, they do
  not eliminate, and the honest output of this work is a number, not a
  claim of immunity.
- **Format generalization**: the prompt encodes assumptions from a handful
  of Belgian formats; a leave-one-laboratory-out evaluation would show how
  far they carry.

## 5. Privacy-preserving variants

The current design sends document content to third-party APIs (recorded
deliberately in ADR-006). Two directions merit comparison on the same
benchmark: PII/PHI redaction *before* the LLM stage (NER-based, with the
irony acknowledged that redaction models also need evaluation), and local
models (docTR + a small instruction-tuned LLM) trading accuracy for data
locality. The comparison itself — a quality/privacy frontier on a synthetic
corpus — would be the contribution; picking a point on it is a product
decision.

## 6. Grounding against authoritative references

Reference ranges are currently taken from the document itself. An
age/sex-aware reference database would allow *discrepancy detection*
(document range vs. expected range) — reframing the system from "trust the
document" toward "cross-check the document", which is arguably the more
interesting data-quality problem. Sourcing and licensing such a database
correctly is the hard part and should not be improvised.

## 7. Handling laboratory format diversity

Belgian lab reports come from many providers (hospital LIS templates,
private networks), and most of the variance sits in *layout semantics* —
which column holds the current result, how historical values and abnormal
markers are denoted, date conventions — rather than in character
recognition. Three approaches, in decreasing order of appeal for this
project:

- **Per-laboratory parsing profiles (favored)**: declarative, versioned
  configurations (column mappings, arrow conventions, date format) selected
  by fingerprinting the report header, feeding the extraction stage.
  Auditable, testable with per-profile fixtures, and cheap to extend — the
  proper generalization of the lab-specific rule this project once carried
  inside a prompt. A leave-one-laboratory-out evaluation (§4) measures how
  far the *default* profile carries without one.
- **A different or "better" OCR model**: only justified if error analysis
  on the evaluation corpus shows OCR itself — not extraction or parsing —
  to be the bottleneck; switching providers without that measurement is
  guesswork.
- **Per-laboratory fine-tuned OCR models (not pursued)**: N models mean N
  training corpora of real health documents (a GDPR Article 9 acquisition
  problem before being an ML problem), N evaluations, and re-training on
  every template change. The maintenance and data-governance costs are out
  of proportion at any scale this project can honestly claim.

The operational counterpart of this section is the quality gate specified
in backlog 015: whatever the OCR and profiles achieve, the system should
measure per-document quality and route low-confidence documents to human
review or explicit rejection rather than degrade silently.

## 8. Reproducibility hygiene

Pinned model versions (a dated snapshot rather than `-latest` aliases),
versioned prompts with provenance on every stored analysis (backlog 010),
and fixture-based evaluations runnable by anyone cloning the repository.
Without these, none of the experiments above would be comparable across
time — reproducibility is the cheapest of the improvements listed here and
the precondition for all the others.

---

*Status: exploratory notes. Items graduate from this document into
`docs/backlog/` when they acquire acceptance criteria and an owner.*
