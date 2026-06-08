#!/usr/bin/env python3
from __future__ import annotations

import subprocess


SUPPORTED_PROVIDERS = {
    "ollama",
    "dummy",
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
