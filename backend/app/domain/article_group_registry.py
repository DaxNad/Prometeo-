from __future__ import annotations

import copy
from typing import Any

RAGNETTO_12074_12078 = {
    "group_id": "ragnetto_12074_12078",
    "group_type": "ASSEMBLY_GROUP",
    "label": "Ragnetto 12074-12078",
    "members": ["12074", "12075", "12076", "12077", "12078"],
    "source": "TL",
    "status": "DA_MODELLARE",
    "confidence": "CERTO",
    "planner_policy": "GROUP_DEPENDENCY_NOT_INDEPENDENT",
    "notes": [
        "Gruppo/aggregato indicato dal TL.",
        "I membri non devono essere trattati come singoli standard indipendenti finché il gruppo non è strutturato.",
        "Route e dipendenze operative del gruppo da modellare con specifica/TL.",
    ],
}

_GROUPS = {
    RAGNETTO_12074_12078["group_id"]: RAGNETTO_12074_12078,
}

_MEMBER_TO_GROUP = {
    member: group_id
    for group_id, group in _GROUPS.items()
    for member in group["members"]
}


def normalize_article_code(value: Any) -> str:
    return str(value or "").strip().upper()


def get_article_group(article_code: Any) -> dict[str, Any] | None:
    article = normalize_article_code(article_code)
    if not article:
        return None

    group_id = _MEMBER_TO_GROUP.get(article)
    if not group_id:
        return None

    return copy.deepcopy(_GROUPS[group_id])


def is_group_dependent_article(article_code: Any) -> bool:
    return get_article_group(article_code) is not None


def list_article_groups() -> list[dict[str, Any]]:
    return [copy.deepcopy(group) for group in _GROUPS.values()]
