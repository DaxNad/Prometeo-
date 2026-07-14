# PRODUCTION_PROGRAM_SNAPSHOT_INTAKE_VERTICAL_SLICE_001

## Status

- `STATUS`: `CLOSED` / `TESTED` / `MERGED`
- `MODE`: `READ_ONLY` / `PREVIEW_FIRST`
- `CAPABILITY`: `PRODUCTION_PROGRAM_SNAPSHOT_INTAKE_001`
- `SLICE`: `VERTICAL_SLICE_001`
- `ADAPTER`: `STRUCTURED_TEXT`
- `RUNTIME_IMPLEMENTATION`: `MERGED`
- `RUNTIME_PR`: `#501`
- `RUNTIME_MERGE_SHA`: `4c848c29e6fcd2ca8dba5c6458afa9d7670fe6ca`
- `CLOSURE_DATE`: `2026-07-14`

## Delivered vertical flow

```text
synthetic or sanitized structured text
→ explicit deterministic record delimiter
→ existing pure order parser
→ governed ProductionProgramSnapshotPreview
→ mandatory TL confirmation
→ zero side effects
```

The delivered service is intentionally not connected to an endpoint, TL Chat, file upload, Excel, image acquisition, OCR, SMF, database, planner, agent runtime or Pattern Learning runtime.

## Changed files

The runtime implementation respected the exact two-file allowlist:

```text
backend/app/services/production_program_snapshot_preview.py
backend/tests/test_production_program_snapshot_preview.py
```

No existing parser, normalizer, endpoint, registry or runtime integration file was modified.

## Delivered behavior

The service:

- accepts structured text only;
- requires the explicit `--- RECORD ---` delimiter;
- rejects empty or non-separable input without guessing record boundaries;
- generates deterministic SHA-256 source and snapshot identifiers;
- extracts multiple order records;
- preserves field-level provenance;
- retains unmatched source content;
- exposes missing fields, ambiguous fields and discrepancies separately;
- accepts `customer_requested_date` only when the source labels it explicitly;
- keeps generic date labels such as `DATA`, `SCADENZA`, `CONSEGNA`, `DUE DATE` and `DATA CONSEGNA` ambiguous;
- also preserves separatorless generic date forms such as `CONSEGNA 22/04/2026` as ambiguous;
- returns only non-authoritative semantic states;
- never promotes preview data to `CERTO`.

## Fixed governance values

```text
requires_confirmation=true
persisted=false
writer_called=false
planner_called=false
pattern_learning_called=false
```

## Acceptance evidence

The focused tests prove:

1. deterministic separation of at least two synthetic records;
2. extraction of article code and quantity;
3. aggregation of missing required fields;
4. ambiguous date meaning without promotion to `customer_requested_date`;
5. separatorless generic dates remain ambiguous;
6. unmatched content remains available for review;
7. field-level provenance is preserved;
8. repeated identical input produces identical identities and output;
9. malformed or non-separable input fails closed;
10. invalid quantities remain missing and discrepant;
11. no forbidden runtime integration is imported or called;
12. all side-effect flags remain false.

## Review evidence

The final review identified one actionable defect: generic dates without a separator were accepted by the reused parser but were not initially added to `ambiguous_fields`.

The defect was corrected within the allowlist and covered by a regression test before merge. The review thread was resolved only after the corrected head passed repository CI.

## CI evidence

On final runtime head `303283fc13703ba7e9a9c3d68c0876962aaf5d1f`:

- `SMF Backend Tests`: PASS;
- `Guards`: PASS;
- `Frontend CI`: PASS;
- `TL Eval Guard`: PASS;
- `Privacy Guard`: PASS;
- `Data Leak Guard`: PASS.

The runtime was squash-merged through PR `#501` as commit:

```text
4c848c29e6fcd2ca8dba5c6458afa9d7670fe6ca
```

## Residual limitations

This closed slice does not provide:

- an endpoint;
- TL Chat transport;
- direct file input;
- Excel ingestion;
- screenshot or photograph ingestion;
- OCR;
- persistence or audit persistence;
- TL confirmation persistence;
- SMF or database access;
- planner or Pattern Learning activation;
- support for real industrial fixtures in cloud tools;
- support for a second adapter.

These are explicit scope boundaries, not defects internal to `VERTICAL_SLICE_001`.

## Closure verdict

All acceptance criteria internal to the authorized service-plus-focused-tests boundary are satisfied.

```text
VERDICT: VERTICAL_SLICE_001_CLOSED
RUNTIME: IMPLEMENTED / TESTED / MERGED
ALLOWLIST: RESPECTED
SIDE_EFFECTS: NONE
SCOPE_CREEP: NONE
```

No subsequent slice, adapter, endpoint integration or capability is authorized automatically by this closure.
