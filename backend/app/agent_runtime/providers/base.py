from __future__ import annotations

from abc import ABC, abstractmethod


class BaseProvider(ABC):
    @abstractmethod
    async def complete(self, prompt: str) -> str:
        raise NotImplementedError
