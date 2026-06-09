#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import urllib.error
import urllib.request


SUPPORTED_PROVIDERS = {
    "ollama",
    "dummy",
    "openai-local",
}


def run_provider(provider: str, model: str, prompt: str, timeout: int = 60) -> str:
    if provider == "dummy":
        return """{
  "verdict": "DA_VERIFICARE",
  "risk": "MEDIUM",
  "summary": "Dummy provider attivo: nessun modello reale interrogato.",
  "suggested_next_command": null,
  "requires_human_confirmation": true
}"""

    if provider == "ollama":
        return run_ollama(model=model, prompt=prompt, timeout=timeout)

    if provider == "openai-local":
        return run_openai_local(model=model, prompt=prompt, timeout=timeout)

    raise ValueError(f"Provider non supportato: {provider}")


def run_ollama(model: str, prompt: str, timeout: int = 60) -> str:
    result = subprocess.run(
        ["ollama", "run", model],
        input=prompt,
        text=True,
        capture_output=True,
        check=False,
        timeout=timeout,
    )

    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "ollama failed")

    return result.stdout.strip()


def run_openai_local(model: str, prompt: str, timeout: int = 60) -> str:
    endpoint = os.environ.get(
        "PROMETEO_OPENAI_LOCAL_URL",
        "http://127.0.0.1:1234/v1/chat/completions",
    )

    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "Rispondi solo con JSON valido. Non eseguire comandi.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        "temperature": 0,
        "stream": False,
    }

    request = urllib.request.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8")
    except urllib.error.URLError as exc:
        raise RuntimeError(f"openai-local request failed: {exc}") from exc

    try:
        data = json.loads(raw)
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"openai-local invalid response shape: {exc}") from exc
