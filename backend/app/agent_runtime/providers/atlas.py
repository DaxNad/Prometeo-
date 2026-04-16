from __future__ import annotations

import os

from .base import BaseProvider


class AtlasProvider(BaseProvider):
    """Soft advisory provider for explainability/tie-break support only.

    This provider is explicitly non-authoritative for sequencing decisions.
    """
    name = "atlas"

    def __init__(self) -> None:
        self.model_name = os.getenv("PROMETEO_ATLAS_MODEL", "atlas-disabled")

    async def complete(self, prompt: str) -> str:
        return (
            "ATLAS advisor attivo in modalità placeholder. "
            f"Model={self.model_name}. "
            "Escalation confermata dal layer deterministico PROMETEO. "
            "Usare questo output come spiegazione opzionale, non come decisione primaria."
        )
