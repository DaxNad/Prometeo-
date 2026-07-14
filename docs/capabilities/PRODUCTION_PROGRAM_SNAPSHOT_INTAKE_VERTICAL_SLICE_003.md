# PRODUCTION_PROGRAM_SNAPSHOT_INTAKE_VERTICAL_SLICE_003

## Status

- `STATUS`: `AUTHORIZED`
- `MODE`: `READ_ONLY / PREVIEW_FIRST`
- `CAPABILITY`: `PRODUCTION_PROGRAM_SNAPSHOT_INTAKE_001`
- `SLICE`: `VERTICAL_SLICE_003`
- `ADAPTER`: `STRUCTURED_TEXT`
- `DELIVERY`: `EXPLICIT_TL_CHAT_STRUCTURED_TEXT_PREVIEW_BINDING`
- `RUNTIME_IMPLEMENTATION`: `AUTHORIZED_WITHIN_ALLOWLIST_ONLY`
- `AUTHORITY`: explicit human decision on 2026-07-14

## Purpose

Expose the existing structured-text production-program snapshot preview through the already available TL Chat composer without adding a frontend control, second adapter, intent inference or operational write.

The authorized flow is:

```text
exact versioned first-line marker
→ unchanged remaining structured-text body
→ existing build_production_program_snapshot_preview(...)
→ deterministic TL Chat readback plus unchanged preview payload
→ early return before all ordinary TL Chat retrieval
→ zero side effects
```

## Preconditions

- `VERTICAL_SLICE_001` is `CLOSED / TESTED / MERGED`.
- Slice-001 runtime PR `#501` merged at `4c848c29e6fcd2ca8dba5c6458afa9d7670fe6ca`.
- `VERTICAL_SLICE_002` is `CLOSED / TESTED / MERGED`.
- Slice-002 runtime PR `#504` merged at `9bc4ca124cb9faee2b5c1780857e3b776c16037e`.
- Existing service: `backend/app/services/production_program_snapshot_preview.py`.
- Existing endpoint: `POST /production-program-snapshot/preview`.
- Existing service, endpoint and prior-slice tests must remain unchanged.

## Exact activation marker

The binding activates only when the first line of `TLChatRequest.question` is exactly:

```text
PROMETEO_PROGRAM_SNAPSHOT_PREVIEW_V1
```

The marker is:

- case-sensitive;
- versioned;
- complete;
- valid only as the entire first line;
- not inferred from ordinary language.

The remaining text after the first line break is the structured-text body passed to the existing service without semantic correction, completion or reinterpretation.

## Near-miss behavior

The following must not activate this slice:

```text
Mostrami PROMETEO_PROGRAM_SNAPSHOT_PREVIEW_V1
```

```text
PROMETEO_PROGRAM_SNAPSHOT_PREVIEW
```

```text
prometeo_program_snapshot_preview_v1
```

```text
Vorrei importare il programma produzione
```

```text
Il programma contiene questi ordini...
```

A marker appearing after the first line must not activate the binding.

## Early-return boundary

The explicit marker path must be intercepted at the beginning of the shared `tl_chat(...)` route handler before:

- `_build_contract_response(...)`;
- article extraction;
- lifecycle loading;
- ordinary TL Chat source loading;
- `build_governed_retrieval_pack(...)`;
- resolver, reader or evidence fallback execution.

The explicit path must return immediately after constructing the governed snapshot response.

Both existing routes must preserve identical behavior:

```text
POST /tl/chat
POST /chat
```

## Response boundary

The response remains a `TLChatResponse`.

The runtime may add one optional field:

```text
production_program_snapshot_preview
```

This field must contain the complete existing service result without field renaming or semantic reinterpretation.

The human-readable `answer` must deterministically expose, where present:

- semantic status;
- period;
- number of detected orders;
- order identifier;
- article code;
- quantity;
- explicitly identified customer-requested date;
- ambiguous dates;
- missing fields;
- discrepancies;
- requirement for TL confirmation;
- no-persistence statement.

Unmatched content and provenance remain available in the attached preview payload and must not be discarded or promoted.

## Fixed governance invariants

```text
requires_confirmation=true
persisted=false
writer_called=false
planner_called=false
pattern_learning_called=false
```

Automatic promotion to `CERTO` is forbidden.

## Exact implementation allowlist

```text
backend/app/api/tl_chat.py
backend/tests/test_tl_chat_production_program_snapshot_binding.py
```

