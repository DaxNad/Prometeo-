from backend.app.api.tl_chat import (
    _response_for_components,
    _response_for_pidmill_dima,
    _response_for_turn_fallback_without_article,
)


def _dump(response):
    return response.model_dump(exclude_none=True)


def test_turn_fallback_without_article_is_normalized_as_missing():
    data = _dump(_response_for_turn_fallback_without_article())

    assert data["source"] == "missing"
    assert data["source_status"] == "SOURCE_MISSING"
    assert data["semantic_status"] == "MANCANTE"
    assert data["missing_data"] == [
        "codice articolo",
        "ordine",
        "lotto",
        "stato board",
        "evento aperto",
    ]


def test_pidmill_missing_dima_keeps_found_metadata_source():
    data = _dump(_response_for_pidmill_dima("50041", {}))

    assert data["source"] == "local_specs_metadata"
    assert data["source_status"] == "SOURCE_FOUND"
    assert data["semantic_status"] == "MANCANTE"
    assert data["missing_data"] == ["dima PIDMILL"]


def test_components_absent_are_normalized_as_missing_data_in_found_source():
    data = _dump(_response_for_components("50041", {}))

    assert data["source"] == "local_specs_metadata"
    assert data["source_status"] == "SOURCE_FOUND"
    assert data["semantic_status"] == "MANCANTE"
    assert data["missing_data"] == ["components"]


def test_components_unreadable_are_da_verificare_not_source_missing():
    data = _dump(
        _response_for_components(
            "50042",
            {"components": ["CRT001", "SUPPORTO"]},
        )
    )

    assert data["source"] == "local_specs_metadata"
    assert data["source_status"] == "SOURCE_FOUND"
    assert data["semantic_status"] == "DA_VERIFICARE"
    assert data["missing_data"] == ["struttura components leggibile"]


def test_available_components_do_not_emit_missing_normalization_fields():
    data = _dump(
        _response_for_components(
            "50043",
            {
                "confidence": "CERTO",
                "components": ["468922"],
            },
        )
    )

    assert data["confidence"] == "CERTO"
    assert "source" not in data
    assert "source_status" not in data
    assert "semantic_status" not in data
    assert "missing_data" not in data
