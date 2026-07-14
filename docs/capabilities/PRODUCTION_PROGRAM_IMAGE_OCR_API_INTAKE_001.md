# PRODUCTION_PROGRAM_IMAGE_OCR_API_INTAKE_001

## Status

- `STATUS`: `AUTHORIZED_CONTRACT_ONLY`
- `MODE`: `LOCAL_ONLY / READ_ONLY / PREVIEW_FIRST`
- upstream `PRODUCTION_PROGRAM_IMAGE_OCR_INTAKE_001`: `CLOSED / TESTED / MERGED`
- runtime and frontend: `NOT_AUTHORIZED`

## Purpose

Define a future HTTP boundary for one Base64 PNG/JPEG that delegates to the existing production-program OCR acquisition and returns a review-only snapshot preview. This document contains no runtime implementation.

## Mapped integration

The repository registers API routers in `backend/app/main.py` by explicit import and `app.include_router(...)`.

The existing article-specification acquisition endpoint demonstrates the permitted structural pattern: Pydantic request, strict Base64 decoding, dependency-injected local OCR adapter, HTTP 422 for malformed Base64, HTTP 200 for governed domain results, and a main-app registration test.

Only this structural pattern may be reused. Production-program contracts remain authoritative.

## Future endpoint

```text
POST /production-program/image-ocr/acquire
```

Request:

```json
{"image_base64":"<non-empty Base64 string>"}
```

The endpoint may only decode strict Base64, resolve `build_production_program_ocr_adapter()`, call `acquire_production_program_image_ocr(...)`, and serialize its result. Media detection, OCR execution, normalization, and preview parsing remain in existing modules.

## Response schema

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

Fixed governance values:

```text
requires_confirmation=true
semantic_status=DA_VERIFICARE
persisted=false
writer_called=false
planner_called=false
pattern_learning_called=false
```

Acquisition fields and `snapshot_preview` must be copied without semantic alteration. Tuple lines become a JSON list only.

## Error mapping

HTTP 422:

```text
INVALID_IMAGE_BASE64
```

Standard request validation may also return 422 for a missing or empty field.

All acquisition-domain outcomes return HTTP 200 and preserve their status and error code, including:

```text
REJECTED
OCR_FAILED
PREVIEW_READY
PREVIEW_BLOCKED
OCR_ADAPTER_REQUIRED
UNSUPPORTED_IMAGE_FORMAT
OCR_EXTRACTION_FAILED
INVALID_OCR_RESULT
OCR_EMPTY_TEXT
PRODUCTION_PROGRAM_TESSERACT_OCR_FAILED
PRODUCTION_PROGRAM_TESSERACT_OCR_TIMEOUT
```

## Future runtime allowlist

Exactly these three files may change in one later authorized slice:

```text
backend/app/api/production_program_image_ocr_acquisition.py
backend/tests/test_production_program_image_ocr_acquisition_endpoint.py
backend/app/main.py
```

These existing modules must remain unchanged:

```text
backend/app/ingest/production_program_image_ocr_acquisition.py
backend/app/services/production_program_tesseract_ocr.py
backend/app/services/production_program_snapshot_preview.py
backend/app/api/article_specification_acquisition.py
```

## Required future tests

Tests must cover valid synthetic PNG/JPEG, malformed Base64, missing adapter, unsupported bytes, OCR timeout/failure, ready and blocked previews, provenance, observed evidence, fixed governance flags, dependency override without installed Tesseract, and router registration in the main app.

Fixtures must be synthetic and non-sensitive.

## Scope limits

The future slice excludes frontend, file picker, multipart, paths, URLs, multiple images, other formats, preprocessing, confirmation application, persistence, planner integration, TL Chat integration, and changes to closed OCR modules.

## Stop conditions

Stop if implementation requires a fourth file, modification of a closed OCR module, duplicate parsing or validation, article-domain result imports, another transport, semantic inference in the API layer, frontend work, or real production images.

## Closure boundary

This document authorizes only the capability contract. Runtime, tests, router registration, and any following slice require a separate explicit authorization.
