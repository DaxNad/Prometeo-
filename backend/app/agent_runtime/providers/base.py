from __future__ import annotations

from abc import ABC, abstractmethod


class BaseProvider(ABC):
    name: str = "base"

    @abstractmethod
    async def complete(self, prompt: str) -> str:
        raise NotImplementedError
