# PROMETEO_NEXT_CAPABILITY_PRIORITY_PREFLIGHT_2026_07_14

## Status

- `STATUS`: `COMPLETED`
- `MODE`: `READ_ONLY_PROJECT_PREFLIGHT`
- `BASELINE`: `main` after closure of `PRODUCTION_PROGRAM_IMAGE_OCR_INTAKE_001`
- `SELECTED_CAPABILITY`: `PRODUCTION_PROGRAM_IMAGE_OCR_API_INTAKE_001`
- `RUNTIME_AUTHORIZED`: `false`
- `AUTOMATIC_SLICE_AUTHORIZED`: `false`

## Objective

Select exactly one next vertical capability after closure of `PRODUCTION_PROGRAM_IMAGE_OCR_INTAKE_001`, without reopening that capability and without expanding into planner, frontend, persistence or Pattern Learning.

## Canonical evidence

`docs/CURRENT_STATE.md` is the canonical current-state document. It records:

- governed TL Chat and unified read-only access as closed;
- production-program image OCR as a separate completed local runtime path;
- planner validation, complete event timeline, single PWA workflow, complete TL audit timeline and Pattern Learning end-to-end as partial;
- no next authorization currently active.

The closed OCR capability now provides:

```text
validated PNG/JPEG bytes
→ deterministic image identity
→ explicitly enabled local Tesseract
→ observed OCR evidence
→ canonical production-program snapshot preview
→ TL confirmation required
→ zero side effects
```

The path is not yet exposed through an application input boundary.

## Candidate comparison

| Candidate | Immediate operational value | Dependency readiness | Smallest verifiable slice | Main risk | Decision |
| --- | --- | --- | --- | --- | --- |
| Production-program OCR API intake | High: makes the completed OCR path callable | High: OCR acquisition and provider are closed | One local Base64 request endpoint with fail-closed response | Accidental transport or write expansion | `SELECTED` |
| Production-program OCR frontend | Medium-high | Low: no API boundary exists yet | Requires API plus UI and browser workflow | Multi-layer scope creep | `DEFER` |
| Planner full-shift validation | High but decision-sensitive | Medium | Requires broad scenario and authority policy | Autonomous planning claims | `DEFER` |
| Complete TL event/audit timeline | Medium-high | Medium | Crosses multiple event and audit sources | Broad data and UI scope | `DEFER` |
| Pattern Learning end-to-end | Medium | Low | Depends on stable confirmed intake chain | Learning from unconfirmed evidence | `DEFER` |
| SaaS/MES or multi-tenant work | Low for current milestone | Low | Not a small vertical slice | Product-architecture expansion | `OUT_OF_PHASE` |

## Selection

The next capability is:

```text
PRODUCTION_PROGRAM_IMAGE_OCR_API_INTAKE_001
```

Purpose:

```text
validated Base64 request
→ decode exactly one PNG/JPEG image
→ resolve explicitly configured local production-program OCR provider
→ call the closed acquire_production_program_image_ocr(...)
→ return governed read-only preview and provenance
→ no persistence
```

This is a new integration capability. It composes with, but does not modify or reopen, `PRODUCTION_PROGRAM_IMAGE_OCR_INTAKE_001`.

## Why this is first

1. It converts an already tested internal runtime into the smallest callable end-to-end path.
2. It reuses an established FastAPI and dependency-injection pattern already present for article-specification acquisition.
3. It remains local-only, read-only and preview-first.
4. It is a prerequisite for any later production-program camera or file-picker workflow.
5. It avoids planner, timeline, persistence and product-architecture expansion.

## Required future contract boundary

A separate contract must be explicitly authorized before runtime work. That contract should constrain the first slice to:

- one FastAPI router module;
- one focused endpoint test module;
- router registration only if explicitly allowlisted after mapping `backend/app/main.py`;
- Base64 input for exactly one image;
- invalid Base64 mapped deterministically;
- provider unavailable and OCR failures preserved fail-closed;
- response limited to acquisition provenance, observed review evidence and snapshot preview;
- `requires_confirmation=true`;
- `persisted=false`;
- `writer_called=false`;
- `planner_called=false`;
- `pattern_learning_called=false`.

## Permanent exclusions

This selection does not authorize:

- modification of the closed OCR acquisition or Tesseract provider;
- multipart upload or filesystem path input;
- frontend, camera or file picker;
- confirmation application;
- persistence, SMF or database writes;
- planner or Pattern Learning;
- cloud OCR;
- PDF, Excel, TIFF, HEIC or multiple images;
- automatic authorization of a runtime slice.

## Acceptance

The project-wide preflight is complete when:

1. exactly one capability is selected;
2. the selection follows the smallest callable vertical path;
3. the closed OCR capability remains unchanged;
4. competing partial areas are explicitly deferred;
5. no runtime or next slice is automatically authorized.

All five conditions are satisfied.

## Next move

Create the contract-only preflight for `PRODUCTION_PROGRAM_IMAGE_OCR_API_INTAKE_001`, including an exact repository allowlist and stop conditions. Do not implement runtime in the same change.
