# TL_CHAT_UNIFIED_DATA_ACCESS_VERTICAL_SLICE_003

## Status

- `STATUS`: `AUTHORIZED`
- `MODE`: `READ_ONLY_FIRST`
- `CAPABILITY`: `TL_CHAT_UNIFIED_DATA_ACCESS_001`
- `SLICE`: `VERTICAL_SLICE_003`
- `AUTHORITY`: explicit human decision on 2026-07-13
- `RUNTIME_IMPLEMENTATION`: `NOT_AUTHORIZED_BY_THIS_DOCUMENT_ALONE`

## Preflight result

The active capability remains `TL_CHAT_UNIFIED_DATA_ACCESS_001`. Its first authorized iteration already delivers article data, components and operations, and customer-demand data through `VERTICAL_SLICE_001` and `VERTICAL_SLICE_002`.

The smallest remaining closure gap inside the same capability is deterministic conflict handling across sources that are already authorized. The resolver currently recognizes `SOURCE_AMBIGUOUS` as a governed status but resolves valid candidates by source priority without comparing concurrent payloads. The capability contract still requires explicit coverage for ambiguous and conflicting sources.

This slice does not add a new source or open a second capability.

## Objective

When two or more already-authorized read-only candidates provide materially different values for the same operational field and article, TL Chat must declare the conflict instead of silently presenting one value as uncontested.

## Scope in

- candidates already admitted by the existing source-governance boundary;
- deterministic comparison of overlapping fields only;
- conflict detection before final answer rendering;
- explicit structural declaration of conflicting field names and involved sources;
- governed outcome using `SOURCE_AMBIGUOUS` or an existing equivalent conflict state;
- preservation of `source`, `status`, and `confidence` for each conflicting evidence block;
- `requires_tl_confirmation: true`;
- `planner_eligible: false`;
- `can_promote: false`;
- tests for:
  - identical values from multiple authorized sources;
  - one materially conflicting field;
  - multiple materially conflicting fields;
  - uncertain or preview source participating in a conflict;
  - no writes on every path.

## Scope out

- new source registration;
- customer-demand fields beyond the existing five-field contract;
- source-priority redesign;
- automatic source reconciliation;
- automatic promotion to `CERTO`;
- production planning decisions;
- database writes or schema changes;
- importer or SMF activation;
- arbitrary filesystem access;
- UI changes;
- OCR changes;
- autonomous agents;
- cloud processing of industrial data;
- planner, board state, timeline, PWA, audit UI, or Pattern Learning work.

## Allowed implementation files

Implementation requires a separate execution preflight. The expected minimal file set is:

- `backend/app/services/tl_chat_context_resolver.py`;
- resolver-focused tests already present in the repository or one new dedicated test module under `backend/tests/`;
- `backend/app/api/tl_chat.py` only if the existing response renderer cannot expose the governed conflict structure without modification.

No other file is authorized without a stop and a new explicit decision.

## Acceptance criteria

1. Equal overlapping values do not create a false conflict.
2. Different overlapping values from authorized sources produce an explicit governed conflict result.
3. The result identifies conflicting fields and involved sources without inventing a reconciled value.
4. Conflict output remains `DA_VERIFICARE`, requires TL confirmation, is not planner eligible, and cannot promote.
5. Existing source-priority behavior remains unchanged when there is no conflict.
6. Missing, forbidden, and unavailable-source behavior remains unchanged.
7. No write, persistence, importer, planner, UI, OCR, agent, or cloud path is invoked.
8. Dedicated tests and repository guards are green.

## Stop conditions

Stop without workaround if implementation requires:

- a new source or field;
- mutation or persistence;
- changing authority rank or source priority;
- resolving the conflict automatically;
- modifying files outside the allowed set;
- opening a second capability;
- weakening existing deny-by-default behavior;
- changing semantic promotion rules.

## Closure boundary

This document authorizes only the slice perimeter. It does not authorize runtime implementation by itself, does not close `TL_CHAT_UNIFIED_DATA_ACCESS_001`, and does not authorize `VERTICAL_SLICE_004` or any other capability.