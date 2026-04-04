from __future__ import annotations

import os

from .providers.atlas import AtlasProvider
from .providers.base import BaseProvider
from .providers.noop import NoOpProvider


def build_runtime_provider() -> BaseProvider:
    provider_name = os.getenv("PROMETEO_RUNTIME_PROVIDER", "noop").strip().lower()

    if provider_name == "atlas":
        return AtlasProvider()

    return NoOpProvider()
