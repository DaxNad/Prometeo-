# PRODUCTION_PROGRAM_IMAGE_OCR_INTAKE_VERTICAL_SLICE_002

## Status

- `STATUS`: `AUTHORIZED`
- `MODE`: `LOCAL_ONLY / READ_ONLY / PREVIEW_FIRST`
- `CAPABILITY`: `PRODUCTION_PROGRAM_IMAGE_OCR_INTAKE_001`
- `SLICE`: `VERTICAL_SLICE_002`
- `DELIVERY`: `PRODUCTION_PROGRAM_TESSERACT_OCR_ADAPTER`
- `RUNTIME_IMPLEMENTATION`: `AUTHORIZED_WITHIN_ALLOWLIST_ONLY`
- `AUTHORITY`: explicit human decision on 2026-07-14

## Purpose

Authorize the smallest runtime path that closes the single residual capability requirement:

```text
validated PNG/JPEG bytes
→ production-program-specific local Tesseract adapter
→ OCRTextExtractionResult from the existing production-program acquisition boundary
→ existing acquire_production_program_image_ocr(...)
→ canonical read-only snapshot preview
```

This slice introduces no endpoint, frontend, upload transport, persistence or semantic parser.

## Read-only mapping decision

The existing runner:

```text
backend/app/services/article_specification_tesseract_ocr.py
```

provides a proven technical pattern for:

- explicit provider opt-in;
- executable discovery;
- positive configurable timeout;
- PNG/JPEG temporary-file suffix selection;
- local `subprocess.run(...)` execution;
- stdout capture;
- fail-closed timeout and command errors;
- unconditional temporary-file cleanup.

Direct reuse by import or composition is not authorized because that module is bound to:

- `ArticleSpecificationOCRAdapter`;
- the article-specific `OCRTextExtractionResult`;
- article-specific provider configuration;
- the article-specification capability namespace.

The selected decision is therefore: reuse the verified execution pattern, not the article-domain runtime object.

## Exact allowlist

```text
backend/app/services/production_program_tesseract_ocr.py
backend/tests/test_production_program_tesseract_ocr.py
```

No third file may change.

The following existing files must remain unchanged:

```text
backend/app/services/article_specification_tesseract_ocr.py
backend/app/ingest/production_program_image_ocr_acquisition.py
backend/app/services/production_program_snapshot_preview.py
```

## Required runtime contract

The new module may define only:

- one immutable Tesseract adapter implementing the existing `ProductionProgramOCRAdapter` protocol structurally;
- one builder that returns the adapter or `None` from explicit configuration;
- production-program-specific constants and error codes;
- private helpers limited to configuration validation and media suffix selection.

The adapter must import and return:

```text
OCRTextExtractionResult
```

from:

```text
app.ingest.production_program_image_ocr_acquisition
```

It must not import article-specification protocols, result types, builders or adapters.

## Configuration contract

Use a production-program-specific provider variable:

```text
PROMETEO_PRODUCTION_PROGRAM_OCR_PROVIDER
```

Allowed active value:

```text
tesseract
```

When absent, blank or different, the builder returns `None`.

Reuse the already established shared technical settings:

```text
PROMETEO_TESSERACT_COMMAND
PROMETEO_TESSERACT_LANGUAGE
PROMETEO_TESSERACT_TIMEOUT_SECONDS
```

Defaults:

```text
command: tesseract
language: ita+eng
timeout_seconds: 30
```

The builder must return `None` when:

- provider is not exactly `tesseract` after trim and lowercase;
- executable discovery fails;
- timeout is not numeric;
- timeout is zero or negative.

No silent provider fallback is allowed.

## Execution contract

For each extraction:

1. select `.png` for `image/png` and `.jpg` for `image/jpeg`;
2. create one temporary file;
3. write the exact image bytes;
4. execute:

```text
<executable> <temporary-image> stdout -l <language>
```

