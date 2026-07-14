# PRODUCTION_PROGRAM_IMAGE_OCR_INTAKE_001

## Status

- `STATUS`: `AUTHORIZED_CONTRACT_ONLY`
- `MODE`: `READ_ONLY` / `PREVIEW_FIRST`
- `CAPABILITY`: `PRODUCTION_PROGRAM_IMAGE_OCR_INTAKE_001`
- `INPUT_ADAPTER`: `IMAGE_PNG_JPEG`
- `RUNTIME_IMPLEMENTATION`: `NOT_AUTHORIZED`
- `ENDPOINT`: `NOT_AUTHORIZED`
- `FRONTEND`: `NOT_AUTHORIZED`
- `AUTHORITY`: explicit human decision on 2026-07-14

## Purpose

Define the governed contract for acquiring one PNG or JPEG image containing a production program, extracting local OCR text, and passing that observed text to the already closed canonical production-program snapshot preview service.

The target flow is conceptual only:

```text
single PNG/JPEG image
→ deterministic input validation and source hash
→ explicitly configured local OCR
→ observed OCR text retained as review evidence
→ existing build_production_program_snapshot_preview(...)
→ governed read-only preview
→ TL confirmation required
→ zero side effects
```

This document authorizes no runtime implementation.

## Preconditions

- `PRODUCTION_PROGRAM_SNAPSHOT_INTAKE_001` is `CLOSED / TESTED / MERGED`.
- Its delivered adapter remains `STRUCTURED_TEXT`.
- Its public preview boundary remains the canonical target for production-program normalization.
- The closed capability must not be reopened or modified merely to add image acquisition.
- Existing article-specification OCR runtime remains a separate domain capability.

## Read-only mapping of existing OCR assets

The repository already contains:

- `backend/app/ingest/article_specification_image_acquisition.py`;
- `backend/app/services/article_specification_tesseract_ocr.py`;
- `backend/app/ingest/ocr_parser.py`;
- `backend/app/ingest/ocr_ingest.py`.

Observed reusable technical patterns:

- PNG and JPEG magic-byte validation;
- SHA-256 source identity;
- one-image input boundary;
- explicit OCR adapter interface;
- local Tesseract invocation;
- provider opt-in through configuration;
- executable discovery before activation;
- bounded timeout;
- temporary-file cleanup;
- fail-closed extraction errors;
- preservation of extracted text and source identity.

Observed non-reusable domain bindings:

- article-specification parser invocation;
- article-specific result types and status names;
- article-specific environment variable names;
- article-specific source-id prefix;
- `ocr_parser.py` heuristics that may collapse production-program date semantics;
- `ocr_ingest.py` writer and SMF paths.

Therefore direct binding of the new capability to the article-specification parser, article-specific acquisition result or SMF writer is forbidden.

## Canonical boundary

The future image adapter may perform only:

```text
image bytes
→ media validation
→ source hash / source id
→ local OCR text extraction
→ OCR evidence normalization limited to whitespace handling
→ existing production-program snapshot preview service
```

The image adapter must not independently reinterpret production-program fields when the existing snapshot service can evaluate the observed text.

The OCR layer is evidence acquisition, not semantic authority.

## Input contract

A future implementation may accept exactly one binary image supplied as bytes or an equivalent validated Base64 transport selected by a later vertical-slice authorization.

Allowed media types:

```text
image/png
image/jpeg
```

The contract must reject:

- missing input;
- multiple images;
- empty bytes;
- unsupported file signatures;
- malformed Base64 when Base64 transport is later selected;
- OCR adapter unavailable;
- OCR timeout;
- OCR execution failure;
- non-string OCR output;
- empty OCR text.

File names and extensions are not authoritative media evidence.

## Source identity and provenance

The future result must preserve:

- deterministic SHA-256 hash of the original image bytes;
- domain-specific source id for production-program image acquisition;
- detected media type;
- OCR provider identifier;
- observed OCR text;
- normalized OCR lines when produced;
- OCR error code when extraction fails;
- downstream snapshot preview unchanged.

The source-id namespace must not reuse `article-spec-image:sha256`.

## OCR runtime boundary

A future implementation may reuse the proven Tesseract execution pattern but must expose production-program-specific configuration or a separately authorized generic OCR core.

Required properties:

- local execution only;
- explicit opt-in provider;
- no silent provider fallback;
- executable availability check;
- configurable positive timeout;
- temporary file deletion in success, failure and timeout paths;
- stdout captured as observed OCR text;
- stderr and command failures not promoted to successful extraction;
- no network or cloud call.

