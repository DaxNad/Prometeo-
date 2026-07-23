from __future__ import annotations

from dataclasses import FrozenInstanceError
import inspect
from pathlib import Path
import subprocess
from types import SimpleNamespace

import pytest

from app.ingest.production_program_image_ocr_acquisition import (
    ProductionProgramImageOCRStatus,
    acquire_production_program_image_ocr,
)
import app.services.production_program_tesseract_ocr as tesseract_ocr
from app.services.production_program_tesseract_ocr import (
    COMMAND_ENV,
    ERROR_PRODUCTION_PROGRAM_TESSERACT_FAILED,
    ERROR_PRODUCTION_PROGRAM_TESSERACT_TIMEOUT,
    LANGUAGE_ENV,
    PROVIDER_ENV,
    PROVIDER_ID,
    TIMEOUT_ENV,
    TesseractProductionProgramOCRAdapter,
    build_production_program_ocr_adapter,
)


PNG = b"\x89PNG\r\n\x1a\nsynthetic-png"
JPEG = b"\xff\xd8\xffsynthetic-jpeg"
OCR_TEXT = """PERIODO: 2026-W29
ordine: ORD-001
codice: ART-001
qta: 12
data richiesta cliente: 2026-07-20
--- RECORD ---
ordine: ORD-002
codice: ART-002
qta: 8
"""


def _enabled(**overrides: str) -> dict[str, str]:
    values = {PROVIDER_ENV: "tesseract"}
    values.update(overrides)
    return values


def test_provider_disabled_returns_none() -> None:
    assert build_production_program_ocr_adapter(environ={}, which=lambda _: "/bin/tesseract") is None
    assert build_production_program_ocr_adapter(
        environ={PROVIDER_ENV: "cloud"},
        which=lambda _: "/bin/tesseract",
    ) is None


def test_stub_provider_without_explicit_allow_flag_returns_none() -> None:
    assert build_production_program_ocr_adapter(
        environ={PROVIDER_ENV: "stub"},
        which=lambda _: "/bin/tesseract",
    ) is None


@pytest.mark.parametrize(
    "allow_value",
    ["", "false", "FALSE", "0", "yes", "invalid"],
)
def test_stub_provider_with_invalid_allow_flag_returns_none(
    allow_value: str,
) -> None:
    assert build_production_program_ocr_adapter(
        environ={
            PROVIDER_ENV: "stub",
            "PROMETEO_ALLOW_DETERMINISTIC_OCR_STUB": allow_value,
        },
        which=lambda _: "/bin/tesseract",
    ) is None


def test_stub_provider_builds_deterministic_adapter_without_command_discovery() -> None:
    discovered_commands: list[str] = []

    def which(command: str) -> str | None:
        discovered_commands.append(command)
        return "/bin/tesseract"

    adapter = build_production_program_ocr_adapter(
        environ={
            PROVIDER_ENV: "stub",
            "PROMETEO_ALLOW_DETERMINISTIC_OCR_STUB": "true",
        },
        which=which,
    )

    assert adapter is not None
    assert discovered_commands == []

    first = adapter.extract_text(
        PNG,
        media_type="image/png",
        source_id="production-program-image:sha256:first",
    )
    second = adapter.extract_text(
        JPEG,
        media_type="image/jpeg",
        source_id="production-program-image:sha256:second",
    )

    assert first.ok is True
    assert second.ok is True
    assert first.provider == "deterministic-stub"
    assert second.provider == "deterministic-stub"
    assert first.text == second.text
    assert "ordine:" in first.text
    assert "codice:" in first.text
    assert "qta:" in first.text


def test_exact_provider_opt_in_builds_adapter_and_discovers_command() -> None:
    commands: list[str] = []

    def which(command: str) -> str | None:
        commands.append(command)
        return "/opt/local/bin/tesseract"

    adapter = build_production_program_ocr_adapter(
        environ=_enabled(**{COMMAND_ENV: " custom-tesseract "}),
        which=which,
    )

    assert commands == ["custom-tesseract"]
    assert adapter == TesseractProductionProgramOCRAdapter(
        executable="/opt/local/bin/tesseract",
        language="ita+eng",
        timeout_seconds=30.0,
    )


def test_missing_executable_returns_none() -> None:
    assert build_production_program_ocr_adapter(
        environ=_enabled(),
        which=lambda _: None,
    ) is None


def test_configured_language_and_timeout_are_respected() -> None:
    adapter = build_production_program_ocr_adapter(
        environ=_enabled(
            **{
                LANGUAGE_ENV: "eng",
                TIMEOUT_ENV: "12.5",
            }
        ),
        which=lambda _: "/bin/tesseract",
    )

    assert adapter is not None
    assert adapter.language == "eng"
    assert adapter.timeout_seconds == 12.5


@pytest.mark.parametrize("timeout", ["invalid", "0", "-1"])
def test_invalid_non_positive_timeout_returns_none(timeout: str) -> None:
    assert build_production_program_ocr_adapter(
        environ=_enabled(**{TIMEOUT_ENV: timeout}),
        which=lambda _: "/bin/tesseract",
    ) is None


