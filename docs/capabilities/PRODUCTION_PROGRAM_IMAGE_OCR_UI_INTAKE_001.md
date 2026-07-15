# PRODUCTION_PROGRAM_IMAGE_OCR_UI_INTAKE_001

## Status

- `STATUS`: `AUTHORIZED_CONTRACT_ONLY`
- `MODE`: `LOCAL_ONLY / READ_ONLY / PREVIEW_FIRST`
- upstream OCR runtime/API: `CLOSED / TESTED / MERGED`
- frontend runtime: `NOT_AUTHORIZED`

## Purpose

Define a future browser surface for one local PNG/JPEG image: local Base64 conversion, `POST /production-program/image-ocr/acquire`, and governed review-only rendering. No frontend runtime is implemented here.

## Mapped pattern

- `frontend/src/App.tsx`: explicit path selection and navigation;
- `frontend/src/pages/ArticleSpecificationAcquisitionPage.tsx`: single-file selection, browser Base64 conversion, loading/error/result state;
- `frontend/src/lib/api/prometeo.ts`: typed POST through existing `apiPost(...)`;
- `frontend/src/pages/ArticleSpecificationAcquisitionPage.test.tsx`: Vitest/Testing Library with mocked API and synthetic files.

Only this structural pattern may be reused. Article confirmation, authority, writer and persistence behavior must not be copied.

## Future route and flow

```text
/production-program/image-ocr/acquire
```

```text
one local PNG/JPEG
→ Base64 in browser memory
→ POST /production-program/image-ocr/acquire
→ render status, provenance, OCR evidence and snapshot preview
→ no confirmation
→ no persistence
```

`App.tsx` may only import the future page, add one navigation entry and render the exact route. No router dependency or global navigation redesign.

## Client contract

`frontend/src/lib/api/prometeo.ts` may add request/response types and `acquireProductionProgramImageOCR(...)`.

Request:

```json
{"image_base64":"<non-empty Base64 string>"}
```

The response type must preserve without semantic rewriting:

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

The UI must explicitly state that the result is review-only, non-authoritative and not persisted. HTTP 200 alone is not operational success. At minimum it must distinguish `PREVIEW_READY`, `PREVIEW_BLOCKED`, `OCR_FAILED` and `REJECTED`; other statuses and error codes remain visible.

The file input is single-selection and communicates PNG/JPEG support. Backend signature validation remains authoritative. No client-side OCR, signature detection, normalization or preview parsing.

## Future runtime allowlist

Exactly these four files may change:

```text
frontend/src/pages/ProductionProgramImageOCRAcquisitionPage.tsx
frontend/src/pages/ProductionProgramImageOCRAcquisitionPage.test.tsx
frontend/src/lib/api/prometeo.ts
frontend/src/App.tsx
```

No fifth file may change.

These modules remain unchanged:

```text
backend/app/api/production_program_image_ocr_acquisition.py
backend/app/ingest/production_program_image_ocr_acquisition.py
backend/app/services/production_program_tesseract_ocr.py
backend/app/services/production_program_snapshot_preview.py
frontend/src/pages/ArticleSpecificationAcquisitionPage.tsx
frontend/src/pages/ArticleSpecificationAcquisitionPage.test.tsx
```

## Required future tests

Synthetic, non-sensitive fixtures only. Tests must prove:

1. review-only and zero-persistence semantics are visible;
2. submit is disabled without a file;
3. synthetic PNG is converted and sent as Base64;
4. synthetic JPEG is accepted;
5. exact endpoint use;
6. `PREVIEW_READY` renders provenance, evidence, normalized lines and preview;
7. `PREVIEW_BLOCKED` does not claim success;
8. `OCR_FAILED` and `REJECTED` expose error codes;
9. governance flags are shown unaltered;
10. transport failure is visible;
11. no confirmation, writer or persistence control exists;
12. route/navigation render the page through `App.tsx`.

## Acceptance criteria

1. Exactly four allowlisted files change.
2. One PNG/JPEG only.
3. Base64 conversion remains local.
4. Existing API helper is reused.
5. Backend fields are rendered without semantic mutation.
6. No write or confirmation action exists.
7. Focused tests, TypeScript build and repository guards pass.
8. No backend changes.

## Scope limits and stop conditions

Not authorized: camera/device APIs, drag-and-drop expansion, multipart, paths, URLs, multiple images, additional formats, preprocessing, client OCR/parsing/inference, confirmation, persistence, SMF/database, planner, Pattern Learning, TL Chat, cloud OCR, PWA/service-worker redesign, global routing redesign, new dependencies, modification of article-specification UI files, backend changes, real production images or sensitive data.

Stop if any fifth file, backend change, new dependency, duplicate domain logic, write control or broader transport/UI architecture is required.

## Closure boundary

This document authorizes only the capability contract. Frontend implementation, tests and route registration require a separate explicit authorization.
