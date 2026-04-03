from __future__ import annotations

from .base import BaseProvider


class NoOpProvider(BaseProvider):
    async def complete(self, prompt: str) -> str:
        return "LLM disabilitato. Decisione gestita con policy locale PROMETEO."
