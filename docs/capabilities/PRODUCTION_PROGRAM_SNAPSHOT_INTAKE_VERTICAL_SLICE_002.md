# PRODUCTION_PROGRAM_SNAPSHOT_INTAKE_VERTICAL_SLICE_002

## Status

- `STATUS`: `CLOSED` / `TESTED` / `MERGED`
- `MODE`: `READ_ONLY` / `PREVIEW_FIRST`
- `CAPABILITY`: `PRODUCTION_PROGRAM_SNAPSHOT_INTAKE_001`
- `SLICE`: `VERTICAL_SLICE_002`
- `ADAPTER`: `STRUCTURED_TEXT`
- `DELIVERY`: `DEDICATED_FASTAPI_PREVIEW_ENDPOINT`
- `RUNTIME_IMPLEMENTATION`: `MERGED`
- `RUNTIME_PR`: `#504`
- `RUNTIME_MERGE_SHA`: `9bc4ca124cb9faee2b5c1780857e3b776c16037e`
- `CLOSURE_DATE`: `2026-07-14`

## Delivered vertical flow

```text
HTTP POST structured text
→ strict request validation
→ existing build_production_program_snapshot_preview(...)
→ unchanged governed preview response
→ zero side effects
```

The delivered route is:

```text
POST /production-program-snapshot/preview
```

The slice exposes only the structured-text adapter completed in `VERTICAL_SLICE_001`. It does not add another adapter and does not activate persistence, confirmation application, TL Chat, planner or Pattern Learning.

## Changed files

The runtime implementation respected the exact three-file allowlist:

```text
backend/app/api/production_program_snapshot.py
backend/app/main.py
backend/tests/test_production_program_snapshot_endpoint.py
```

`backend/app/main.py` changed only to import the router and register one `app.include_router(...)` call. The existing snapshot service and slice-001 tests were not modified.

## Delivered request boundary

The request model accepts only:

- required `structured_text: str`;
- optional `source_id: str | None`.

The model uses `extra="forbid"`. File paths, workbook data, bytes, images, uploads, database identifiers, planner fields, confirmation commands and persistence controls are rejected by request validation.

## Delivered response boundary

The endpoint delegates directly to the existing service and returns its result without field renaming or semantic reinterpretation. It preserves:

- snapshot and source identity;
- source type and status;
- period and orders;
- missing, ambiguous and discrepant fields;
- confidence and semantic status;
- provenance and unmatched content;
- all no-side-effect flags.

## Fixed governance values

```text
requires_confirmation=true
persisted=false
writer_called=false
planner_called=false
pattern_learning_called=false
```

Automatic promotion to `CERTO` remains forbidden.

## Acceptance evidence

Focused endpoint tests prove:

1. valid two-record structured text returns HTTP 200;
2. article code and quantity are preserved per record;
3. the existing snapshot response is returned without semantic transformation;
4. identical input produces deterministic output and identities;
5. empty input returns governed `BLOCCATO` rather than an unhandled error;
6. input without the explicit delimiter remains fail-closed;
7. missing required fields remain declared;
8. generic dates, including separatorless forms, remain ambiguous and do not populate `customer_requested_date`;
9. provenance and unmatched content remain available;
10. `requires_confirmation=true`;
11. all side-effect flags remain false;
12. canonical router registration is present in `backend/app/main.py`;
13. no database, SMF, filesystem, Excel, upload, image, OCR, network, AI, planner, agent or Pattern Learning runtime is invoked;
14. only the three allowlisted files changed;
15. the existing service and slice-001 tests remained unchanged;
16. focused tests and repository guards pass.

## Review and correction evidence

The initial runtime head passed five workflows but failed `Guards`. The failure was traced to the endpoint test importing `app.main` at module collection time, which could initialize the canonical application before unrelated tests established their configuration.

The test was corrected within the allowlist by replacing the eager canonical-app import with a deterministic static verification of the required router import and single `app.include_router(...)` registration in `backend/app/main.py`.

No runtime behavior or production file outside the authorized boundary was changed by this correction.

## CI evidence

On final runtime head `571188fd8f0b4d77859cd3a423d4884b2afaa26e`:

- `SMF Backend Tests`: PASS;
- `Guards`: PASS;
- `Frontend CI`: PASS;
- `TL Eval Guard`: PASS;
- `Privacy Guard`: PASS;
- `Data Leak Guard`: PASS.

The runtime was squash-merged through PR `#504` as commit:

```text
9bc4ca124cb9faee2b5c1780857e3b776c16037e
```

## Residual limitations

This closed slice does not provide:

- TL Chat or UI integration;
- chat transport;
- Excel or direct file ingestion;
- upload handling;
- screenshot or photograph ingestion;
- OCR;
- persistence or audit persistence;
- TL confirmation persistence or application;
- SMF or database access;
- planner, operator assignment, agent runtime or Pattern Learning activation;
- source registry changes;
- cloud processing of industrial data;
- real industrial fixtures;
- a second adapter.

These are explicit scope boundaries, not defects internal to `VERTICAL_SLICE_002`.

## Closure verdict

All acceptance criteria internal to the authorized endpoint, canonical-registration and focused-test boundary are satisfied.

```text
VERDICT: VERTICAL_SLICE_002_CLOSED
RUNTIME: IMPLEMENTED / TESTED / MERGED
ALLOWLIST: RESPECTED
CANONICAL_ROUTE: REGISTERED
SIDE_EFFECTS: NONE
SCOPE_CREEP: NONE
```

No `VERTICAL_SLICE_003`, subsequent adapter, confirmation persistence, TL Chat integration, planner usage, Pattern Learning usage or another capability is authorized automatically by this closure.
