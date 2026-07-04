from __future__ import annotations

from typing import Any


def _clean(value: Any) -> str:
    return str(value or "").strip()


def _component_code(item: dict[str, Any]) -> str:
    return _clean(
        item.get("component")
        or item.get("code")
        or item.get("codice")
        or item.get("component_code")
        or item.get("codice_componente")
    )


def _has_manicotto_classification(*values: Any) -> bool:
    return any("manicotto" in _clean(value).lower() for value in values)


def find_explicit_manicotto_component(
    metadata: dict[str, Any],
    component_codes: list[str],
) -> str | None:
    candidates = {_clean(code).upper(): _clean(code) for code in component_codes if _clean(code)}

    part_of = metadata.get("part_of") if isinstance(metadata.get("part_of"), dict) else {}
    related_component = _clean(part_of.get("related_component"))
    if (
        related_component
        and related_component.upper() in candidates
        and _has_manicotto_classification(
            part_of.get("relationship"),
            part_of.get("role"),
            part_of.get("type"),
            part_of.get("description"),
        )
    ):
        return candidates[related_component.upper()]

    for item in metadata.get("linked_bom") or []:
        if not isinstance(item, dict):
            continue

        code = _component_code(item)
        if code.upper() not in candidates:
            continue

        if _has_manicotto_classification(
            item.get("description"),
            item.get("role"),
            item.get("ruolo"),
            item.get("type"),
            item.get("tipo"),
            item.get("classification"),
            item.get("relationship"),
        ):
            return candidates[code.upper()]

    for item in metadata.get("components") or []:
        if not isinstance(item, dict):
            continue

        code = _component_code(item)
        if code.upper() not in candidates:
            continue

        if _has_manicotto_classification(
            item.get("description"),
            item.get("role"),
            item.get("ruolo"),
            item.get("type"),
            item.get("tipo"),
            item.get("classification"),
            item.get("relationship"),
        ):
            return candidates[code.upper()]

    return None
