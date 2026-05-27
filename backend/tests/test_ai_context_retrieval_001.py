from backend.app.atlas_engine.context_retrieval import build_context_pack


def test_context_pack_retrieves_zaw_non_interchangeable_rule():
    pack = build_context_pack("ZAW1 e ZAW2 sono intercambiabili?")

    assert pack["confidence"] == "PREVIEW_ONLY"
    assert "no planner mutation" in pack["constraints"]
    assert "no DB writes" in pack["constraints"]
    assert "no SMF writes" in pack["constraints"]

    text = "\n".join(chunk["text"] for chunk in pack["chunks"])

    assert "ZAW-1 e ZAW-2 non sono intercambiabili" in text
    assert any(
        source.endswith("#zaw_non_interchangeable")
        for source in pack["sources"]
    )


def test_context_pack_is_empty_for_blank_question():
    pack = build_context_pack("   ")

    assert pack["question"] == ""
    assert pack["confidence"] == "PREVIEW_ONLY"
    assert pack["sources"] == []
    assert pack["chunks"] == []
