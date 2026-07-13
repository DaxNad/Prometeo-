# TL_CHAT_UNIFIED_DATA_ACCESS_VERTICAL_SLICE_004

## Status

- `STATUS`: `AUTHORIZED`
- `MODE`: `READ_ONLY_FIRST`
- `CAPABILITY`: `TL_CHAT_UNIFIED_DATA_ACCESS_001`
- `SLICE`: `VERTICAL_SLICE_004`
- `AUTHORITY`: explicit human decision on 2026-07-13
- `RUNTIME_IMPLEMENTATION`: `NOT_AUTHORIZED_BY_THIS_DOCUMENT_ALONE`

## Preflight result

`VERTICAL_SLICE_001`, `VERTICAL_SLICE_002` and `VERTICAL_SLICE_003` are closed, tested and merged. The capability remains open because the closure contract requires one TL Chat request to consume data from multiple authorized sources and to expose conflicts and missing data through the TL response.

Static review of the current runtime found that application call sites invoke `resolve_tl_chat_context(...)` with a single candidate. Conflict detection therefore exists inside the resolver but is not yet exercised through one end-to-end TL Chat request. `TLChatResponse` also does not yet expose the resolver conflict structure.

The smallest remaining closure gap is a single governed multi-source endpoint path with structured conflict readback. This slice adds no new source and opens no second capability.

## Objective

Allow one TL Chat request to pass at least two already-authorized read-only candidates to the existing context resolver and return a governed, structured conflict result when their overlapping operational values differ.

## Scope in

- one existing TL Chat endpoint path only;
- at least two candidates already authorized by existing source-governance boundaries;
- reuse of `resolve_tl_chat_context(...)` without changing source priority;
- response exposure of:
  - `source`;
  - `source_status`;
  - `confidence`;
  - conflicting field names;
  - involved source names;
  - raw conflicting values;
  - missing data when applicable;
- governed conflict outcome:
  - `SOURCE_AMBIGUOUS`;
  - `DA_VERIFICARE`;
  - `requires_confirmation: true`;
  - no planner eligibility;
  - no promotion;
- one synthetic endpoint test proving a real multi-source request path;
- explicit no-write verification.

## Scope out

- new source registration;
- new customer-demand fields;
- source-priority redesign;
- automatic reconciliation or selection of a winning value;
- database writes or schema changes;
- importer or SMF activation;
- generic filesystem readers;
- new endpoint families;
- UI changes;
- OCR changes;
- planner, board state or timeline work;
- autonomous agents;
- cloud processing of industrial data;
- changes to unrelated TL Chat intents.

## Allowed implementation files

Runtime implementation requires a separate execution preflight. The minimal expected file set is:

- `backend/app/api/tl_chat.py`;
- one existing or new focused endpoint test module under `backend/tests/`;
- `backend/app/services/tl_chat_context_resolver.py` only if a strictly necessary serialization adjustment cannot be implemented at the API boundary.

No other file is authorized without a stop and a new explicit decision.

## Acceptance criteria

1. One TL Chat request path constructs at least two already-authorized candidates for the same article or operational query.
2. The candidates are passed together to the existing resolver.
3. Equal overlapping operational values preserve the existing non-conflict behavior.
4. Different overlapping operational values produce `SOURCE_AMBIGUOUS` and `DA_VERIFICARE` at the endpoint response.
5. The response exposes conflicting fields, involved sources and raw values without inventing a reconciled value.
6. `source`, `source_status` and `confidence` remain present and coherent.
7. Missing data remains explicitly declared when applicable.
8. Conflict output requires confirmation, is not planner eligible and cannot promote.
9. Existing single-source paths and source-priority behavior remain unchanged.
10. No write, persistence, importer, planner, UI, OCR, agent or cloud path is invoked.
11. Focused endpoint tests and repository guards are green.

## Stop conditions

Stop without workaround if implementation requires:

- registering a new source;
- adding operational fields;
- changing source authority or priority;
- mutating or persisting data;
- resolving conflicts automatically;
- modifying files outside the allowed set;
- opening another capability;
- weakening deny-by-default behavior;
- changing semantic promotion rules;
- expanding beyond one endpoint path.

## Closure boundary

This document authorizes only the slice perimeter. It does not authorize runtime implementation by itself, does not close `TL_CHAT_UNIFIED_DATA_ACCESS_001`, and does not authorize `VERTICAL_SLICE_005` or any other capability.
