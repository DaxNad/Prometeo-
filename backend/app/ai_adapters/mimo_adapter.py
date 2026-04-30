import os
import json
import urllib.request


class MiMoAdapterError(RuntimeError):
    pass


class MiMoAdapter:
    """
    Adapter isolato per MiMo/OpenAI-compatible API.
    Non modifica dominio PROMETEO.
    Non accede a repo.
    Non esegue patch.
    """

    def __init__(self):
        self.api_key = os.getenv("MIMO_API_KEY")
        self.base_url = os.getenv("MIMO_BASE_URL", "").rstrip("/")
        self.model = os.getenv("MIMO_MODEL", "mimo-v2.5-pro")

    @property
    def enabled(self) -> bool:
        return bool(self.api_key and self.base_url)

    def ask(self, prompt: str, system: str | None = None) -> dict:
        if not self.enabled:
            raise MiMoAdapterError("MiMo adapter non configurato: mancano MIMO_API_KEY o MIMO_BASE_URL")

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.2,
        }

        req = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=60) as res:
                return json.loads(res.read().decode("utf-8"))
        except Exception as exc:
            raise MiMoAdapterError(f"Errore chiamata MiMo: {exc}") from exc
