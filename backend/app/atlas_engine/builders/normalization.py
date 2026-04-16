from __future__ import annotations


def normalize_station(s: str | None) -> str | None:
    if not s:
        return s
    return s.replace("_", "-").upper()

