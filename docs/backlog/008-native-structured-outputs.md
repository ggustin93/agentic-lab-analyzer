# 008: Native structured outputs

- Severity: Medium · Priority: Should · Labels: responsible-ai, backend

## Context

Both agents use `response_format: {"type": "json_object"}` (which guarantees
JSON, not *our* JSON), describe the schema in prose inside the prompt, and
parse with a hand-rolled cleaner. The schema already exists as Pydantic
models; it should be the contract sent to the API.

## Expected behavior

The provider is given the JSON Schema generated from the Pydantic model
(`model_json_schema()`) via the structured-outputs `response_format`;
responses are validated with `model_validate_json`; on validation failure,
one retry carries the validation error back to the model.

## Business rules

- Output models set `extra="forbid"` so hallucinated fields fail fast
  instead of being silently dropped.
- `services/json_utils.py`'s JSON repair becomes unnecessary and is removed
  (date validation moves next to the models).

## Validation intent (acceptance criteria)

- Given a mocked model response with a missing required field, then exactly
  one retry occurs with the validation message included, and a second
  failure surfaces as a typed pipeline error.
- Given a response with an extra invented field, then validation rejects it.

## Out of scope (deliberate)

Adopting PydanticAI or instructor wholesale; reconsidered under ADR-002's
migration triggers.

## Assumptions / open questions

Confirm structured-outputs support on the exact Mistral and Chutes.AI
endpoints in use; fall back to schema-in-prompt + strict validation where
unsupported.