This contract does not authorize refactoring the article-specification OCR service into a shared core. Such refactoring, if necessary, belongs to a separately authorized minimal vertical slice with an exact allowlist.

## Preview and semantic invariants

Every successful acquisition must terminate in the existing canonical production-program snapshot preview behavior.

Permanent invariants:

```text
requires_confirmation=true
persisted=false
writer_called=false
planner_called=false
pattern_learning_called=false
```

Additionally:

- no automatic promotion to `CERTO`;
- OCR text is `DA_VERIFICARE` evidence;
- missing fields remain missing;
- ambiguous fields remain ambiguous;
- discrepancies remain explicit;
- unmatched OCR content remains review evidence;
- date labels are not treated as equivalent by OCR heuristics;
- a generic date must not automatically populate `customer_requested_date`;
- OCR confidence must not become production truth.

## Separation from legacy OCR order parsing

`backend/app/ingest/ocr_parser.py` contains aliases and fallback heuristics for order data, including generic date extraction.

That parser is not authorized as the canonical parser for this capability because:

- it produces a single legacy order shape rather than the closed snapshot contract;
- it uses `due_date` terminology;
- it may extract an unlabeled date;
- it does not preserve the full production-program multi-record delimiter contract;
- it is not sufficient evidence that customer-requested, shipment, delivery and internal dates remain distinct.

A future slice may use it only as a read-only comparison fixture or must prove field-by-field that no semantic collapse occurs. Default decision: do not bind it.

## Separation from SMF and writers

`backend/app/ingest/ocr_ingest.py` contains normalization plus SMF write paths.

This capability must not call or import into its runtime path:

- `write_extracted_order_to_smf(...)`;
- `write_extracted_orders_to_smf(...)`;
- `SMFAdapter`;
- discrepancy-sheet writers;
- production-order writers;
- database repositories.

No OCR result may produce an operational write.

## Scope in

This contract covers only:

- one PNG/JPEG image adapter concept;
- local OCR extraction;
- deterministic image identity;
- observed OCR evidence and provenance;
- fail-closed errors;
- handoff to the existing snapshot preview service;
- read-only and no-side-effect guarantees;
- test and stop conditions for a later vertical slice.

## Scope out

Not authorized:

- runtime files;
- tests;
- endpoint or route;
- frontend, PWA, camera or file picker;
- multipart upload;
- PDF;
- TIFF or HEIC;
- Excel or workbook parsing;
- batch or multi-image ingestion;
- image preprocessing or computer vision pipeline;
- cloud OCR;
- real industrial images or fixtures;
- persistence or audit persistence;
- confirmation application;
- source registry changes;
- SMF or database access;
- planner;
- Pattern Learning;
- operator or station assignment;
- modification of `PRODUCTION_PROGRAM_SNAPSHOT_INTAKE_001`;
- modification of article-specification OCR behavior;
- automatic opening of a vertical slice.

## Acceptance criteria for this contract

1. The capability is separate from the closed structured-text capability.
2. Only PNG and JPEG are in the conceptual input boundary.
3. OCR is local and explicitly enabled.
4. Image identity is deterministic and domain-specific.
5. OCR text and provenance are retained as review evidence.
6. The existing snapshot preview service remains the semantic target.
7. Article-specification parser and result types are not treated as production-program contracts.
8. Legacy `ocr_parser.py` is not authorized as the default parser.
9. SMF and all writers are excluded.
10. Missing fields, ambiguities, discrepancies and unmatched content remain explicit.
11. Date meanings are not collapsed.
12. TL confirmation remains mandatory.
13. Persistence, writer, planner and Pattern Learning flags remain false.
14. No automatic promotion to `CERTO` occurs.
15. Runtime, endpoint, tests and frontend require a separate preflight and explicit authorization.

## Stop conditions

Stop without workaround if future work requires:

- cloud OCR;
- direct reuse of article-specification parsing semantics;
- direct use of `ocr_parser.py` without proving date and multi-record safety;
- import or invocation of SMF/write paths;
- loss of raw OCR evidence;
- semantic correction of OCR text before preview;
- acceptance of unsupported media by extension alone;
- unbounded OCR execution;
- temporary image retention after execution;
- multiple input formats in one slice;
- frontend, endpoint and OCR runtime implementation in the same unbounded slice;
- real industrial fixtures in repository or cloud tools;
- persistence, planner, Pattern Learning or autonomous decisions;
- modification outside an explicitly approved future allowlist.

## Closure boundary

This document authorizes only the capability contract and its governance boundaries.

It does not authorize runtime implementation, tests, endpoint, frontend, camera access, upload handling, parser reuse, shared-core refactoring, persistence, planner, Pattern Learning or a subsequent capability automatically.
