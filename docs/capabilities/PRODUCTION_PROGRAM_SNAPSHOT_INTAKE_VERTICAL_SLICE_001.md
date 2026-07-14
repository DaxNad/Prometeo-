# PRODUCTION_PROGRAM_SNAPSHOT_INTAKE_VERTICAL_SLICE_001

## Status

- `STATUS`: `AUTHORIZED`
- `MODE`: `READ_ONLY` / `PREVIEW_FIRST`
- `CAPABILITY`: `PRODUCTION_PROGRAM_SNAPSHOT_INTAKE_001`
- `SLICE`: `VERTICAL_SLICE_001`
- `ADAPTER`: `STRUCTURED_TEXT`
- `RUNTIME_IMPLEMENTATION`: `AUTHORIZED_WITHIN_ALLOWLIST_ONLY`
- `AUTHORITY`: explicit human decision on 2026-07-14

## Purpose

Authorize the smallest verifiable runtime slice for `PRODUCTION_PROGRAM_SNAPSHOT_INTAKE_001`:

```text
synthetic structured text
→ deterministic record separation
→ order parsing and normalization
→ governed production-program snapshot preview
→ mandatory TL confirmation
→ zero side effects
```

This slice proves the canonical preview contract without opening endpoint, file, Excel, OCR, UI, SMF, database, planner, agent-runtime or Pattern Learning integration.

## Preconditions

The following are already established and remain authoritative:

- `docs/capabilities/PRODUCTION_PROGRAM_SNAPSHOT_INTAKE_001.md`;
- the capability is format-agnostic at contract level;
- this slice selects only the first adapter;
- no other adapter is authorized by this decision;
- existing closed capabilities remain closed.

## Selected adapter

The only authorized input format is:

```text
STRUCTURED_TEXT
```

The input must be synthetic or sanitized and must contain clearly delimited production-program records.

The adapter selection does not authorize:

- chat transport;
- Excel parsing;
- screenshot processing;
- photograph processing;
- OCR;
- file upload;
- production data from real industrial sources.

## Authorized vertical flow

The implementation may perform only the following flow:

```text
structured_text
→ deterministic block split
→ parse each record with existing pure order-parsing logic where compatible
→ normalize each parsed record without writer activation
→ aggregate ProductionProgramSnapshotPreview
→ expose missing fields, ambiguous fields, discrepancies and unmatched content
→ return preview with requires_confirmation=true
```

## Allowed files

The implementation allowlist is limited to exactly two files:

```text
backend/app/services/production_program_snapshot_preview.py
backend/tests/test_production_program_snapshot_preview.py
```

No other file may be added or modified by this slice.

## Allowed reuse

The new service may import and reuse existing pure functions only when this does not require modifying their source files or activating adjacent side-effect paths.

Allowed reuse candidates:

- `backend/app/ingest/ocr_parser.py`;
- normalization-only functions from `backend/app/ingest/ocr_ingest.py`.

`backend/app/services/controlled_import_preview.py` may be used as a contract and design reference. It is not in the modification allowlist.

## Canonical output

The service must return a governed object conceptually equivalent to:

```text
ProductionProgramSnapshotPreview
```

The minimum snapshot-level fields are:

- `snapshot_id`;
- `source_id`;
- `source_type` with value `structured_text`;
- `source_status`;
- `period`;
- `orders`;
- `missing_fields`;
- `ambiguous_fields`;
- `discrepancies`;
- `confidence`;
- `semantic_status`;
- `requires_confirmation`;
- `persisted`;
- `writer_called`;
- `planner_called`;
- `pattern_learning_called`.

Required fixed values:

- `requires_confirmation`: `true`;
- `persisted`: `false`;
- `writer_called`: `false`;
- `planner_called`: `false`;
- `pattern_learning_called`: `false`.

Preview data must not be promoted automatically to `CERTO`.

## Row requirements

Each item in `orders` must preserve at least:

