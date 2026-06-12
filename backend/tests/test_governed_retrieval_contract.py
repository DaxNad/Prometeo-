from backend.app.atlas_engine.governed_retrieval import build_governed_retrieval_pack


def test_blank_question_returns_controlled_empty_pack():
    pack = build_governed_retrieval_pack("   ")
    assert pack["mode"] == "GOVERNED_RETRIEVAL_001"
    assert pack["question"] == ""
    assert pack["evidence"] == []
    assert "read-only" in pack["constraints"]
    assert "local-only" in pack["constraints"]
    assert "no LLM calls" in pack["constraints"]
    assert "no DB writes" in pack["constraints"]
    assert "no SMF writes" in pack["constraints"]


def test_zaw_question_returns_governed_evidence():
    pack = build_governed_retrieval_pack("ZAW1 e ZAW2 sono intercambiabili?", limit=5)
    assert pack["mode"] == "GOVERNED_RETRIEVAL_001"
    assert pack["evidence"]
    joined = " ".join(item["text"] for item in pack["evidence"])
    assert "ZAW" in joined.upper()


def test_every_evidence_item_has_required_contract_fields():
    pack = build_governed_retrieval_pack("ZAW1 e ZAW2 sono intercambiabili?", limit=5)
    required = {"source_id", "source_type", "authority_rank", "confidence", "text", "reason"}
    assert pack["evidence"]
    for item in pack["evidence"]:
        assert required <= set(item)
        assert item["confidence"] in {"CERTO", "INFERITO", "DA_VERIFICARE", "PREVIEW_ONLY"}
        assert isinstance(item["authority_rank"], int)
        assert item["source_id"]
        assert item["source_type"]
        assert item["text"]
        assert item["reason"]


def test_pack_declares_allowed_and_blocked_sources():
    pack = build_governed_retrieval_pack("retrieval fonti autorizzate")
    assert "tl_memory_rules" in pack["allowed_sources"]
    assert "docs/prometeo_system_map.md" in pack["allowed_sources"]
    assert "specs_finitura_images" in pack["blocked_sources"]
    assert "real_smf" in pack["blocked_sources"]
    assert "secrets" in pack["blocked_sources"]


def test_governed_retrieval_does_not_import_tl_chat_runtime():
    import sys
    sys.modules.pop("backend.app.api.tl_chat", None)
    build_governed_retrieval_pack("ZAW1 ZAW2")
    assert "backend.app.api.tl_chat" not in sys.modules

def test_system_map_evidence_is_not_dropped_by_limit():
    pack = build_governed_retrieval_pack(
        "ZAW1 ZAW2 planner retrieval fonti autorizzate",
        limit=5,
    )

    assert pack["mode"] == "GOVERNED_RETRIEVAL_001"
    assert any(
        item["source_type"] == "system_map"
        and item["source_id"] == "docs/prometeo_system_map.md"
        for item in pack["evidence"]
    )

def test_zero_limit_keeps_evidence_empty():
    pack = build_governed_retrieval_pack(
        "ZAW1 ZAW2 planner retrieval fonti autorizzate",
        limit=0,
    )

    assert pack["mode"] == "GOVERNED_RETRIEVAL_001"
    assert pack["evidence"] == []


def test_confidence_question_uses_semantic_registry_confidence_source():
    pack = build_governed_retrieval_pack(
        "Spiegami confidence CERTO INFERITO DA_VERIFICARE",
        limit=5,
    )

    assert any(
        item["source_type"] == "semantic_registry_confidence"
        and item["source_id"] == "semantic_registry_confidence:CERTO"
        for item in pack["evidence"]
    )

    joined = " ".join(item["text"] for item in pack["evidence"])
    assert "CERTO" in joined
    assert "INFERITO" in joined
    assert "DA_VERIFICARE" in joined


def test_semantic_registry_confidence_is_preview_only_evidence():
    pack = build_governed_retrieval_pack("confidence CERTO", limit=3)

    semantic_items = [
        item for item in pack["evidence"]
        if item["source_type"] == "semantic_registry_confidence"
    ]

    assert semantic_items
    assert all(item["confidence"] == "PREVIEW_ONLY" for item in semantic_items)
    assert all(item["authority_rank"] == 15 for item in semantic_items)
