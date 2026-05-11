from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
SPECS_ROOT = ROOT / "specs_finitura"

SUPPORTED_IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg"}
AUTHORITATIVE_SCHEMA = "PROMETEO_REAL_DATA_PILOT_V1"


def _clean(value: Any) -> str:
    return str(value or "").strip()


def _relative_path(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _safe_article_from_folder(path: Path) -> str:
    return path.name.strip()


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def _image_files(article_dir: Path) -> list[str]:
    if not article_dir.exists():
        return []

    files = []
    for item in article_dir.iterdir():
        if item.is_file() and item.suffix.lower() in SUPPORTED_IMAGE_SUFFIXES:
            files.append(item.name)

    return sorted(files)


def build_finishing_spec_record(metadata_path: Path) -> dict[str, Any]:
    article_dir = metadata_path.parent
    folder_article = _safe_article_from_folder(article_dir)
    data = _read_json(metadata_path)

    if data is None:
        return {
            "article": folder_article,
            "metadata_path": _relative_path(metadata_path),
            "status": "INVALID_JSON",
            "schema": "",
            "confidence": "DA_VERIFICARE",
            "route_status": "DA_VERIFICARE",
            "authoritative": False,
            "issues": ["invalid_metadata_json"],
            "image_files": _image_files(article_dir),
            "has_image": bool(_image_files(article_dir)),
        }

    article = _clean(data.get("article") or data.get("codice") or folder_article)
    schema = _clean(data.get("schema"))
    confidence = _clean(data.get("confidence")) or "DA_VERIFICARE"
    route_status = _clean(data.get("route_status")) or "DA_VERIFICARE"
    drawing = _clean(data.get("drawing") or data.get("disegno"))
    revision = _clean(data.get("revision") or data.get("rev"))
    png_file = _clean(data.get("png_file"))

    images = _image_files(article_dir)
    issues: list[str] = []

    if article != folder_article:
        issues.append("article_folder_mismatch")

    if schema != AUTHORITATIVE_SCHEMA:
        issues.append("unsupported_or_missing_schema")

    if not confidence:
        issues.append("missing_confidence")

    if not route_status:
        issues.append("missing_route_status")

    if png_file and png_file not in images:
        issues.append("declared_image_missing")

    if images and not png_file:
        issues.append("image_present_but_not_declared")

    authoritative = (
        schema == AUTHORITATIVE_SCHEMA
        and confidence == "CERTO"
        and route_status == "CERTO"
        and "article_folder_mismatch" not in issues
    )

    status = "AUTHORITATIVE_READY" if authoritative else "NEEDS_NORMALIZATION"

    return {
        "article": article,
        "folder_article": folder_article,
        "metadata_path": _relative_path(metadata_path),
        "status": status,
        "schema": schema,
        "confidence": confidence,
        "route_status": route_status,
        "drawing": drawing,
        "revision": revision,
        "png_file": png_file,
        "image_files": images,
        "has_image": bool(images),
        "authoritative": authoritative,
        "source": "SPECIFICA_FINITURA_METADATA",
        "issues": issues,
    }


def build_finishing_specs_index(specs_root: Path | None = None) -> dict[str, Any]:
    root = specs_root or SPECS_ROOT
    records = []

    if root.exists():
        for metadata_path in sorted(root.glob("*/metadata.json")):
            records.append(build_finishing_spec_record(metadata_path))

    by_status: dict[str, int] = {}
    for record in records:
        status = str(record.get("status") or "UNKNOWN")
        by_status[status] = by_status.get(status, 0) + 1

    return {
        "schema": "PROMETEO_FINISHING_SPECS_INDEX_V1",
        "source": "specs_finitura_metadata_read_only",
        "records_count": len(records),
        "authoritative_count": sum(1 for r in records if r.get("authoritative") is True),
        "by_status": by_status,
        "records": records,
    }


def list_finishing_spec_metadata(specs_root: Path | None = None) -> list[dict[str, Any]]:
    return copy.deepcopy(build_finishing_specs_index(specs_root)["records"])


def get_finishing_spec_metadata(article: Any, specs_root: Path | None = None) -> dict[str, Any] | None:
    wanted = _clean(article).upper()
    if not wanted:
        return None

    for record in list_finishing_spec_metadata(specs_root):
        if _clean(record.get("article")).upper() == wanted:
            return copy.deepcopy(record)

    return None
