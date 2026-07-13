# TL_CHAT_UNIFIED_DATA_ACCESS_VERTICAL_SLICE_003

## Status

- `STATUS`: `CLOSED` / `TESTED` / `MERGED`
- `MODE`: `READ_ONLY_FIRST`
- `CAPABILITY`: `TL_CHAT_UNIFIED_DATA_ACCESS_001`
- `SLICE`: `VERTICAL_SLICE_003`
- `AUTHORITY`: explicit human decision on 2026-07-13
- `RUNTIME_IMPLEMENTATION`: `MERGED`
- `PR`: `#494`
- `MERGE_SHA`: `cbfa4793e2c914e2f75fab5fdc43a6ad1cbf8b8b`

## Preflight result

The active capability remains `TL_CHAT_UNIFIED_DATA_ACCESS_001`. Its first authorized iteration already delivers article data, components and operations, and customer-demand data through `VERTICAL_SLICE_001` and `VERTICAL_SLICE_002`.

The smallest remaining closure gap inside the same capability was deterministic conflict handling across sources that were already authorized. The resolver recognized `SOURCE_AMBIGUOUS` as a governed status but previously resolved valid candidates by source priority without comparing concurrent payloads. The capability contract required explicit coverage for ambiguous and conflicting sources.

This slice did not add a new source or open a second capability.

## Objective

When two or more already-authorized read-only candidates provide materially different values for the same operational field and article, TL Chat declares the conflict instead of silently presenting one value as uncontested.

## Delivered scope

- candidates already admitted by the existing source-governance boundary;
- deterministic comparison of overlapping operational fields only;
- provenance and governance metadata excluded from conflict comparison;
- conflict detection before final resolver outcome;
- explicit structural declaration of conflicting field names, involved sources and raw values;
- governed outcome `SOURCE_AMBIGUOUS`;
- `confidence: DA_VERIFICARE`;
- `requires_tl_confirmation: true`;
- `planner_eligible: false`;
- `can_promote: false`;
- existing source-priority behavior preserved when no conflict exists;
- no automatic reconciliation or invented authoritative value.

## Runtime and tests

- runtime changed: `backend/app/services/tl_chat_context_resolver.py`;
- tests added: `backend/tests/test_tl_chat_context_resolver_conflicts.py`;
- API changed: no;
- source priority changed: no;
- database write: none;
- planner, importer, SMF, UI, OCR, agent and cloud paths: unchanged and not invoked by this slice.

Dedicated tests cover:

- equal operational values without false conflict;
- one materially conflicting field;
- multiple conflicting fields in deterministic order;
- preview or uncertain source participating in a conflict;
- provenance-only differences ignored;
- conflict output not promotable and not planner eligible.

## Acceptance evidence

1. Equal overlapping values do not create a false conflict: verified.
2. Different overlapping values from authorized sources produce `SOURCE_AMBIGUOUS`: verified.
3. Conflicting fields, sources and raw values are exposed structurally: verified.
4. Conflict output remains `DA_VERIFICARE`, requires TL confirmation, is not planner eligible and cannot promote: verified.
5. Existing source-priority behavior remains unchanged without conflicts: verified.
6. Existing missing, forbidden and unavailable-source behavior remains covered by the pre-existing resolver suite.
7. No write, persistence, importer, planner, UI, OCR, agent or cloud path was added.
8. Repository CI for PR #494: six workflows passed.

## Excluded scope preserved

- new source registration;
- customer-demand fields beyond the existing five-field contract;
- source-priority redesign;
- automatic source reconciliation;
- automatic promotion to `CERTO`;
- production planning decisions;
- database writes or schema changes;
- importer or SMF activation;
- arbitrary filesystem access;
- UI or OCR changes;
- autonomous agents;
- cloud processing of industrial data;
- planner, board state, timeline, PWA, audit UI or Pattern Learning work.

## Closure boundary

`VERTICAL_SLICE_003` is closed, tested and merged. This closure does not by itself close the entire `TL_CHAT_UNIFIED_DATA_ACCESS_001` capability and does not authorize `VERTICAL_SLICE_004`, another source or another capability.
