
"""
Read-only crosscheck BOM payload builder for executor.

Boundary-safe rules:
- uses existing SMF BOM read call-site pattern via HTTP adapter
- no DB access
- no schema mutations
- no ProductionEvent writes
"""

from __future__ import annotations

from typing import Any

from app.atlas_engine.adapters.smf_bom_adapter import SMFBOMAdapter


def _normalize_list(values: Any) -> list[str]:
    if not isinstance(values, list):
        return []
    out = {
        str(value).strip()
        for value in values
        if str(value).strip()
    }
    return sorted(out)


def _extract_expected_from_family(summary: dict[str, Any]) -> dict[str, list[str]]:
    return {
        "components": _normalize_list(
            summary.get("componenti_coinvolti", summary.get("componenti", []))
        ),
        "operations": _normalize_list(
            summary.get("fasi_coinvolte", summary.get("fasi", []))
        ),
    }


def build_expected_from_drawing(
    drawing: str,
    *,
    adapter: SMFBOMAdapter | None = None,
) -> dict[str, Any]:
    read_adapter = adapter or SMFBOMAdapter()
    summary = read_adapter.family_by_drawing(drawing)

    if not summary.get("ok"):
        return {
            "ok": False,
            "scope": "drawing",
            "drawing": drawing,
            "expected": {
                "components": [],
                "operations": [],
            },
            "error": summary.get("error", "family_summary_unavailable"),
        }

    return {
        "ok": True,
        "scope": "drawing",
        "drawing": summary.get("drawing", drawing),
        "normalized_drawing": summary.get("normalized_drawing"),
        "expected": _extract_expected_from_family(summary),
        "source": "SMF_BOM",
    }


def build_crosscheck_payload_for_drawing(
    drawing: str,
    *,
    observed: dict[str, Any] | None = None,
    adapter: SMFBOMAdapter | None = None,
) -> dict[str, Any]:
    expected_payload = build_expected_from_drawing(drawing, adapter=adapter)
    return {
        "expected": expected_payload.get(
            "expected",
            {"components": [], "operations": []},
        ),
        "observed": observed or {},
        "scope": {
            "drawing": expected_payload.get("drawing", drawing),
            "normalized_drawing": expected_payload.get("normalized_drawing"),
            "source": expected_payload.get("source", "SMF_BOM"),
        },
    }


def build_expected_from_code(
    code: str,
    *,
    adapter: SMFBOMAdapter | None = None,
) -> dict[str, Any]:
    """
    Compatibility alias: current domain call-sites resolve BOM family by drawing.
    """
    return build_expected_from_drawing(code, adapter=adapter)
