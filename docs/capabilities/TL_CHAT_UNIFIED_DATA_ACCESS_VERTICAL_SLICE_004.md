# TL_CHAT_UNIFIED_DATA_ACCESS_VERTICAL_SLICE_004

## Status

- `STATUS`: `CLOSED` / `TESTED` / `MERGED`
- `MODE`: `READ_ONLY_FIRST`
- `CAPABILITY`: `TL_CHAT_UNIFIED_DATA_ACCESS_001`
- `SLICE`: `VERTICAL_SLICE_004`
- `AUTHORITY`: explicit human decision on 2026-07-13
- `RUNTIME_IMPLEMENTATION`: `MERGED`
- `PR`: `#497`
- `MERGE_SHA`: `a397b1df92886f23b70561379fca89eef242d562`

## Closure result

`VERTICAL_SLICE_004` closes the final runtime gap identified for `TL_CHAT_UNIFIED_DATA_ACCESS_001`: one existing TL Chat request path now consumes two already-authorized read-only candidates, passes them together to the existing context resolver and exposes governed conflict readback at the endpoint boundary.

The implementation is limited to the existing `/tl/chat` path and preserves source priority, deny-by-default behavior, read-only operation and the existing single-source response when overlapping values agree.

## Delivered scope

- one existing TL Chat endpoint path;
- two already-authorized candidates:
  - `local_specs_metadata`;
  - `spec_intake_preview`;
- reuse of `resolve_tl_chat_context(...)` without resolver modification;
- comparison limited to shared article identity fields already present:
  - `codice`;
  - `disegno`;
  - `rev`;
- structured response exposure of:
  - `source`;
  - `source_status`;
  - `confidence`;
  - conflicting field names;
  - involved source names;
  - raw conflicting values;
  - missing data;
- governed conflict outcome:
  - `SOURCE_AMBIGUOUS`;
  - `DA_VERIFICARE`;
  - `requires_confirmation: true`;
  - no planner eligibility;
  - no promotion;
- equivalent overlapping values preserve existing non-conflict behavior;
- explicit no-write verification.

## Runtime and tests

- `RUNTIME_CHANGED`: `backend/app/api/tl_chat.py`;
- `TESTS_ADDED`: `backend/tests/test_tl_chat_multisource_conflict_endpoint.py`;
- `RESOLVER_CHANGED`: `false`;
- `SOURCE_PRIORITY_CHANGED`: `false`;
- `NEW_SOURCE_REGISTERED`: `false`;
- `DATABASE_WRITE`: `NONE`;
- `PLANNER_ELIGIBLE_ON_CONFLICT`: `false`;
- `AUTOMATIC_PROMOTION_ON_CONFLICT`: `false`;
- `REQUIRES_TL_CONFIRMATION_ON_CONFLICT`: `true`.

## Acceptance evidence

1. One `/tl/chat` request constructs two already-authorized candidates for the same article.
2. Both candidates are passed together to the existing resolver.
3. Equal overlapping values preserve the prior response behavior.
4. Different overlapping values produce `SOURCE_AMBIGUOUS` and `DA_VERIFICARE`.
5. The response exposes field, sources and raw values without reconciliation.
6. `source`, `source_status` and `confidence` remain coherent.
7. Missing data is structurally available.
8. Conflict output requires confirmation and cannot promote or become planner eligible.
9. Existing source priority remains unchanged.
10. No write, persistence, importer, planner, UI, OCR, agent or cloud path is invoked.
11. Local focused validation: `9 passed`.
12. Repository CI: six workflows PASS, including backend guards and structural guard.

## Scope exclusions preserved

- no new source registration;
- no new customer-demand fields;
- no source-priority redesign;
- no automatic reconciliation or winning-value selection;
- no database writes or schema changes;
- no importer or SMF activation;
- no generic filesystem reader;
- no new endpoint family;
- no UI or OCR changes;
- no planner, board state or timeline work;
- no autonomous agent;
- no cloud processing of industrial data;
- no unrelated TL Chat intent changes.

## Capability closure verdict

After `VERTICAL_SLICE_001`, `VERTICAL_SLICE_002`, `VERTICAL_SLICE_003` and this slice, the closure criteria of `TL_CHAT_UNIFIED_DATA_ACCESS_001` are satisfied:

- TL Chat can request data from multiple authorized sources;
- source, status and confidence are preserved;
- conflicts and missing data are declared;
- `PREVIEW_ONLY` remains non-authoritative;
- no write is performed;
- tests cover present, missing, forbidden, ambiguous and conflicting source outcomes.

`VERDICT`: `CAPABILITY_CLOSABLE`.

## Closure boundary

This closure does not authorize a `VERTICAL_SLICE_005`, a new source, a new capability or any mutation, planner, UI, OCR, agent or cloud expansion.