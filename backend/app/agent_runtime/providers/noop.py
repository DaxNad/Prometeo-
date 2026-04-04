from __future__ import annotations

from .base import BaseProvider


class NoOpProvider(BaseProvider):
    name = "noop"

    async def complete(self, prompt: str) -> str:
        return "LLM disabilitato. Decisione gestita con policy locale PROMETEO."