@pytest.mark.parametrize(
    ("image_bytes", "media_type", "suffix"),
    [(PNG, "image/png", ".png"), (JPEG, "image/jpeg", ".jpg")],
)
def test_execution_uses_exact_bytes_suffix_arguments_and_stdout(
    image_bytes: bytes,
    media_type: str,
    suffix: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    observed: dict[str, object] = {}

    def fake_run(args: list[str], **kwargs: object) -> SimpleNamespace:
        image_path = Path(args[1])
        observed["args"] = args
        observed["kwargs"] = kwargs
        observed["suffix"] = image_path.suffix
        observed["bytes"] = image_path.read_bytes()
        observed["path"] = image_path
        return SimpleNamespace(returncode=0, stdout=" OCR output \n", stderr="ignored")

    monkeypatch.setattr(tesseract_ocr.subprocess, "run", fake_run)
    adapter = TesseractProductionProgramOCRAdapter(
        executable="/bin/tesseract",
        language="ita+eng",
        timeout_seconds=9.0,
    )

    result = adapter.extract_text(
        image_bytes,
        media_type=media_type,
        source_id="production-program-image:sha256:test",
    )

    path = observed["path"]
    assert isinstance(path, Path)
    assert observed["suffix"] == suffix
    assert observed["bytes"] == image_bytes
    assert observed["args"] == [
        "/bin/tesseract",
        str(path),
        "stdout",
        "-l",
        "ita+eng",
    ]
    assert observed["kwargs"] == {
        "capture_output": True,
        "text": True,
        "timeout": 9.0,
        "check": False,
    }
    assert result.ok is True
    assert result.provider == PROVIDER_ID
    assert result.text == " OCR output \n"
    assert not path.exists()


def test_timeout_returns_dedicated_error_and_deletes_temp_file(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    observed_path: Path | None = None

    def fake_run(args: list[str], **kwargs: object) -> object:
        nonlocal observed_path
        observed_path = Path(args[1])
        raise subprocess.TimeoutExpired(cmd=args, timeout=kwargs["timeout"])

    monkeypatch.setattr(tesseract_ocr.subprocess, "run", fake_run)
    result = TesseractProductionProgramOCRAdapter("/bin/tesseract").extract_text(
        PNG,
        media_type="image/png",
        source_id="source",
    )

    assert result.ok is False
    assert result.provider == PROVIDER_ID
    assert result.error_code == ERROR_PRODUCTION_PROGRAM_TESSERACT_TIMEOUT
    assert observed_path is not None
    assert not observed_path.exists()


@pytest.mark.parametrize("failure", [OSError("failed"), ValueError("failed")])
def test_os_and_value_failures_return_dedicated_error_and_cleanup(
    failure: Exception,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    observed_path: Path | None = None

    def fake_run(args: list[str], **kwargs: object) -> object:
        nonlocal observed_path
        observed_path = Path(args[1])
        raise failure

    monkeypatch.setattr(tesseract_ocr.subprocess, "run", fake_run)
    result = TesseractProductionProgramOCRAdapter("/bin/tesseract").extract_text(
        PNG,
        media_type="image/png",
        source_id="source",
    )

    assert result.ok is False
    assert result.provider == PROVIDER_ID
    assert result.error_code == ERROR_PRODUCTION_PROGRAM_TESSERACT_FAILED
    assert observed_path is not None
    assert not observed_path.exists()


def test_non_zero_return_code_fails_closed_and_does_not_use_stderr(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    observed_path: Path | None = None

    def fake_run(args: list[str], **kwargs: object) -> SimpleNamespace:
        nonlocal observed_path
        observed_path = Path(args[1])
        return SimpleNamespace(returncode=2, stdout="partial", stderr="secret-error")

    monkeypatch.setattr(tesseract_ocr.subprocess, "run", fake_run)
    result = TesseractProductionProgramOCRAdapter("/bin/tesseract").extract_text(
        JPEG,
        media_type="image/jpeg",
        source_id="source",
    )

    assert result.ok is False
    assert result.provider == PROVIDER_ID
    assert result.text == ""
    assert result.error_code == ERROR_PRODUCTION_PROGRAM_TESSERACT_FAILED
    assert observed_path is not None
    assert not observed_path.exists()


def test_adapter_composes_with_existing_acquisition_boundary(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_run(args: list[str], **kwargs: object) -> SimpleNamespace:
        return SimpleNamespace(returncode=0, stdout=OCR_TEXT, stderr="")

    monkeypatch.setattr(tesseract_ocr.subprocess, "run", fake_run)
    adapter = TesseractProductionProgramOCRAdapter("/bin/tesseract")

    result = acquire_production_program_image_ocr(PNG, ocr_adapter=adapter)

    assert result.ok is True
    assert result.status is ProductionProgramImageOCRStatus.PREVIEW_READY
    assert result.provider == PROVIDER_ID
    assert result.observed_text == OCR_TEXT
    assert result.snapshot_preview is not None
    assert result.snapshot_preview["requires_confirmation"] is True
    assert result.snapshot_preview["persisted"] is False
    assert result.snapshot_preview["writer_called"] is False
    assert result.snapshot_preview["planner_called"] is False
    assert result.snapshot_preview["pattern_learning_called"] is False


def test_adapter_is_immutable_and_has_no_article_domain_import() -> None:
    adapter = TesseractProductionProgramOCRAdapter("/bin/tesseract")
    with pytest.raises(FrozenInstanceError):
        adapter.language = "eng"  # type: ignore[misc]

    source = inspect.getsource(tesseract_ocr)
    assert "article_specification" not in source
    assert "ArticleSpecification" not in source


def test_no_network_is_invoked(monkeypatch: pytest.MonkeyPatch) -> None:
    def forbidden_network(*args: object, **kwargs: object) -> object:
        raise AssertionError("network access is forbidden")

    def fake_run(args: list[str], **kwargs: object) -> SimpleNamespace:
        return SimpleNamespace(returncode=0, stdout=OCR_TEXT, stderr="")

    monkeypatch.setattr("socket.create_connection", forbidden_network)
    monkeypatch.setattr(tesseract_ocr.subprocess, "run", fake_run)

    result = TesseractProductionProgramOCRAdapter("/bin/tesseract").extract_text(
        PNG,
        media_type="image/png",
        source_id="source",
    )
    assert result.ok is True
    assert result.provider == PROVIDER_ID
