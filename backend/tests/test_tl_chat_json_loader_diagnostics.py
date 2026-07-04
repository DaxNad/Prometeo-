import json
from pathlib import Path
from typing import Any, Callable

import pytest

from app.api import tl_chat as tl_chat_api


def _setup_path_loader(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    path_attr: str,
    filename: str,
) -> Path:
    path = tmp_path / filename
    monkeypatch.setattr(tl_chat_api, path_attr, path)
    return path


def _setup_local_specs_loader(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    _: str,
    filename: str,
) -> Path:
    root = tmp_path / "specs_finitura"
    path = root / "12514" / filename
    monkeypatch.setattr(tl_chat_api, "SPECS_ROOT", root)
    return path


def _setup_spec_intake_loader(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    _: str,
    filename: str,
) -> Path:
    root = tmp_path / "spec_intake_preview"
    path = root / filename
    monkeypatch.setattr(tl_chat_api, "SPEC_INTAKE_PREVIEW_ROOT", root)
    return path


LOADER_CASES: tuple[
    tuple[
        str,
        Callable[[pytest.MonkeyPatch, Path, str, str], Path],
        str,
        str,
        Callable[[], Any],
        Any,
    ],
    ...,
] = (
    (
        "lifecycle_registry",
        _setup_path_loader,
        "LIFECYCLE_REGISTRY",
        "article_lifecycle_registry.json",
        tl_chat_api._load_lifecycle_registry,
        {},
    ),
    (
        "family_registry",
        _setup_path_loader,
        "FAMILY_REGISTRY",
        "prometeo_famiglie.json",
        tl_chat_api._load_family_registry,
        {},
    ),
    (
        "local_specs_metadata",
        _setup_local_specs_loader,
        "",
        "metadata.json",
        lambda: tl_chat_api._load_local_specs_metadata("12514"),
        None,
    ),
    (
        "codici_staging_preview",
        _setup_path_loader,
        "CODICI_STAGING_PREVIEW",
        "codici_staging_preview.json",
        tl_chat_api._load_codici_staging_preview,
        {},
    ),
    (
        "tl_real_spec_intake",
        _setup_path_loader,
        "TL_REAL_SPEC_INTAKE",
        "TL_REAL_SPEC_INTAKE_001.json",
        tl_chat_api._load_tl_real_spec_intake,
        {},
    ),
    (
        "spec_intake_preview",
        _setup_spec_intake_loader,
        "",
        "12514_metadata_preview.json",
        lambda: tl_chat_api._load_spec_intake_preview("12514"),
        None,
    ),
    (
        "article_route_matrix_preview",
        _setup_path_loader,
        "ARTICLE_ROUTE_MATRIX_PREVIEW",
        "article_route_matrix.preview.json",
        tl_chat_api._load_article_route_matrix_preview,
        {},
    ),
)


@pytest.mark.parametrize(
    "source_name,setup,path_attr,filename,loader,fallback",
    LOADER_CASES,
)
def test_tl_chat_json_loader_missing_keeps_existing_fallback(
    monkeypatch,
    tmp_path,
    source_name,
    setup,
    path_attr,
    filename,
    loader,
    fallback,
):
    setup(monkeypatch, tmp_path, path_attr, filename)

    assert loader() == fallback
    assert tl_chat_api._get_json_loader_status(source_name) == tl_chat_api.SOURCE_MISSING


@pytest.mark.parametrize(
    "source_name,setup,path_attr,filename,loader,fallback",
    LOADER_CASES,
)
def test_tl_chat_json_loader_malformed_json_is_invalid(
    monkeypatch,
    tmp_path,
    source_name,
    setup,
    path_attr,
    filename,
    loader,
    fallback,
):
    path = setup(monkeypatch, tmp_path, path_attr, filename)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("{bad", encoding="utf-8")

    assert loader() == fallback
    assert tl_chat_api._get_json_loader_status(source_name) == tl_chat_api.SOURCE_INVALID


@pytest.mark.parametrize(
    "source_name,setup,path_attr,filename,loader,fallback",
    LOADER_CASES,
)
def test_tl_chat_json_loader_unreadable_source_is_distinct(
    monkeypatch,
    tmp_path,
    source_name,
    setup,
    path_attr,
    filename,
    loader,
    fallback,
):
    path = setup(monkeypatch, tmp_path, path_attr, filename)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("{}", encoding="utf-8")
    original_read_text = Path.read_text

    def unreadable(self: Path, *args: Any, **kwargs: Any) -> str:
        if self == path:
            raise PermissionError("blocked for test")
        return original_read_text(self, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", unreadable)

    assert loader() == fallback
    assert tl_chat_api._get_json_loader_status(source_name) == tl_chat_api.SOURCE_UNREADABLE


@pytest.mark.parametrize(
    "source_name,setup,path_attr,filename,loader,fallback",
    LOADER_CASES,
)
def test_tl_chat_json_loader_unexpected_structure_is_invalid(
    monkeypatch,
    tmp_path,
    source_name,
    setup,
    path_attr,
    filename,
    loader,
    fallback,
):
    path = setup(monkeypatch, tmp_path, path_attr, filename)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(["unexpected"]), encoding="utf-8")

    assert loader() == fallback
    assert tl_chat_api._get_json_loader_status(source_name) == tl_chat_api.SOURCE_INVALID
