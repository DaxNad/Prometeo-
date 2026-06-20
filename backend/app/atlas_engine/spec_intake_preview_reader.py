from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


SOURCE_ID = "spec_intake_preview"
SOURCE_FOUND = "SOURCE_FOUND"
SOURCE_MISSING = "SOURCE_MISSING"
SOURCE_FORBIDDEN = "SOURCE_FORBIDDEN"
PATH_TRAVERSAL_BLOCKED = "PATH_TRAVERSAL_BLOCKED"

ARTICLE_RE = re.compile(r"^\d{5}[A-Z]{0,3}$")


def read_spec_intake_preview(
    *,
    article: str | None,
    source_id: str = SOURCE_ID,
    root: Path,
) -> dict[str, Any]:
    """
    Read-only spec_intake_preview reader adapter.

    Contract:
    - local-only
    - read-only
    - preview-only
    - no LLM calls
    - no DB writes
    - no SMF writes
    - no planner mutation
    - no runtime mutation
    - no image access
    """

    if source_id != SOURCE_ID:
        return {
            "source_id": source_id,
            "source_status": SOURCE_FORBIDDEN,
            "article": str(article or "").strip().upper(),
            "excerpt": "",
            "confidence": "DA_VERIFICARE",
            "requires_tl_confirmation": True,
            "planner_eligible": False,
            "limitation": "source identifier is not authorized for this reader",
        }

    safe_article = str(article or "").strip().upper()

    if not safe_article or not ARTICLE_RE.fullmatch(safe_article):
        return {
            "source_id": SOURCE_ID,
            "source_status": PATH_TRAVERSAL_BLOCKED,
            "article": safe_article,
            "excerpt": "",
            "confidence": "DA_VERIFICARE",
            "requires_tl_confirmation": True,
            "planner_eligible": False,
            "limitation": "article identifier rejected by safe article policy",
        }

    base = Path(root).resolve()
    target = (base / f"{safe_article}_metadata_preview.json").resolve()

    if base not in target.parents:
        return {
            "source_id": SOURCE_ID,
            "source_status": PATH_TRAVERSAL_BLOCKED,
            "article": safe_article,
            "excerpt": "",
            "confidence": "DA_VERIFICARE",
            "requires_tl_confirmation": True,
            "planner_eligible": False,
            "limitation": "resolved path escapes authorized source root",
        }

    if not target.exists():
        return {
            "source_id": SOURCE_ID,
            "source_status": SOURCE_MISSING,
            "article": safe_article,
            "excerpt": "",
            "confidence": "DA_VERIFICARE",
            "requires_tl_confirmation": True,
            "planner_eligible": False,
            "limitation": "spec intake preview metadata not found",
        }

    data = json.loads(target.read_text(encoding="utf-8"))

    status = str(data.get("status") or "").strip().upper()
    confidence = str(data.get("confidence") or "DA_VERIFICARE").strip().upper()
    requires_tl_confirmation = bool(data.get("requires_tl_confirmation", True))

    article_payload = data.get("article") if isinstance(data.get("article"), dict) else {}
    codice = str(article_payload.get("codice") or "").strip()
    disegno = str(article_payload.get("disegno") or "").strip()

    excerpt_parts = [
        f"{safe_article} trovato in spec_intake_preview.",
        f"status={status or 'DA_VERIFICARE'}.",
        f"confidence={confidence}.",
    ]

    if codice:
        excerpt_parts.append(f"codice={codice}.")
    if disegno:
        excerpt_parts.append(f"disegno={disegno}.")

    return {
        "source_id": SOURCE_ID,
        "source_status": SOURCE_FOUND if status == "PREVIEW_ONLY" else SOURCE_MISSING,
        "article": safe_article,
        "excerpt": " ".join(excerpt_parts),
        "confidence": confidence if confidence else "DA_VERIFICARE",
        "requires_tl_confirmation": True if requires_tl_confirmation else True,
        "planner_eligible": False,
        "limitation": "preview-only source; no planner eligibility and no promotion to CERTO",
    }
