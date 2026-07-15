from pathlib import Path


def test_frontend_tl_chat_uses_canonical_endpoint():
    repo_root = Path(__file__).resolve().parents[2]
    api_client = repo_root / "frontend" / "src" / "lib" / "api" / "prometeo.ts"
    source = api_client.read_text(encoding="utf-8")

    assert 'apiPost<TLChatResponse>("/tl/chat", payload)' in source
    assert 'apiPost<TLChatResponse>("/chat", payload)' not in source


def test_frontend_vite_proxy_loads_local_api_key_for_tl_chat():
    repo_root = Path(__file__).resolve().parents[2]
    vite_config = repo_root / "frontend" / "vite.config.ts"
    source = vite_config.read_text(encoding="utf-8")

    assert "loadEnv" in source
    assert "env.VITE_PROMETEO_API_KEY" in source
    assert 'proxy.on("proxyReq", (proxyReq) => {' in source
    assert "proxyReq.removeHeader" not in source
    assert 'proxyReq.setHeader("x-api-key", apiKey)' in source
