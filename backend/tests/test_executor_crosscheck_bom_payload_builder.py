from app.executor.payload_builders.crosscheck_bom_payload_builder import (
    build_crosscheck_payload_for_drawing,
    build_expected_from_drawing,
)


class _FakeAdapter:
    def __init__(self, payload):
        self.payload = payload

    def family_by_drawing(self, drawing: str):
        return self.payload


def test_build_expected_from_drawing_uses_family_projection():
    adapter = _FakeAdapter(
        {
            "ok": True,
            "drawing": "DWG-100",
            "normalized_drawing": "DWG-100",
            "componenti": ["C1", " C2 ", "C1", ""],
            "fasi": ["OP10", " OP20 ", "OP10", ""],
        }
    )

    result = build_expected_from_drawing("DWG-100", adapter=adapter)

    assert result["ok"] is True
    assert result["expected"] == {
        "components": ["C1", "C2"],
        "operations": ["OP10", "OP20"],
    }
    assert result["source"] == "SMF_BOM"


def test_build_expected_from_drawing_handles_unavailable_summary():
    adapter = _FakeAdapter(
        {
            "ok": False,
            "error": "http_404",
        }
    )

    result = build_expected_from_drawing("DWG-404", adapter=adapter)

    assert result["ok"] is False
    assert result["expected"] == {"components": [], "operations": []}
    assert result["error"] == "http_404"


def test_build_crosscheck_payload_for_drawing_keeps_observed_external():
    adapter = _FakeAdapter(
        {
            "ok": True,
            "drawing": "DWG-100",
            "normalized_drawing": "DWG-100",
            "componenti": ["C1"],
            "fasi": ["OP10"],
        }
    )

    observed = {"components": ["C1"], "operations": ["OP10", "OP30"]}
    payload = build_crosscheck_payload_for_drawing(
        "DWG-100",
        observed=observed,
        adapter=adapter,
    )

    assert payload["expected"] == {"components": ["C1"], "operations": ["OP10"]}
    assert payload["observed"] == observed
    assert payload["scope"]["drawing"] == "DWG-100"
