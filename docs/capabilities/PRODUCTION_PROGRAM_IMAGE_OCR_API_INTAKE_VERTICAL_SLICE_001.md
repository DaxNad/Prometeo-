# PRODUCTION_PROGRAM_IMAGE_OCR_API_INTAKE_VERTICAL_SLICE_001

## Status

- `STATUS`: `AUTHORIZED`
- `CAPABILITY`: `PRODUCTION_PROGRAM_IMAGE_OCR_API_INTAKE_001`
- `SLICE`: `VERTICAL_SLICE_001`
- `MODE`: `LOCAL_ONLY / READ_ONLY / PREVIEW_FIRST`
- `RUNTIME_IMPLEMENTATION`: `AUTHORIZED_WITHIN_ALLOWLIST_ONLY`

## Purpose

Authorize one governed runtime path:

```text
strict Base64 PNG/JPEG
→ configured local OCR adapter
→ existing production-program OCR acquisition
→ review-only HTTP response
```

## Exact allowlist

Only these files may change:

```text
backend/app/api/production_program_image_ocr_acquisition.py
backend/tests/test_production_program_image_ocr_acquisition_endpoint.py
backend/app/main.py
```

No fourth file may change. Closed OCR acquisition, Tesseract, snapshot-preview and article-specification API modules must remain unchanged.

## Endpoint contract

```text
POST /production-program/image-ocr/acquire
```

Request:

```json
{"image_base64":"<non-empty Base64 string>"}
```

The API layer may only validate the request, strictly decode Base64, resolve `build_production_program_ocr_adapter()` through dependency injection, invoke `acquire_production_program_image_ocr(...)`, and serialize the existing result.

## Response contract

For valid JSON and valid Base64, return HTTP 200 with:

```text
ok
status
source_id
source_hash
media_type
provider
error_code
requires_confirmation
semantic_status
persisted
writer_called
planner_called
pattern_learning_called
observed_text
normalized_lines
snapshot_preview
```

Fixed values:

```text
requires_confirmation=true
semantic_status=DA_VERIFICARE
persisted=false
writer_called=false
planner_called=false
pattern_learning_called=false
```

All acquisition fields and `snapshot_preview` must be copied without semantic alteration. `normalized_lines` may only become a JSON list.

## Error mapping

Malformed Base64 returns HTTP 422 with `INVALID_IMAGE_BASE64`. Standard schema validation may return 422 for a missing or empty field.

All OCR-domain outcomes return HTTP 200 and preserve the existing status and error code, including rejected input, missing adapter, unsupported media, OCR failure or timeout, invalid/empty OCR output, ready preview and blocked preview.

## Required tests

Tests must prove:

1. synthetic PNG and JPEG success paths;
2. malformed, missing and empty Base64 handling;
3. missing adapter and unsupported bytes fail closed;
4. OCR timeout and failure preservation;
5. ready and blocked preview serialization;
6. provenance, provider, observed text and normalized lines preservation;
7. fixed governance flags;
8. dependency override without installed Tesseract;
9. router registration in the main app;
10. no writer, database, planner, Pattern Learning, network or cloud invocation.

Fixtures must be synthetic and non-sensitive.

## Acceptance criteria

1. Exactly three allowlisted files change.
2. Endpoint path and request schema match the capability contract.
3. Strict Base64 decoding is used.
4. Provider resolution is dependency-injected and fail-closed.
5. Existing OCR acquisition is the only domain execution path.
6. Statuses, errors, provenance, observed evidence and preview remain unaltered.
7. Governance flags remain read-only.
8. Main-app router registration is tested.
9. Focused tests and repository guards pass.

## Scope out

Not authorized: frontend, camera, file picker, multipart, paths, URLs, multiple images, other formats, preprocessing, confirmation application, persistence, SMF, database writes, planner, Pattern Learning, TL Chat, cloud OCR, closed-module changes, capability closure or another slice.

## Stop conditions

Stop if implementation requires a fourth file, a closed-module change, duplicate media/OCR/normalization/preview logic, article-domain result types, semantic inference in the API, any write path, another transport, frontend work or real production images.

## Closure boundary

This document authorizes only `VERTICAL_SLICE_001` within the exact three-file allowlist. It does not close the capability or authorize a following slice.
