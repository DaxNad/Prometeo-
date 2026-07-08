from __future__ import annotations

from enum import Enum
from typing import Any


class AuthorityRole(str, Enum):
    RESPONSABILE_PRODUZIONE = "RESPONSABILE_PRODUZIONE"


ALLOWED_AUTHORITY_ROLES = frozenset(role.value for role in AuthorityRole)


def normalize_authority_role(value: Any) -> str:
    return str(value or "").strip().upper().replace("-", "_").replace(" ", "_")
