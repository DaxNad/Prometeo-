from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
from typing import Callable

from app.ingest.article_specification_image_acquisition import (
    ArticleSpecificationOCRAdapter,
    OCRTextExtractionResult,
)


ERROR_TESSERACT_FAILED = "TESSERACT_OCR_FAILED"
ERROR_TESSERACT_TIMEOUT = "TESSERACT_OCR_TIMEOUT"

PROVIDER_ENV = "PROMETEO_ARTICLE_SPEC_OCR_PROVIDER"
COMMAND_ENV = "PROMETEO_TESSERACT_COMMAND"
LANGUAGE_ENV = "PROMETEO_TESSERACT_LANGUAGE"
TIMEOUT_ENV = "PROMETEO_TESSERACT_TIMEOUT_SECONDS"

_MEDIA_SUFFIX = {
    "image/png": ".png",
    "image/jpeg": ".jpg",
}


@dataclass(frozen=True)
class TesseractArticleSpecificationOCRAdapter(ArticleSpecificationOCRAdapter):
    executable: str
    language: str = "ita+eng"
    timeout_seconds: float = 30.0

    def extract_text(
        self,
        image_bytes: bytes,
        *,
        media_type: str,
        source_id: str,
    ) -> OCRTextExtractionResult:
        del source_id
        suffix = _MEDIA_SUFFIX.get(media_type, ".img")
        image_path: Path | None = None

        try:
            with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as handle:
                handle.write(image_bytes)
                image_path = Path(handle.name)

            completed = subprocess.run(
                [
                    self.executable,
                    str(image_path),
                    "stdout",
                    "-l",
                    self.language,
                ],
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
                check=False,
            )
        except subprocess.TimeoutExpired:
            return OCRTextExtractionResult(
                ok=False,
                error_code=ERROR_TESSERACT_TIMEOUT,
            )
        except (OSError, ValueError):
            return OCRTextExtractionResult(
                ok=False,
                error_code=ERROR_TESSERACT_FAILED,
            )
        finally:
            if image_path is not None:
                image_path.unlink(missing_ok=True)

        if completed.returncode != 0:
            return OCRTextExtractionResult(
                ok=False,
                error_code=ERROR_TESSERACT_FAILED,
            )

        return OCRTextExtractionResult(ok=True, text=completed.stdout)


def build_article_specification_ocr_adapter(
    *,
    environ: Mapping[str, str] | None = None,
    which: Callable[[str], str | None] = shutil.which,
) -> ArticleSpecificationOCRAdapter | None:
    values = os.environ if environ is None else environ
    provider = values.get(PROVIDER_ENV, "").strip().lower()
    if provider != "tesseract":
        return None

    command = values.get(COMMAND_ENV, "tesseract").strip() or "tesseract"
    executable = which(command)
    if not executable:
        return None

    language = values.get(LANGUAGE_ENV, "ita+eng").strip() or "ita+eng"
    raw_timeout = values.get(TIMEOUT_ENV, "30").strip()
    try:
        timeout_seconds = float(raw_timeout)
    except ValueError:
        return None
    if timeout_seconds <= 0:
        return None

    return TesseractArticleSpecificationOCRAdapter(
        executable=executable,
        language=language,
        timeout_seconds=timeout_seconds,
    )
