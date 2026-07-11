from __future__ import annotations

from pathlib import Path
import subprocess
from types import SimpleNamespace

from app.services import article_specification_tesseract_ocr as tesseract_ocr
from app.services.article_specification_tesseract_ocr import (
    ERROR_TESSERACT_FAILED,
    ERROR_TESSERACT_TIMEOUT,
    TesseractArticleSpecificationOCRAdapter,
    build_article_specification_ocr_adapter,
)


def test_runtime_binding_is_disabled_by_default():
    assert build_article_specification_ocr_adapter(environ={}) is None


def test_runtime_binding_fails_closed_when_tesseract_is_missing():
    adapter = build_article_specification_ocr_adapter(
        environ={tesseract_ocr.PROVIDER_ENV: "tesseract"},
        which=lambda _command: None,
    )

    assert adapter is None


def test_runtime_binding_builds_configured_local_adapter():
    adapter = build_article_specification_ocr_adapter(
        environ={
            tesseract_ocr.PROVIDER_ENV: "tesseract",
            tesseract_ocr.COMMAND_ENV: "custom-tesseract",
            tesseract_ocr.LANGUAGE_ENV: "ita",
            tesseract_ocr.TIMEOUT_ENV: "12.5",
        },
        which=lambda command: f"/usr/local/bin/{command}",
    )

    assert isinstance(adapter, TesseractArticleSpecificationOCRAdapter)
    assert adapter.executable == "/usr/local/bin/custom-tesseract"
    assert adapter.language == "ita"
    assert adapter.timeout_seconds == 12.5


def test_runtime_binding_rejects_invalid_timeout():
    adapter = build_article_specification_ocr_adapter(
        environ={
            tesseract_ocr.PROVIDER_ENV: "tesseract",
            tesseract_ocr.TIMEOUT_ENV: "invalid",
        },
        which=lambda _command: "/opt/homebrew/bin/tesseract",
    )

    assert adapter is None


def test_tesseract_adapter_extracts_text_and_removes_temp_file(monkeypatch):
    observed = {}

    def run_spy(command, **kwargs):
        observed["command"] = command
        observed["kwargs"] = kwargs
        observed["path"] = Path(command[1])
        assert observed["path"].read_bytes() == b"synthetic-image"
        return SimpleNamespace(returncode=0, stdout="ARTICOLO: SYNTH-01\n")

    monkeypatch.setattr(tesseract_ocr.subprocess, "run", run_spy)
    adapter = TesseractArticleSpecificationOCRAdapter(
        executable="/opt/homebrew/bin/tesseract",
        language="ita+eng",
        timeout_seconds=30,
    )

    result = adapter.extract_text(
        b"synthetic-image",
        media_type="image/png",
        source_id="article-spec-image:sha256:test",
    )

    assert result.ok is True
    assert result.text == "ARTICOLO: SYNTH-01\n"
    assert observed["command"][0] == "/opt/homebrew/bin/tesseract"
    assert observed["command"][2:] == ["stdout", "-l", "ita+eng"]
    assert observed["kwargs"]["timeout"] == 30
    assert observed["path"].exists() is False


def test_tesseract_adapter_maps_nonzero_exit_to_governed_error(monkeypatch):
    monkeypatch.setattr(
        tesseract_ocr.subprocess,
        "run",
        lambda *_args, **_kwargs: SimpleNamespace(returncode=1, stdout=""),
    )
    adapter = TesseractArticleSpecificationOCRAdapter(executable="tesseract")

    result = adapter.extract_text(
        b"synthetic-image",
        media_type="image/jpeg",
        source_id="source",
    )

    assert result.ok is False
    assert result.error_code == ERROR_TESSERACT_FAILED


def test_tesseract_adapter_maps_timeout_to_governed_error(monkeypatch):
    def raise_timeout(*_args, **_kwargs):
        raise subprocess.TimeoutExpired(cmd="tesseract", timeout=1)

    monkeypatch.setattr(tesseract_ocr.subprocess, "run", raise_timeout)
    adapter = TesseractArticleSpecificationOCRAdapter(executable="tesseract")

    result = adapter.extract_text(
        b"synthetic-image",
        media_type="image/png",
        source_id="source",
    )

    assert result.ok is False
    assert result.error_code == ERROR_TESSERACT_TIMEOUT