No other file may be added or modified.

## Runtime file boundary

Changes to `backend/app/api/tl_chat.py` may contain only:

1. import of the existing snapshot preview service;
2. exact marker constant;
3. pure marker/body extraction helper;
4. pure deterministic preview rendering helper;
5. optional typed response field for the unchanged preview payload;
6. early return at the beginning of the shared route handler.

The file must not introduce:

- a second adapter;
- keyword or intent inference;
- frontend dependencies;
- filesystem access for this path;
- database, SMF, importer or writer access;
- persistence or confirmation application;
- network or cloud calls;
- planner, agent runtime or Pattern Learning calls.

## Focused test boundary

The new focused test file must prove at least:

1. exact marker on the first line activates the binding;
2. valid multi-record body matches the existing service output;
3. marker-only input returns governed `BLOCCATO` preview;
4. missing delimiter remains fail-closed;
5. generic dates remain ambiguous;
6. all no-side-effect flags remain false;
7. `_build_contract_response(...)` is not called on the explicit path;
8. `build_governed_retrieval_pack(...)` is not called on the explicit path;
9. lifecycle and ordinary TL Chat source loaders are not called on the explicit path;
10. near-miss markers do not activate;
11. marker after the first line does not activate;
12. ordinary TL Chat behavior remains unchanged;
13. `/chat` and `/tl/chat` remain equivalent;
14. only the existing snapshot service is called;
15. the existing service, endpoint and prior tests remain unchanged.

Bypass tests must use deterministic monkeypatch guards that raise if a forbidden ordinary TL Chat component is invoked.

## Acceptance criteria

1. Exact first-line marker activates the snapshot-preview binding.
2. The body is passed to the existing service without semantic transformation.
3. Valid multi-record input returns deterministic preview output.
4. The complete preview result is attached to the TL Chat response.
5. The textual answer exposes status, period, orders, missing fields, ambiguity and discrepancies.
6. Marker-only input remains governed and `BLOCCATO`.
7. Input without the explicit record delimiter remains fail-closed.
8. Generic date labels remain ambiguous and do not populate `customer_requested_date`.
9. `requires_confirmation=true`.
10. All side-effect flags remain false.
11. No automatic promotion to `CERTO` occurs.
12. `_build_contract_response(...)` is bypassed.
13. `build_governed_retrieval_pack(...)` is bypassed.
14. No lifecycle, reader, database, filesystem or other TL Chat source is consulted.
15. Ordinary TL Chat questions preserve existing behavior.
16. Near-miss markers do not activate the binding.
17. `/chat` and `/tl/chat` remain behaviorally identical.
18. Existing snapshot service and endpoint remain unchanged.
19. No frontend file changes.
20. Only the two allowlisted files change.
21. Focused tests and repository guards pass.

## Scope out

Not authorized:

- frontend or UI changes;
- context-field-only transport;
- natural-language intent inference;
- Excel, workbook or direct file ingestion;
- upload handling;
- screenshot or photograph ingestion;
- OCR;
- persistence or audit persistence;
- confirmation persistence or application;
- source registry changes;
- customer-demand binding changes;
- SMF or database access;
- planner, operator assignment, agent runtime or Pattern Learning;
- network or cloud processing;
- real industrial fixtures;
- a second adapter;
- modification of the existing snapshot service or endpoint.

## Stop conditions

Stop without workaround if implementation requires:

- a marker that is not exact, versioned and first-line-only;
- keyword or natural-language intent inference;
- traversal through `_build_contract_response(...)` on the explicit path;
- invocation of `build_governed_retrieval_pack(...)` on the explicit path;
- frontend modification;
- service or endpoint modification;
- a third changed file;
- body correction, completion or semantic reinterpretation;
- loss of missing fields, ambiguity, discrepancies, provenance or unmatched content;
- automatic promotion to `CERTO`;
- persistence, confirmation application or any side effect;
- Excel, upload, image, OCR, database, SMF, planner, agent or Pattern Learning integration;
- another adapter.

## Closure boundary

This document authorizes only `VERTICAL_SLICE_003` within the exact two-file runtime allowlist.

It does not authorize implementation outside that allowlist, capability-level closure, `VERTICAL_SLICE_004`, a second adapter, frontend work, persistence, confirmation application, planner usage, Pattern Learning usage or another capability automatically.
