from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "build_documentation_catalog.py"


def _load_catalog_module():
    spec = importlib.util.spec_from_file_location("build_documentation_catalog", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize(
    ("path", "expected_lifecycle"),
    [
        ("docs/PROMETEO_PORTABLE_WORK_METHOD_001.md", "ACTIVE"),
        (
            "docs/capabilities/PRODUCTION_PROGRAM_IMAGE_OCR_UI_INTAKE_VERTICAL_SLICE_001.md",
            "ARCHIVED",
        ),
        (
            "docs/capabilities/TL_CHAT_PRODUCTION_SPEC_SUMMARY_001.md",
            "ARCHIVED",
        ),
        (
            "docs/capabilities/TL_CHAT_UNIFIED_DATA_ACCESS_001.md",
            "ARCHIVED",
        ),
        (
            "docs/capabilities/TL_CHAT_UNIFIED_DATA_ACCESS_VERTICAL_SLICE_002.md",
            "ARCHIVED",
        ),
        (
            "docs/capabilities/TL_CHAT_UNIFIED_DATA_ACCESS_VERTICAL_SLICE_003.md",
            "ARCHIVED",
        ),
        (
            "docs/capabilities/TL_CHAT_UNIFIED_DATA_ACCESS_VERTICAL_SLICE_004.md",
            "ARCHIVED",
        ),
    ],
)
def test_document_lifecycle_matches_verified_status(path, expected_lifecycle):
    catalog = _load_catalog_module()

    actual_lifecycle, _replacement = catalog.lifecycle(path)

    assert actual_lifecycle == expected_lifecycle


@pytest.mark.parametrize(
    ("path", "expected_category"),
    [
        (
            "docs/capabilities/PRODUCTION_PROGRAM_IMAGE_OCR_UI_INTAKE_VERTICAL_SLICE_001.md",
            "EVIDENCE",
        ),
        (
            "docs/capabilities/TL_CHAT_PRODUCTION_SPEC_SUMMARY_001.md",
            "EVIDENCE",
        ),
        (
            "docs/capabilities/TL_CHAT_UNIFIED_DATA_ACCESS_001.md",
            "EVIDENCE",
        ),
        (
            "docs/capabilities/TL_CHAT_UNIFIED_DATA_ACCESS_VERTICAL_SLICE_002.md",
            "EVIDENCE",
        ),
        (
            "docs/capabilities/TL_CHAT_UNIFIED_DATA_ACCESS_VERTICAL_SLICE_003.md",
            "EVIDENCE",
        ),
        (
            "docs/capabilities/TL_CHAT_UNIFIED_DATA_ACCESS_VERTICAL_SLICE_004.md",
            "EVIDENCE",
        ),
        (
            "docs/capabilities/PRODUCTION_PROGRAM_IMAGE_OCR_API_INTAKE_001.md",
            "CONTRACT",
        ),
        (
            "docs/capabilities/PRODUCTION_PROGRAM_IMAGE_OCR_INTAKE_001.md",
            "CONTRACT",
        ),
        (
            "docs/capabilities/PRODUCTION_PROGRAM_IMAGE_OCR_UI_INTAKE_001.md",
            "CONTRACT",
        ),
    ],
)
def test_document_category_matches_verified_role(path, expected_category):
    catalog = _load_catalog_module()

    assert catalog.function(path) == expected_category
