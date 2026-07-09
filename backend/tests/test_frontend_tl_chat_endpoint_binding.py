from pathlib import Path


def test_frontend_tl_chat_uses_canonical_endpoint():
    repo_root = Path(__file__).resolve().parents[2]
    api_client = repo_root / "frontend" / "src" / "lib" / "api" / "prometeo.ts"
    source = api_client.read_text(encoding="utf-8")

    assert 'apiPost<TLChatResponse>("/tl/chat", payload)' in source
    assert 'apiPost<TLChatResponse>("/chat", payload)' not in source
