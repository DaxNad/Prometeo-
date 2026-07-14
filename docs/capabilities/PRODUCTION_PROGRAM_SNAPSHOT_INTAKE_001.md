# PRODUCTION_PROGRAM_SNAPSHOT_INTAKE_001

## Status

- `STATUS`: `CLOSED / TESTED / MERGED`
- `MODE`: `READ_ONLY / PREVIEW_FIRST`
- `RUNTIME_IMPLEMENTATION`: `COMPLETE_WITHIN_STRUCTURED_TEXT_BOUNDARY`
- `FORMAT_ADAPTER`: `STRUCTURED_TEXT`
- `TL_CHAT_TRANSPORT`: `COMPLETE`
- `CAPABILITY_CLOSURE_DATE`: `2026-07-14`

## Purpose

Define and deliver the canonical governed path for acquiring a production program as structured text and returning a production-program snapshot preview without operational writes.

The closed flow is:

```text
structured text
→ deterministic parsing and normalization
→ ProductionProgramSnapshotPreview
→ dedicated preview endpoint
→ explicit TL Chat transport
→ TL review required
→ zero side effects
```

## Canonical alignment

This capability remains subordinate to:

- `docs/PROMETEO_MASTER.md`;
- `docs/PROMETEO_PATTERN_LEARNING_IMPERATIVE.md`;
- `docs/PROMETEO_INPUT_INTERFACE_V1.md`;
- `docs/CURRENT_STATE.md`.

It delivers only acquisition and governed preview. It does not authorize confirmation persistence, production planning or Pattern Learning execution.

## Delivered vertical slices

### VERTICAL_SLICE_001

Status: `CLOSED / TESTED / MERGED`.

Delivered:

- pure `STRUCTURED_TEXT` preview service;
- deterministic source and snapshot identity;
- explicit multi-record delimiter;
- field-level provenance;
- unmatched content retention;
- missing fields, ambiguities and discrepancies kept structurally distinct;
- date meanings preserved without invented equivalence;
- fail-closed malformed-input behavior;
- no side effects.

Runtime PR: `#501`.

### VERTICAL_SLICE_002

Status: `CLOSED / TESTED / MERGED`.

Delivered:

- `POST /production-program-snapshot/preview`;
- strict structured-text request boundary;
- unchanged service response;
- canonical router registration;
- no persistence, upload, OCR, planner or Pattern Learning calls.

Runtime PR: `#504`.
Runtime merge: `9bc4ca124cb9faee2b5c1780857e3b776c16037e`.

### VERTICAL_SLICE_003

Status: `CLOSED / TESTED / MERGED`.

Delivered:

- explicit TL Chat transport through exact first-line marker;
- marker: `PROMETEO_PROGRAM_SNAPSHOT_PREVIEW_V1`;
- unchanged body passed to the existing preview service;
- deterministic human-readable readback;
- complete preview payload attached to `TLChatResponse`;
- early return before ordinary TL Chat contract and governed retrieval;
- `/chat` and `/tl/chat` behavioral equivalence;
- no frontend changes and no side effects.

Runtime PR: `#507`.
Runtime merge: `f877428cafe430af3f01e4f1470ed7178c934de2`.
Closure PR: `#508`.
Closure merge: `93a9b950b1e4ab16448103e50cab35d822df3ada`.

## Canonical preview contract

The runtime object is `ProductionProgramSnapshotPreview`.

Minimum snapshot-level fields:

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
- `semantic_status`;
- `requires_confirmation`;
- `persisted`;
- `writer_called`;
- `planner_called`;
- `pattern_learning_called`.

Each order preserves:

- `order_id`;
- `article_code`;
- `quantity`;
- `customer_requested_date`;
- `priority`;
- `station_hint`;
- `field_statuses`;
- `field_provenance`;
- `missing_fields`;
- `ambiguous_fields`;
- `discrepancies`;
- `unmatched_content`.

## Fixed governance invariants

```text
requires_confirmation=true
persisted=false
writer_called=false
planner_called=false
pattern_learning_called=false
```

Automatic promotion to `CERTO` is forbidden.

Customer-requested date, shipment date, due date, delivery date, internal deadline and production promise remain distinct concepts. Ambiguous source labels must remain explicit.

## Closure acceptance

The capability is closed because:

1. the canonical preview contract is implemented;
2. the first adapter, `STRUCTURED_TEXT`, is implemented and tested;
3. a dedicated preview endpoint exists;
4. the preview is reachable through the existing TL Chat composer;
5. provenance, missing data, ambiguities, discrepancies and unmatched content are preserved;
6. malformed input remains fail-closed;
7. ordinary TL Chat retrieval is bypassed on the explicit intake path;
8. all no-side-effect invariants remain enforced;
9. focused tests and repository workflows passed;
10. vertical slices 001, 002 and 003 are closed and merged.

## Residual boundaries

The following are not part of this closed capability and are not authorized by this document:

- Excel or workbook ingestion;
- direct file upload;
- screenshot ingestion;
- photograph ingestion;
- OCR for production-program input;
- UI or mobile controls dedicated to these formats;
- TL confirmation persistence or application;
- snapshot persistence;
- source-registry changes;
- SMF or database access;
- planner runtime;
- station or operator assignment;
- agent runtime;
- Pattern Learning runtime;
- cloud processing of real industrial data;
- automatic reconciliation;
- automatic promotion to `CERTO`.

Excel, screenshot, photograph and OCR require separate adapter or capability preflight, explicit authorization, isolated allowlists and independent acceptance criteria.

## Closure verdict

```text
CAPABILITY: PRODUCTION_PROGRAM_SNAPSHOT_INTAKE_001
STATUS: CLOSED / TESTED / MERGED
DELIVERED_ADAPTER: STRUCTURED_TEXT
DELIVERED_TRANSPORT: ENDPOINT + TL_CHAT
SIDE_EFFECTS: NONE
VERTICAL_SLICE_004_AUTHORIZED: NO
SECOND_ADAPTER_AUTHORIZED: NO
PATTERN_LEARNING_AUTHORIZED: NO
```

This closure does not close `PROMETEO_INPUT_INTERFACE_V1` as a whole and does not authorize any subsequent capability automatically.