5. use `capture_output=True`, `text=True`, `check=False` and the configured timeout;
6. delete the temporary file in every success, failure and timeout path;
7. return observed stdout unchanged on success;
8. never call network or cloud services.

Required provider identifier on every result:

```text
tesseract-local
```

Required production-program-specific errors:

```text
PRODUCTION_PROGRAM_TESSERACT_OCR_FAILED
PRODUCTION_PROGRAM_TESSERACT_OCR_TIMEOUT
```

A non-zero return code is failure. `stderr` must not be promoted to observed OCR text.

## Composition boundary

The new adapter is consumed through the already delivered function:

```text
acquire_production_program_image_ocr(image_bytes, ocr_adapter=adapter)
```

This slice must not modify that function or add a new orchestration layer.

The Tesseract adapter performs evidence extraction only. It must not:

- parse production-program fields;
- insert record delimiters;
- correct OCR text;
- infer date meaning;
- call the snapshot service directly;
- alter confirmation or side-effect flags.

## Focused tests

The test file must prove:

1. provider disabled returns `None`;
2. exact provider opt-in builds the adapter;
3. command discovery receives the configured command;
4. missing executable returns `None`;
5. default and configured language are respected;
6. default and configured timeout are respected;
7. invalid, zero and negative timeouts return `None`;
8. PNG and JPEG receive the correct temporary suffix;
9. exact command arguments are used;
10. exact bytes are written;
11. stdout is preserved unchanged;
12. provider is always `tesseract-local`;
13. timeout returns the dedicated timeout error;
14. OS/value failures return the dedicated failure error;
15. non-zero return code returns failure;
16. temporary files are deleted after success, timeout and failure;
17. the adapter result is accepted by `acquire_production_program_image_ocr(...)`;
18. the resulting snapshot preserves confirmation and zero-side-effect invariants;
19. no article-specification OCR type or runtime is imported or invoked;
20. no network, SMF, database, writer, planner or Pattern Learning component is invoked.

All tests must use synthetic bytes and monkeypatched subprocess/filesystem boundaries. No real industrial image and no dependency on an installed Tesseract executable is allowed in repository CI.

## Acceptance criteria

1. Exactly the two allowlisted files change.
2. The article-specification runner remains unchanged.
3. The production-program acquisition and snapshot services remain unchanged.
4. The adapter is local-only and explicitly enabled.
5. The provider namespace is production-program-specific.
6. Shared Tesseract command, language and timeout settings are reused without changing existing behavior.
7. Executable availability is verified before activation.
8. Timeout is positive and bounded.
9. Temporary files are always removed.
10. Stdout is preserved as observed evidence.
11. Failures remain fail-closed with dedicated errors.
12. The adapter composes with the existing production-program boundary.
13. No semantic field interpretation occurs in the adapter.
14. No cloud, endpoint, frontend or persistence is introduced.
15. Focused tests and repository guards pass.

## Scope out

Not authorized:

- modification or import-based reuse of the article-specification Tesseract adapter;
- shared OCR-core refactoring;
- endpoint, route or API model;
- Base64, multipart, path input or upload;
- frontend, camera or file picker;
- image preprocessing;
- PDF, TIFF, HEIC, Excel or multiple images;
- real industrial fixtures;
- cloud OCR;
- persistence, audit persistence, SMF or database access;
- confirmation application;
- planner, Pattern Learning or autonomous decisions;
- modification of the closed snapshot capability;
- capability closure documentation;
- automatic authorization of another slice.

## Stop conditions

Stop without workaround if implementation requires:

- a third file;
- modification of article-specification OCR behavior;
- shared-core refactoring;
- semantic correction or parsing inside the adapter;
- network or cloud execution;
- real production images in repository or cloud tools;
- endpoint/frontend work;
- persistence, writer, planner or Pattern Learning access.

## Closure boundary

This document authorizes only `VERTICAL_SLICE_002` within the exact two-file allowlist. It does not close the capability and does not authorize an endpoint, frontend, upload transport or following slice.