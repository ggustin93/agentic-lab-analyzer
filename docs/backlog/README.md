# Remediation backlog

This backlog documents the findings of a structured audit of this
proof-of-concept (security, responsible-AI, architecture, and testing),
triaged and prioritized deliberately. Each item follows the same
specification template — expected behavior, business rules, edge cases,
constraints, validation intent (acceptance criteria), what is intentionally
out of scope, and open questions — so that it can be converted into a GitHub
issue as-is. Open items are mirrored as GitHub issues (linked in the table);
the files here remain the spec of record.

Two prioritization lenses are used and they intentionally disagree:
**severity** reflects technical risk; **priority** reflects value ÷ effort
for the project's current goal (a credible, honest PoC). An item can be
severity-critical yet scheduled late when a documented mitigation captures
most of its value (see `001`–`004`).

| # | Title | Severity | Priority | Status |
|---|-------|----------|----------|--------|
| [001](001-server-side-upload-validation.md) | Server-side upload validation | High | Should | Done |
| [002](002-bounded-sse-streams.md) | Bounded SSE streams | High | Should | Done |
| [003](003-authentication-and-user-scoping.md) | Authentication & per-user scoping | Critical | Could* | Open ([#2](https://github.com/ggustin93/agentic-lab-analyzer/issues/2)) |
| [004](004-rls-and-private-storage.md) | Row Level Security & private storage | Critical | Could* | Open ([#3](https://github.com/ggustin93/agentic-lab-analyzer/issues/3)) |
| [005](005-rate-limiting.md) | Rate limiting & processing locks | High | Should | Open ([#4](https://github.com/ggustin93/agentic-lab-analyzer/issues/4)) |
| [006](006-generic-error-messages.md) | Generic client-facing error messages | Medium | Should | Done |
| [007](007-deterministic-out-of-range.md) | Deterministic out-of-range flag | High | Should | Open ([#5](https://github.com/ggustin93/agentic-lab-analyzer/issues/5)) |
| [008](008-native-structured-outputs.md) | Native structured outputs | Medium | Should | Open ([#6](https://github.com/ggustin93/agentic-lab-analyzer/issues/6)) |
| [009](009-async-ocr-client.md) | Non-blocking OCR HTTP client | High | Should | Done |
| [010](010-analysis-provenance.md) | Analysis provenance metadata | Medium | Should | Open ([#7](https://github.com/ggustin93/agentic-lab-analyzer/issues/7)) |
| [011](011-prompt-evaluation-harness.md) | Prompt evaluation harness | Medium | Could | Open ([#8](https://github.com/ggustin93/agentic-lab-analyzer/issues/8)) |
| [012](012-sanitize-ai-rendered-html.md) | Sanitize AI-rendered HTML | Medium | Should | Open ([#9](https://github.com/ggustin93/agentic-lab-analyzer/issues/9)) |
| [013](013-test-coverage-gaps.md) | Close targeted test coverage gaps | Medium | Should | Open ([#10](https://github.com/ggustin93/agentic-lab-analyzer/issues/10)) |
| [014](014-processing-task-lifecycle.md) | Processing task lifecycle | Medium | Could | Open ([#11](https://github.com/ggustin93/agentic-lab-analyzer/issues/11)) |
| [015](015-ocr-quality-gate.md) | OCR quality gate with three-way routing | Medium | Could | Open ([#12](https://github.com/ggustin93/agentic-lab-analyzer/issues/12)) |
| [016](016-repository-split.md) | Split DatabaseManager into repositories | Low | Could† | Open ([#13](https://github.com/ggustin93/agentic-lab-analyzer/issues/13)) |
| [017](017-docling-local-ocr-adapter.md) | Local OCR adapters: modality routing (Docling / PaddleOCR) | Low | Could | Open ([#14](https://github.com/ggustin93/agentic-lab-analyzer/issues/14)) |

## Prioritization method

Priorities use MoSCoW informed by a RICE-lite score — Impact (1–5, on the
project's current goal: a credible, honest proof-of-concept) × Confidence ÷
Effort in days. Scores are indicative, recorded so the ordering can be
challenged rather than guessed at; they are re-derived when the goal changes
(the same items would rank differently against a "deploy to production"
goal, where 003/004 become non-negotiable Musts).

| Open item | Impact | Confidence | Effort | Score | MoSCoW |
|---|---|---|---|---|---|
| 007 Deterministic out-of-range flag | 5 | 80 % | 1.5 d | 2.7 | Should |
| 012 Sanitize AI-rendered HTML | 4 | 90 % | 0.5 d | 7.2 | Should |
| 013 Targeted test coverage gaps | 4 | 80 % | 1.5 d | 2.1 | Should |
| 010 Analysis provenance | 3 | 80 % | 1 d | 2.4 | Should |
| 008 Native structured outputs | 3 | 80 % | 1 d | 2.4 | Should |
| 005 Rate limiting | 3 | 90 % | 0.5 d | 5.4 | Should |
| 011 Prompt evaluation harness | 4 | 70 % | 2 d | 1.4 | Could |
| 015 OCR quality gate | 3 | 60 % | 3 d | 0.6 | Could |
| 003 Authentication & scoping | 4 | 70 % | 3 d | 0.9 | Could* |
| 004 RLS & private storage | 4 | 70 % | 2 d | 1.4 | Could* |
| 014 Processing task lifecycle | 2 | 90 % | 0.5 d | 3.6 | Could |
| 016 Repository split | 1 | 90 % | 1 d | 0.9 | Could† |
| 017 Local OCR adapter (Docling / PaddleOCR) | 3 | 60 % | 2 d | 0.9 | Could |

† Deferred with an explicit trigger (see the issue) — recorded so the deferral is a decision, not an omission.

\* Deliberately scheduled behind a documented mitigation: the project runs
locally with synthetic data, and README section 8 states these limitations
openly. They become non-negotiable before any deployment.

Already addressed during the initial hardening pass (kept for the record):
repository hygiene (committed bytecode, duplicate files), documentation
aligned with the actual code, ISO 8601 date validation with rejection of
ambiguous formats, server-enforced medical disclaimer, JSON "cleaning" that
could corrupt valid output, dependency updates for known CVEs, agent
contracts (`agents/base.py`) aligned and injected, backend CI re-enabled.
