# PROMETEO_NEXT_CAPABILITY_PRIORITY_PREFLIGHT_2026_07_15

## Status

- `STATUS`: `COMPLETED`
- `MODE`: `READ_ONLY_PROJECT_PREFLIGHT`
- `BASELINE`: `main` at `03c0ecacb2281a246ebe807a2643075881bda22c`
- `SELECTED_CAPABILITY`: `PRODUCTION_PROGRAM_IMAGE_OCR_UI_INTAKE_001`
- `RUNTIME_AUTHORIZED`: `false`
- `AUTOMATIC_SLICE_AUTHORIZED`: `false`

## Objective

Select exactly one next vertical capability after closure of both:

- `PRODUCTION_PROGRAM_IMAGE_OCR_INTAKE_001`;
- `PRODUCTION_PROGRAM_IMAGE_OCR_API_INTAKE_001`.

Neither closed capability may be modified, reopened or extended implicitly.

## Canonical evidence

`docs/CURRENT_STATE.md` remains the canonical project-state source. It records the following partial areas:

- planner not validated on one complete shift scenario;
- events and blocks not closed as a complete product timeline;
- PWA not validated as one complete department workflow;
- backend audit not exposed as a complete TL timeline;
- Pattern Learning not fed end-to-end by the confirmed intake chain.

The production-program image path now provides:

```text
PNG/JPEG image
→ strict Base64 API boundary
→ explicitly configured local OCR
→ observed OCR evidence
→ canonical production-program snapshot preview
→ review-only response
→ zero operational side effects
```

The path is callable but has no dedicated browser input and review surface.

## Reusable verified pattern

The repository already contains a closed article-specification acquisition UI that proves a minimal frontend pattern:

```text
single browser image selection
→ local Base64 conversion
→ existing API client
→ governed endpoint request
→ explicit review-only result rendering
→ fail-closed error rendering
```

That pattern introduced no new frontend dependency and did not modify OCR or domain behavior.

## Candidate comparison

| Candidate | Immediate operational value | Dependency readiness | Smallest verifiable slice | Main risk | Decision |
| --- | --- | --- | --- | --- | --- |
| Production-program OCR UI intake | High: makes the closed local OCR/API path directly usable from the browser | High: OCR runtime and API are closed; UI pattern already exists | One route/page, one API-client binding, focused tests and navigation registration only if mapped | Accidental expansion into camera, persistence or global PWA redesign | `SELECTED` |
| Planner full-shift validation | High but decision-sensitive | Medium | Requires representative shift dataset, authority boundaries and broad scenario assertions | Implicit production decisions or false planner readiness | `DEFER` |
| Complete TL event/audit timeline | Medium-high | Medium | Requires reconciliation of multiple event and audit sources plus presentation policy | Cross-domain and UI scope expansion | `DEFER` |
| PWA single department workflow | High eventually | Low-medium | Crosses multiple routes and operating flows | Product-wide redesign before stable workflow selection | `DEFER` |
| Pattern Learning end-to-end | Medium | Low | Requires stable confirmed intake and governed feedback labels | Learning from unconfirmed evidence | `DEFER` |
| SaaS/MES or multi-tenant work | Low for the current milestone | Low | Not a small vertical slice | Premature product architecture | `OUT_OF_PHASE` |

## Selection

The next capability is:

```text
PRODUCTION_PROGRAM_IMAGE_OCR_UI_INTAKE_001
```

Purpose:

```text
select exactly one local PNG/JPEG in the browser
→ convert locally to Base64
→ call POST /production-program/image-ocr/acquire
→ render status, provenance, OCR evidence and snapshot preview
→ preserve review-only governance
→ no persistence or confirmation application
```

This is a new presentation capability. It composes with the two closed OCR capabilities but does not modify or reopen them.

## Why this is first

1. The prior blocking dependency, the governed API boundary, is now closed.
2. It creates the smallest human-usable end-to-end flow from image selection to reviewable production-program preview.
3. It can reuse an already verified frontend acquisition pattern without adding a new framework or dependency.
4. It remains local-only, preview-first and side-effect free.
5. It avoids planner authority, timeline reconciliation, persistence and learning expansion.

## Required future contract boundary

A separate contract-only change must precede runtime work. That contract must map the actual frontend structure and constrain the first slice to the minimum observed files, likely covering only:

- one dedicated page/component;
- one focused page test;
- the existing frontend API client;
- route or navigation registration only when required by the mapped application structure.

The exact allowlist must be derived from repository inspection, not assumed from this preflight.

The contract must require:

- exactly one browser-selected image;
- PNG/JPEG only;
- local Base64 conversion;
- the existing production-program OCR API endpoint only;
- explicit loading, governed success, rejected, blocked and transport-error states;
- rendering of `status`, `source_id`, `source_hash`, `media_type`, `provider`, `error_code`, `observed_text`, `normalized_lines` and `snapshot_preview` as available;
- visible `requires_confirmation=true` and `semantic_status=DA_VERIFICARE` governance;
- no interpretation of HTTP 200 alone as operational success;
- synthetic and non-sensitive frontend tests.

## Permanent exclusions

This selection does not authorize:

- changes to either closed OCR capability or its backend modules;
- camera capture or device APIs;
- multipart upload, filesystem path or URL input;
- multiple images, PDF, Excel, TIFF or HEIC;
- image preprocessing or OCR correction;
- confirmation application;
- persistence, SMF or database writes;
- planner, Pattern Learning or TL Chat integration;
- cloud OCR or external network processing;
- global PWA redesign;
- automatic authorization of runtime or another slice.

## Stop conditions

Stop if the future contract or implementation requires:

- modification of a closed OCR/backend module;
- a new frontend dependency;
- more than one image or another transport;
- camera or filesystem path access;
- semantic transformation of the backend result;
- persistence, confirmation application or planning behavior;
- broad PWA/navigation redesign;
- real production images in tests;
- files outside the exact mapped allowlist.

## Acceptance

This project-wide preflight is complete when:

1. exactly one capability is selected;
2. both OCR capabilities remain closed and unchanged;
3. the selection is the smallest currently unblocked human-usable vertical path;
4. competing partial areas are explicitly deferred;
5. no runtime or vertical slice is automatically authorized.

All five conditions are satisfied.

## Next move

Create the contract-only document for `PRODUCTION_PROGRAM_IMAGE_OCR_UI_INTAKE_001` after a read-only mapping of the frontend route, page, API client and test structure. Define the exact file allowlist and stop conditions before any runtime change.