- `order_id`;
- `article_code`;
- `quantity`;
- `customer_requested_date` when explicitly identified by the source;
- `priority`;
- `station_hint`;
- `field_statuses`;
- `field_provenance`;
- `unmatched_content`.

Missing values must remain missing and be declared structurally. They must not be defaulted into operational truth.

## Deterministic record separation

Record separation must use an explicit, documented delimiter or another deterministic rule proven by tests.

The implementation must not use:

- probabilistic segmentation;
- language-model inference;
- OCR heuristics;
- hidden fallback to a single combined order.

Malformed or non-separable input must return a governed incomplete or blocked preview rather than guessing record boundaries.

## Date semantics

Only a date explicitly labeled as customer-requested may populate `customer_requested_date`.

Generic labels such as `DATA`, `SCADENZA`, `CONSEGNA` or `DUE DATE` must not be silently mapped to customer-requested date, shipment commitment, planner deadline or production promise.

When date meaning is unclear:

- preserve the raw value and source line;
- add the field to `ambiguous_fields`;
- keep the item and snapshot non-authoritative;
- require TL confirmation.

## Semantic status

Allowed preview outcomes for this slice are limited to non-authoritative states, including:

- `DA_VERIFICARE`;
- `INCOMPLETO`;
- a governed blocked or rejected state when parsing cannot proceed safely.

`CERTO` is forbidden.

## Acceptance criteria

The slice is accepted only when focused tests prove all of the following:

1. one synthetic structured-text input contains at least two clearly separated records;
2. records are separated deterministically;
3. valid article code and quantity values are extracted per record;
4. a missing required value appears in `missing_fields`;
5. a generically labeled date appears in `ambiguous_fields` and is not promoted to `customer_requested_date`;
6. unmatched source content is retained for review;
7. field-level provenance is preserved;
8. snapshot and row statuses remain non-authoritative;
9. `requires_confirmation` is `true`;
10. `persisted`, `writer_called`, `planner_called` and `pattern_learning_called` are all `false`;
11. no file, workbook, database, network, OCR, AI, planner, agent or Pattern Learning runtime is invoked;
12. only the two allowlisted files are changed;
13. all fixtures are synthetic or sanitized;
14. existing parser and normalizer behavior remains unchanged.

## Required focused tests

The dedicated test module must cover at least:

- valid two-record preview;
- missing-field aggregation;
- ambiguous date meaning;
- unmatched-content retention;
- malformed or non-separable input;
- deterministic snapshot/source identity when identical input is repeated;
- explicit no-side-effect flags;
- static or behavioral proof that forbidden integrations are not called.

## Scope out

This slice does not authorize:

- endpoint creation or modification;
- TL Chat integration;
- chat-input transport;
- UI work;
- file upload;
- Excel reading;
- screenshot or photograph processing;
- OCR;
- `SMFAdapter`;
- SMF bootstrap;
- database access;
- importer or writer activation;
- audit persistence;
- production-order mutation;
- planner calls;
- agent-runtime calls;
- Pattern Learning calls;
- operator or station assignment;
- source registry changes;
- cloud processing of industrial data;
- real industrial fixtures;
- modifications to existing parser, normalizer or preview modules;
- support for multiple adapters in this slice.

## Stop conditions

Stop without workaround if implementation requires:

- a third changed file;
- modifying `ocr_parser.py`, `ocr_ingest.py` or `controlled_import_preview.py`;
- an endpoint or request model;
- file, Excel, image or OCR handling;
- `SMFAdapter`, database, importer or writer access;
- planner, agent or Pattern Learning activation;
- date-semantic collapse;
- probabilistic record segmentation;
- real industrial data;
- automatic promotion to `CERTO`;
- another adapter;
- architecture expansion beyond the service-plus-focused-tests boundary.

## Closure boundary

This document authorizes only `VERTICAL_SLICE_001` within the stated two-file allowlist.

It does not authorize a subsequent endpoint slice, a second adapter, confirmation persistence, planner usage, Pattern Learning usage or any other capability automatically.
