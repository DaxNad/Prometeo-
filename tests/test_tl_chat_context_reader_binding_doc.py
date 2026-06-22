from pathlib import Path


DOC_PATH = Path("docs/PROMETEO_TL_CHAT_CONTEXT_READER_BINDING_001.md")


def test_tl_chat_context_reader_binding_exists():
    assert DOC_PATH.exists()


def test_tl_chat_context_reader_binding_declares_scope():
    text = DOC_PATH.read_text(encoding="utf-8")

    assert "TL Chat Context Resolver" in text
    assert "ContextSourceReaderAdapter" in text
    assert "source_id logico" in text
    assert "memory/context_source_index.json" in text


def test_tl_chat_context_reader_binding_blocks_direct_paths():
    text = DOC_PATH.read_text(encoding="utf-8")

    assert "path diretti" in text
    assert "path relativi" in text
    assert "path assoluti" in text
    assert "richieste libere a file system" in text


def test_tl_chat_context_reader_binding_preserves_readonly_governance():
    text = DOC_PATH.read_text(encoding="utf-8")

    assert "access_mode = read_only" in text
    assert "metadata sicuri" in text
    assert "excerpt limitato" in text
    assert "codice errore governato" in text


def test_tl_chat_context_reader_binding_blocks_promotion_to_fact():
    text = DOC_PATH.read_text(encoding="utf-8")

    assert "non promuove excerpt a dato certo" in text
    assert "dato certo" in text
    assert "necessita di verifica TL" in text


def test_tl_chat_context_reader_binding_does_not_enable_operational_integration():
    text = DOC_PATH.read_text(encoding="utf-8")

    assert "non collega ancora il resolver all'adapter" in text
    assert "non implementare ancora il collegamento operativo" in text
    assert "non cambiare comportamento della TL Chat" in text
