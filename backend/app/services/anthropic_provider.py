from __future__ import annotations

import os

import requests

ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"

DEFAULT_SYSTEM = """
Sei il motore operativo PROMETEO per reparti produttivi.
Rispondi sempre in italiano.
Rispondi in modo sintetico, diretto, operativo.
Niente introduzioni, niente emoji, niente tono consulenziale.
Se l'input descrive un evento operativo, restituisci solo:
AZIONE_TL: ...
MOTIVO: ...
PRIORITA: ...
Usa PRIORITA solo con uno di questi valori:
CRITICA
ALTA
MEDIA
BASSA
""".strip()


def claude_chat(
    prompt: str,
    model: str = "claude-sonnet-4-20250514",
    max_tokens: int = 120,
    temperature: float = 0.1,
    system: str = DEFAULT_SYSTEM,
) -> dict:
    api_key = os.getenv("ANTHROPIC_API_KEY")

    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY non definita")

    payload = {
        "model": model,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "system": system,
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ],
    }

    try:
        response = requests.post(
            ANTHROPIC_URL,
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json=payload,
            timeout=60,
        )
    except requests.RequestException as exc:
        raise RuntimeError(f"Claude API request failed: {exc}") from exc

    if response.status_code != 200:
        raise RuntimeError(f"Claude API error {response.status_code}: {response.text}")

    try:
        data = response.json()
    except ValueError as exc:
        raise RuntimeError("Claude API returned invalid JSON") from exc

    text_parts: list[str] = []
    for item in data.get("content", []):
        if item.get("type") == "text":
            text = item.get("text", "")
            if text:
                text_parts.append(text)

    text = "\n".join(text_parts).strip()
    if not text:
        raise RuntimeError("Claude API returned empty text content")

    return {
        "text": text,
        "usage": data.get("usage", {}),
        "model": data.get("model"),
    }
