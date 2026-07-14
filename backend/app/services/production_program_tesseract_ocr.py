from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
from typing import Callable

from app.ingest.production_program_image_ocr_acquisition import OCRTextExtractionResult


ERROR_PRODUCTION_PROGRAM_TESSERACT_FAILED = (
    "PRODUCTION_PROGRAM_TESSERACT_OCR_FAILED"
)
ERROR_PRODUCTION_PROGRAM_TESSERACT_TIMEOUT = (
    "PRODUCTION_PROGRAM_TESSERACT_OCR_TIMEOUT"
)

PROVIDER_ID = "tesseract-local"
PROVIDER_ENV = "PROMETEO_PRODUCTION_PROGRAM_OCR_PROVIDER"
COMMAND_ENV = "PROMETEO_TESSERACT_COMMAND"
LANGUAGE_ENV = "PROMETEO_TESSERACT_LANGUAGE"
TIMEOUT_ENV = "PROMETEO_TESSERACT_TIMEOUT_SECONDS"

_MEDIA_SUFFIX = {
    "image/png": ".png",
    "image/jpeg": ".jpg",
}


@dataclass(frozen=True)
class TesseractProductionProgramOCRAdapter:
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
        suffix = _media_suffix(media_type)
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
                provider=PROVIDER_ID,
                error_code=ERROR_PRODUCTION_PROGRAM_TESSERACT_TIMEOUT,
            )
        except (OSError, ValueError):
            return OCRTextExtractionResult(
                ok=False,
                provider=PROVIDER_ID,
                error_code=ERROR_PRODUCTION_PROGRAM_TESSERACT_FAILED,
            )
        finally:
            if image_path is not None:
                image_path.unlink(missing_ok=True)

        if completed.returncode != 0:
            return OCRTextExtractionResult(
                ok=False,
                provider=PROVIDER_ID,
                error_code=ERROR_PRODUCTION_PROGRAM_TESSERACT_FAILED,
            )

        return OCRTextExtractionResult(
            ok=True,
            provider=PROVIDER_ID,
            text=completed.stdout,
        )


def build_production_program_ocr_adapter(
    *,
    environ: Mapping[str, str] | None = None,
    which: Callable[[str], str | None] = shutil.which,
) -> TesseractProductionProgramOCRAdapter | None:
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

    return TesseractProductionProgramOCRAdapter(
        executable=executable,
        language=language,
        timeout_seconds=timeout_seconds,
    )


def _media_suffix(media_type: str) -> str:
    return _MEDIA_SUFFIX.get(media_type, ".img")
