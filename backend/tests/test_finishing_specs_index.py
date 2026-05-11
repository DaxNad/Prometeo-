import json

from app.domain.finishing_specs_index import (
    build_finishing_specs_index,
    get_finishing_spec_metadata,
    list_finishing_spec_metadata,
)


def _write_metadata(root, article, payload):
    article_dir = root / article
    article_dir.mkdir(parents=True)
    (article_dir / "metadata.json").write_text(json.dumps(payload), encoding="utf-8")
    return article_dir


def test_finishing_specs_index_marks_authoritative_metadata(tmp_path):
    root = tmp_path / "specs_finitura"
    article_dir = _write_metadata(
        root,
        "12066",
        {
            "schema": "PROMETEO_REAL_DATA_PILOT_V1",
            "article": "12066",
            "confidence": "CERTO",
            "route_status": "CERTO",
            "drawing": "A2145013301",
            "revision": "13",
            "png_file": "12066_A2145013301_rev13.png",
        },
    )
    (article_dir / "12066_A2145013301_rev13.png").write_text("fake image placeholder")

    index = build_finishing_specs_index(root)
    record = index["records"][0]

    assert index["schema"] == "PROMETEO_FINISHING_SPECS_INDEX_V1"
    assert index["records_count"] == 1
    assert index["authoritative_count"] == 1
    assert record["article"] == "12066"
    assert record["status"] == "AUTHORITATIVE_READY"
    assert record["authoritative"] is True
    assert record["has_image"] is True
    assert record["issues"] == []


def test_finishing_specs_index_keeps_partial_metadata_non_authoritative(tmp_path):
    root = tmp_path / "specs_finitura"
    _write_metadata(
        root,
        "12102",
        {
            "article": "12102",
            "confidence": "CERTO",
            "drawing": "A2368305500",
            "revision": "9",
        },
    )

    record = get_finishing_spec_metadata("12102", root)

    assert record is not None
    assert record["article"] == "12102"
    assert record["status"] == "NEEDS_NORMALIZATION"
    assert record["authoritative"] is False
    assert "unsupported_or_missing_schema" in record["issues"]


def test_finishing_specs_index_detects_declared_image_missing(tmp_path):
    root = tmp_path / "specs_finitura"
    _write_metadata(
        root,
        "12055",
        {
            "schema": "PROMETEO_REAL_DATA_PILOT_V1",
            "article": "12055",
            "confidence": "CERTO",
            "route_status": "CERTO",
            "png_file": "missing.png",
        },
    )

    record = get_finishing_spec_metadata("12055", root)

    assert record is not None
    assert record["authoritative"] is True
    assert "declared_image_missing" in record["issues"]


def test_finishing_specs_index_returns_copies(tmp_path):
    root = tmp_path / "specs_finitura"
    _write_metadata(
        root,
        "12063",
        {
            "schema": "PROMETEO_REAL_DATA_PILOT_V1",
            "article": "12063",
            "confidence": "CERTO",
            "route_status": "CERTO",
        },
    )

    records = list_finishing_spec_metadata(root)
    records[0]["article"] = "BROKEN"

    fresh = get_finishing_spec_metadata("12063", root)
    assert fresh is not None
    assert fresh["article"] == "12063"
