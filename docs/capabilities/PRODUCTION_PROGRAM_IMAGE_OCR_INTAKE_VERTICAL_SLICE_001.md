# PRODUCTION_PROGRAM_IMAGE_OCR_INTAKE_VERTICAL_SLICE_001

## Status

- `STATUS`: `AUTHORIZED`
- `MODE`: `READ_ONLY / PREVIEW_FIRST`
- `CAPABILITY`: `PRODUCTION_PROGRAM_IMAGE_OCR_INTAKE_001`
- `SLICE`: `VERTICAL_SLICE_001`
- `DELIVERY`: `ABSTRACT_OCR_ADAPTER_TO_EXISTING_SNAPSHOT_PREVIEW`
- `RUNTIME_IMPLEMENTATION`: `AUTHORIZED_WITHIN_ALLOWLIST_ONLY`
- `AUTHORITY`: explicit human decision on 2026-07-14

## Purpose

Authorize the smallest runtime path:

```text
one PNG/JPEG bytes value
→ magic-byte validation
→ SHA-256 image identity
→ injected abstract OCR adapter
→ observed OCR text retained
→ existing build_production_program_snapshot_preview(...)
→ governed read-only result
```

No real OCR provider, endpoint, frontend or side effect is included.

## Preconditions

- The capability contract is merged.
- `PRODUCTION_PROGRAM_SNAPSHOT_INTAKE_001` is closed.
- `backend/app/services/production_program_snapshot_preview.py` remains unchanged.
- Article-specification OCR behavior remains unchanged.

## Exact allowlist

```text
backend/app/ingest/production_program_image_ocr_acquisition.py
backend/tests/test_production_program_image_ocr_acquisition.py
```

No third file may change.

## Runtime boundary

The new module may define only:

- immutable OCR extraction and acquisition result structures;
- one abstract adapter protocol exposing `extract_text(...)`;
- one public orchestration function accepting image bytes and an injected adapter;
- private pure helpers for validation, media detection, hashing and whitespace-only normalization.

Accepted signatures:

```text
PNG:  89 50 4E 47 0D 0A 1A 0A
JPEG: FF D8 FF
```

Reject fail-closed:

- missing, non-bytes or empty input;
- unsupported signature;
- missing or invalid adapter;
- adapter exception or invalid result;
- adapter-declared failure;
- non-string, empty or whitespace-only OCR text.

File names and extensions are not media evidence.

## Identity and evidence

For valid bytes:

- compute SHA-256 over the original bytes;
- use `production-program-image:sha256:<digest>`;
- preserve media type, provider identifier, exact OCR text and normalized non-empty lines;
- attach the complete downstream snapshot preview unchanged.

The article source-id namespace must not be reused.

## Adapter restrictions

This slice uses only a test-injected abstract adapter. It must not:

- invoke Tesseract;
- read environment variables;
- discover executables;
- create files;
- run subprocesses;
- call network services;
- import article-specification OCR adapters, parsers or result types.

## Snapshot handoff

On successful OCR extraction call exactly:

```text
build_production_program_snapshot_preview(observed_text, source_id=source_id)
```

The acquisition layer must not alter semantic fields, insert delimiters, repair text, relabel dates or populate `customer_requested_date`.

Permanent downstream invariants remain:

```text
requires_confirmation=true
persisted=false
writer_called=false
planner_called=false
pattern_learning_called=false
```

No promotion to `CERTO` is allowed. A downstream `BLOCCATO` result remains governed and must not be rewritten as semantic success.

## Focused tests

The test file must prove:

1. valid PNG and JPEG paths;
2. correct media type passed to the adapter;
3. deterministic hash and source id;
4. different bytes produce different identity;
5. exact OCR text preservation;
6. whitespace-only normalization;
7. multi-record OCR text equals direct service output for the same text and source id;
8. missing delimiter remains downstream `BLOCCATO`;
9. generic dates remain ambiguous;
10. confirmation is required and all side-effect flags are false;
11. every invalid-input and invalid-adapter case fails closed;
12. adapter error code is preserved when valid;
13. snapshot service is called once only after successful OCR;
14. snapshot service is not called after acquisition failure;
15. no filesystem, subprocess, network, SMF, database, writer, planner or Pattern Learning component is invoked.

Forbidden-component checks must use deterministic monkeypatch guards.

## Acceptance criteria

1. Exactly two allowlisted files change.
2. Only PNG/JPEG bytes are accepted.
3. Media detection uses magic bytes.
4. Identity is deterministic and domain-specific.
5. OCR is abstract and test-injected.
6. No Tesseract or real provider is introduced.
7. OCR evidence is preserved.
8. Only whitespace normalization occurs.
9. The existing snapshot service is the only semantic parser.
10. Its result is attached unchanged.
11. Missing, ambiguous, discrepancy and unmatched evidence remains explicit.
12. Date meanings are not collapsed.
13. Confirmation remains mandatory.
14. All side-effect flags remain false.
15. All failures are fail-closed.
16. Focused tests and repository guards pass.

## Scope out

Not authorized:

- endpoint, API models or route;
- frontend, camera, picker or upload;
- Base64, multipart or path input;
- Tesseract, environment configuration, subprocess or temporary files;
- shared OCR-core refactoring;
- article-specification OCR changes;
- snapshot-service changes;
- legacy OCR parser or OCR ingest changes;
- SMF, database, persistence or audit persistence;
- confirmation application, planner or Pattern Learning;
- PDF, TIFF, HEIC, Excel or multiple images;
- real industrial fixtures or cloud OCR.

## Stop conditions

Stop if work requires a third file, semantic OCR correction, missing-delimiter insertion, date inference, any real OCR runtime, endpoint/frontend work, writer access, persistence or modification of a closed capability.

## Closure boundary

This document authorizes only `VERTICAL_SLICE_001` within the exact two-file allowlist. It does not authorize a real OCR provider, endpoint, frontend, capability closure or a following slice.
