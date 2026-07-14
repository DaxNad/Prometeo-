# PRODUCTION_PROGRAM_SNAPSHOT_INTAKE_VERTICAL_SLICE_002

## Status

- `STATUS`: `AUTHORIZED`
- `MODE`: `READ_ONLY / PREVIEW_FIRST`
- `CAPABILITY`: `PRODUCTION_PROGRAM_SNAPSHOT_INTAKE_001`
- `SLICE`: `VERTICAL_SLICE_002`
- `ADAPTER`: `STRUCTURED_TEXT`
- `DELIVERY`: `DEDICATED_FASTAPI_PREVIEW_ENDPOINT`
- `RUNTIME_IMPLEMENTATION`: `AUTHORIZED_WITHIN_ALLOWLIST_ONLY`
- `AUTHORITY`: explicit human decision on 2026-07-14

## Purpose

Expose the existing structured-text snapshot service through one dedicated read-only FastAPI endpoint:

```text
HTTP POST structured text
→ strict request validation
→ build_production_program_snapshot_preview(...)
→ unchanged governed preview response
→ zero side effects
```

This slice does not add another adapter and does not authorize persistence, confirmation application, TL Chat, planner or Pattern Learning.

## Preconditions

- `VERTICAL_SLICE_001` is `CLOSED / TESTED / MERGED`.
- Runtime PR `#501` merged at `4c848c29e6fcd2ca8dba5c6458afa9d7670fe6ca`.
- Closure PR `#502` merged at `ba61c8605a0444b626d54677a19b37719ac48af8`.
- Existing service: `backend/app/services/production_program_snapshot_preview.py`.
- The existing service must remain unchanged.

## Bootstrap preflight

The canonical FastAPI application is assembled in `backend/app/main.py` through explicit router imports and `app.include_router(...)` calls.

A router-only test would not prove canonical availability. Therefore the implementation requires exactly three changed files: router, canonical registration and focused tests.

## Authorized route

```text
POST /production-program-snapshot/preview
```

The route is preview-only and must not reuse persistence, apply or audit-persistence paths.

## Request boundary

The request may contain only:

- required `structured_text: str`;
- optional `source_id: str | None`.

No file path, workbook, bytes, image, upload, database identifier, planner field or confirmation command is accepted. Fixtures must be synthetic or sanitized.

## Response boundary

Return the existing service result without field renaming or semantic reinterpretation. Preserve:

- snapshot and source identity;
- source type and status;
- period and orders;
- missing, ambiguous and discrepant fields;
- confidence and semantic status;
- provenance and unmatched content;
- all no-side-effect flags.

Required invariants:

- `requires_confirmation=true`;
- `persisted=false`;
- `writer_called=false`;
- `planner_called=false`;
- `pattern_learning_called=false`;
- automatic promotion to `CERTO` is forbidden.

## Exact implementation allowlist

```text
backend/app/api/production_program_snapshot.py
backend/app/main.py
backend/tests/test_production_program_snapshot_endpoint.py
```

No other file may be added or modified.

## File boundaries

### Router module

May contain only a strict request model, one `APIRouter`, one preview route, one call to the existing service and direct return of its result.

It must not import or call database, repository, writer, audit persistence, file, Excel, image, OCR, network, cloud, planner, agent, Pattern Learning, TL Chat or confirmation-mutation components.

### `backend/app/main.py`

May change only to import the new router and register one `app.include_router(...)` call. Startup, database, middleware, authentication, health, UI mounts and existing routers must remain otherwise unchanged.

### Endpoint tests

Must prove isolated endpoint behavior and canonical route registration, using synthetic or sanitized fixtures only.

## Acceptance criteria

1. Valid two-record structured text returns HTTP 200.
2. Article code and quantity are preserved per record.
3. Existing snapshot fields are returned without semantic transformation.
4. Identical input produces deterministic snapshot and source identity.
5. Empty input returns governed `BLOCCATO`, not an unhandled error.
6. Missing delimiter remains fail-closed.
7. Missing required fields remain declared.
8. Generic dates, including separatorless forms, remain ambiguous and do not populate `customer_requested_date`.
9. Provenance and unmatched content remain available.
10. `requires_confirmation=true`.
11. All side-effect flags remain `false`.
12. The route is registered in the canonical FastAPI application.
13. No database, SMF, filesystem, Excel, upload, image, OCR, network, AI, planner, agent or Pattern Learning runtime is invoked.
14. Only the three allowlisted files change.
15. The existing service and slice-001 tests remain unchanged.
16. Focused tests and repository guards pass.

## Scope out

Not authorized:

- TL Chat or UI integration;
- chat transport;
- Excel, file upload, screenshot, photograph or OCR;
- SMF or database access;
- importer, writer, audit persistence or preview persistence;
- confirmation persistence or application;
- planner, operator assignment, agent runtime or Pattern Learning;
- source registry changes;
- cloud processing of industrial data;
- real industrial fixtures;
- a second adapter;
- modification of the existing snapshot service.

## Stop conditions

Stop if implementation requires:

- a fourth changed file;
- changing the existing snapshot service or slice-001 tests;
- persistence, apply or audit-persistence behavior;
- file, Excel, image, upload or OCR handling;
- database, SMF, importer or writer access;
- planner, agent, Pattern Learning, TL Chat or UI changes;
- date-semantic collapse;
- automatic promotion to `CERTO`;
- real industrial data;
- another adapter;
- expansion beyond router, canonical registration and focused tests.

## Closure boundary

This document authorizes only `VERTICAL_SLICE_002` within the exact three-file allowlist. It does not authorize a subsequent slice, second adapter, confirmation persistence, TL Chat integration, planner usage, Pattern Learning usage or another capability automatically.
