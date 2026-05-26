from backend.app.services.pattern_learning_registry import (
    find_patterns_by_code,
    find_patterns_by_station,
    list_patterns,
    load_pattern_examples,
)


def test_load_pattern_examples_reads_first_tl_pattern():
    patterns = load_pattern_examples()

    assert patterns
    assert any("ZAW1 / ZAW2 NON INTERCAMBIABILI" in p.title for p in patterns)


def test_list_patterns_returns_public_metadata_only():
    rows = list_patterns()

    assert rows
    assert {"path", "title", "status"} <= set(rows[0].keys())
    assert "content" not in rows[0]


def test_find_patterns_by_station_finds_zaw2_rule():
    matches = find_patterns_by_station("ZAW2")

    assert matches
    assert any("non intercambiabili" in p.content.lower() for p in matches)


def test_find_patterns_by_code_returns_empty_for_unknown_or_unlisted_code():
    matches = find_patterns_by_code("12511")

    assert matches == []
