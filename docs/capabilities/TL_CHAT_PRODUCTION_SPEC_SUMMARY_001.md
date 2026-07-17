# TL_CHAT_PRODUCTION_SPEC_SUMMARY_001 — End-to-end verification closure

## Status

- `CAPABILITY`: `TL_CHAT_PRODUCTION_SPEC_SUMMARY_001`
- `STATUS`: `VERIFIED_END_TO_END_PREVIEW_ONLY`
- `MODE`: `READ_ONLY / PREVIEW_ONLY`
- `DATE`: `2026-07-15`
- `BACKEND_PAYLOAD_PARITY_COMMIT`: `7279d66`
- `LOCAL_AUTH_PROXY_COMMIT`: `a2d87eb`

## Verified chain

```text
TL Chat UI
→ POST /tl/chat through the local Vite proxy
→ local x-api-key authentication
→ FastAPI TL Chat handler
→ production-spec-summary intent
→ spec_intake_preview read-only source
→ governed preview response
→ rendered TL Chat answer
```

The following boundaries were verified:

- direct backend `/tl/chat`: `OK`, HTTP 200 with the configured local `X-API-Key`; the key value is intentionally omitted;
- Vite proxy `/tl/chat`: `OK`, HTTP 200;
- real TL Chat UI: `OK` for the request `sintesi produzione del 12514`;
- local `x-api-key` propagation: `OK`.

## Verification evidence

- `./tools/py -m pytest backend/tests/test_tl_chat_production_spec_summary.py -q`: `6 passed`;
- backend authentication, endpoint binding and TL Chat regressions: `12 passed`;
- frontend Vitest suite: `8 passed`;
- frontend TypeScript check: `PASS`;
- direct HTTP request to backend `/tl/chat`: HTTP 200;
- HTTP request through Vite `/tl/chat`: HTTP 200;
- UI rendering at `/tl-chat`: expected preview summary observed.

No API key, token or secret is recorded by this closure.

## Verified response

```text
12514 — SINTESI PRODUZIONE
Fonte: spec_intake_preview
Stato: PREVIEW_ONLY
Identificazione
Componenti principali
Ciclo operativo
Vincoli
Dati mancanti
```

## Limits

- `spec_intake_preview` remains a preview-only source;
- the response requires Team Leader confirmation;
- no value is promoted automatically to `CERTO`;
- no planner, database or SMF mutation is performed;
- the response must not be used operationally without validation;
- this closure does not authorize another capability or any additional runtime change.

## Verdict

```text
CAPABILITY_STATUS: VERIFIED_END_TO_END_PREVIEW_ONLY
RUNTIME_MUTATION: NONE
OPERATIONAL_USE_WITHOUT_TL_CONFIRMATION: FORBIDDEN
```

## Next move

Perform a document-only review before committing this closure.
