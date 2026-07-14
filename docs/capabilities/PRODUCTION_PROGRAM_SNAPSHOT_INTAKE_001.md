# PRODUCTION_PROGRAM_SNAPSHOT_INTAKE_001

## Status

- `STATUS`: `AUTHORIZED_CONTRACT_ONLY`
- `MODE`: `READ_ONLY` / `PREVIEW_FIRST`
- `RUNTIME_IMPLEMENTATION`: `NOT_AUTHORIZED`
- `FORMAT_ADAPTER`: `NOT_SELECTED`
- `AUTHORITY`: explicit human decision on 2026-07-14

## Purpose

Define the canonical, format-agnostic contract for acquiring a production program and returning a governed production-program snapshot preview.

The contract exists to close the gap between real TL input and future Pattern Learning usage without selecting an acquisition format, activating runtime integration or permitting operational writes.

## Canonical alignment

This capability is subordinate to:

- `docs/PROMETEO_MASTER.md`;
- `docs/PROMETEO_PATTERN_LEARNING_IMPERATIVE.md`;
- `docs/PROMETEO_INPUT_INTERFACE_V1.md`;
- `docs/CURRENT_STATE.md`.

It contributes only to the following governed cycle:

```text
TL input
→ acquisition adapter selected by a later decision
→ extraction and normalization
→ production-program snapshot preview
→ TL review and confirmation
→ later governed runtime usage
```

This document does not authorize the adapter-selection step or any step after preview.

## Format-agnostic boundary

The contract must remain independent of the acquisition channel.

Potential future adapters include:

- text;
- chat input;
- Excel;
- screenshot;
- photograph.

No adapter is preferred, selected or authorized by this document.

Each future adapter must produce the same canonical preview contract and requires a separate preflight and explicit authorization.

## Canonical preview object

The future runtime object is conceptually named:

```text
ProductionProgramSnapshotPreview
```

The minimum snapshot-level fields are:

- `snapshot_id`;
- `source_id`;
- `source_type`;
- `source_status`;
- `period`;
- `orders`;
- `missing_fields`;
- `ambiguous_fields`;
- `discrepancies`;
- `confidence`;
- `requires_confirmation`;
- `persisted`;
- `writer_called`;
- `planner_called`;
- `pattern_learning_called`.

Required invariants:

- `requires_confirmation` is `true` until an explicitly authorized TL-confirmation path exists;
- `persisted` is `false`;
- `writer_called` is `false`;
- `planner_called` is `false`;
- `pattern_learning_called` is `false`;
- preview data cannot be promoted automatically to `CERTO`.

## Production-program row contract

Each row in `orders` must preserve field-level provenance and uncertainty.

The minimum conceptual fields are:

- `order_id`;
- `article_code`;
- `quantity`;
- `customer_requested_date`;
- `priority`;
- `station_hint`;
- `field_statuses`;
- `field_provenance`.

The final runtime names must be verified against existing domain contracts during a separate implementation preflight. This document does not authorize renaming existing fields or introducing semantic equivalence by assumption.

## Date semantics

The following terms are not automatically equivalent:

- customer-requested date;
- shipment date;
- due date;
- delivery date;
- internal deadline;
- production promise.

The canonical preview must preserve the observed source meaning.

A future adapter or runtime implementation must stop when the source does not distinguish the date meaning. Ambiguous dates must remain explicit and must not be converted into a production promise, planner deadline or authoritative shipment commitment.

## Preview requirements

Every preview must declare:

- extracted values;
- source and provenance;
- missing fields;
- ambiguous fields;
- discrepancies;
- confidence;
- semantic status;
- whether TL confirmation is required;
- explicit no-side-effect evidence.

Unmatched or unclassified source content must be retained as review evidence when technically possible and must not be silently discarded.

## Allowed reuse candidates

A later implementation preflight may evaluate reuse of existing pure or preview-oriented components, including:

- `backend/app/ingest/ocr_parser.py`;
- the normalization-only boundary in `backend/app/ingest/ocr_ingest.py`;
- `backend/app/services/controlled_import_preview.py` as a preview-contract reference;
- the deterministic source-hash and fail-closed patterns in the existing article-specification acquisition boundary.

Listing a component here does not authorize its modification or runtime use.

## Explicitly excluded components

The contract must not be implemented by binding directly to:

- `SMFAdapter`;
- SMF bootstrap paths;
- database engines or repositories;
- customer-demand importers;
- SMF writers;
- production-order writers;
- planner runtime;
- agent runtime;
- Pattern Learning runtime;
- existing article-specification domain parsers.

## Scope in

This authorization covers only:

- the format-agnostic preview contract;
- the conceptual snapshot and row fields;
- source, status, confidence and provenance invariants;
- missing-data, ambiguity and discrepancy behavior;
- read-only and no-side-effect guarantees;
- stop conditions for future adapter and runtime work.

## Scope out

This document does not authorize:

- a parser implementation;
- an acquisition adapter;
- text, Excel, screenshot, photograph or chat-input selection;
- an endpoint;
- file upload;
- OCR;
- UI work;
- SMF access;
- database access;
- persistence or audit persistence;
- planner calls;
- station or operator assignment;
- Pattern Learning calls;
- source registration;
- cloud processing of industrial data;
- real industrial fixtures;
- automatic reconciliation;
- automatic promotion to `CERTO`.

## Acceptance criteria for this contract

1. The contract remains independent of text, Excel, screenshot, photograph and chat-input adapters.
2. The snapshot preview declares source, status, confidence and provenance.
3. Missing fields, ambiguous fields and discrepancies remain structurally distinct.
4. Field-level uncertainty is preserved.
5. Date meanings are not collapsed into an invented equivalence.
6. Preview requires TL confirmation.
7. Persistence, writer, planner and Pattern Learning calls are explicitly false.
8. No runtime file, endpoint, test or source registry is authorized by this document.
9. Existing closed capabilities remain closed and unchanged.
10. A future implementation requires a separate preflight, a minimal vertical slice and explicit human authorization.

## Stop conditions

Stop without workaround if future work requires or assumes:

- selecting an input format before an explicit decision;
- direct reuse of `SMFAdapter` as the preview boundary;
- filesystem, workbook or database mutation;
- importer or writer activation;
- planner or agent runtime activation;
- Pattern Learning activation;
- new OCR, upload, UI or cloud dependencies;
- real industrial data in cloud tools or tests;
- automatic promotion to `CERTO`;
- invented equivalence between date concepts;
- automatic assignment of operators or stations;
- implementation across multiple formats in one slice;
- modifications outside an explicitly approved future allowlist.

## Closure boundary

This document authorizes only the canonical format-agnostic contract.

It does not authorize runtime implementation, does not select the first adapter, does not open a vertical implementation slice and does not authorize any subsequent capability automatically.
