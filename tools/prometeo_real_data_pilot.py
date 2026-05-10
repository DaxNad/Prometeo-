#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SPECS_ROOT = ROOT / "specs_finitura"

ALLOWED_CLASSES = {
    "STANDARD",
    "REFERENCE_ONLY",
    "ONE_SHOT",
    "RICAMBIO",
    "DA_VERIFICARE",
}

ARTICLE_PATTERN = re.compile(r"^[0-9]{5}[A-Z]{0,3}$")
DRAWING_PATTERN = re.compile(r"^[A-Z0-9_.-]+$")


def fail(message: str) -> None:
    raise SystemExit(f"ERRORE: {message}")


def normalize_article(value: str) -> str:
    article = str(value or "").strip().upper()
    if not ARTICLE_PATTERN.match(article):
        fail("codice articolo non valido. Atteso formato tipo 12056 o 12191A.")
    return article


def normalize_class(value: str) -> str:
    cls = str(value or "").strip().upper()
    if cls not in ALLOWED_CLASSES:
        fail(f"classe operativa non valida: {cls}. Valori ammessi: {', '.join(sorted(ALLOWED_CLASSES))}")
    return cls


def normalize_bool(value: str | None, *, default: bool) -> bool:
    if value is None:
        return default
    raw = str(value).strip().lower()
    if raw in {"1", "true", "yes", "y", "si", "sì"}:
        return True
    if raw in {"0", "false", "no", "n"}:
        return False
    fail(f"booleano non valido: {value}")


def validate_safe_text(label: str, value: str | None, *, required: bool = False) -> str:
    text = str(value or "").strip()
    if required and not text:
        fail(f"{label} obbligatorio.")

    if not text:
        return ""

    lowered = text.lower()

    home_path = str(Path.home()).lower()
    if home_path and home_path in lowered:
        fail(f"{label} contiene un path locale personale.")

    if re.search(r"(^|\\s)/(users|home|private|var|volumes|mnt)/", lowered):
        fail(f"{label} contiene un path assoluto locale.")

    blocked_terms = [
        ".photoslibrary",
        "apikey",
        "api_key",
        "token",
        "secret",
        "password",
    ]
    for term in blocked_terms:
        if term in lowered:
            fail(f"{label} contiene un termine sensibile non ammesso.")

    return text


def build_metadata(args: argparse.Namespace, existing: dict[str, Any] | None = None) -> dict[str, Any]:
    existing = existing or {}

    article = normalize_article(args.article)
    operational_class = normalize_class(args.operational_class)

    drawing = validate_safe_text("disegno", args.drawing or existing.get("drawing", ""))
    if drawing and not DRAWING_PATTERN.match(drawing):
        fail("disegno contiene caratteri non ammessi. Usa lettere/numeri/underscore/punto/trattino.")

    rev = validate_safe_text("rev", args.rev or existing.get("rev") or existing.get("revision", ""))
    source = validate_safe_text("source", args.source or existing.get("source") or "TL", required=True)
    route_status = validate_safe_text("route_status", args.route_status or existing.get("route_status") or existing.get("classification") or "DA_VERIFICARE", required=True)
    notes = validate_safe_text("notes", args.notes or existing.get("notes") or existing.get("note") or "")

    planner_default = operational_class == "STANDARD"
    planner_eligible = normalize_bool(args.planner_eligible, default=planner_default)

    if operational_class in {"REFERENCE_ONLY", "ONE_SHOT", "RICAMBIO"} and planner_eligible:
        fail("REFERENCE_ONLY / ONE_SHOT / RICAMBIO non possono avere planner_eligible=true senza gestione esplicita separata.")

    now = datetime.now(timezone.utc).isoformat()

    metadata = dict(existing)
    metadata.update(
        {
            "schema": "PROMETEO_REAL_DATA_PILOT_V1",
            "article": article,
            "drawing": drawing,
            "rev": rev,
            "operational_class": operational_class,
            "planner_eligible": planner_eligible,
            "route_status": route_status,
            "source": source,
            "confidence": existing.get("confidence") or existing.get("classification") or "DA_VERIFICARE",
            "updated_at": now,
            "assets": {
                **(existing.get("assets") if isinstance(existing.get("assets"), dict) else {}),
                "spec_image_expected": bool(drawing),
                "spec_image_filename": f"{article}_{drawing}_rev{rev}.png" if drawing and rev else "",
            },
            "notes": notes,
            "rules": [
                "metadata reale locale: non pushare se contiene dati sensibili",
                "immagini/specifiche reali non devono essere versionate",
                "TL resta fonte di conferma operativa",
                "planner_eligible dipende da operational_class e conferma TL",
            ],
        }
    )

    metadata.setdefault("created_at", existing.get("created_at") or now)

    return metadata


def read_existing_metadata(article: str) -> dict[str, Any]:
    metadata_path = SPECS_ROOT / article / "metadata.json"
    if not metadata_path.exists():
        return {}

    try:
        data = json.loads(metadata_path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"metadata esistente non leggibile: {metadata_path} ({exc})")

    if not isinstance(data, dict):
        fail(f"metadata esistente non valido: {metadata_path}")

    return data


def write_metadata(metadata: dict[str, Any], *, overwrite: bool, merge_existing: bool) -> Path:
    article = metadata["article"]
    article_dir = SPECS_ROOT / article
    metadata_path = article_dir / "metadata.json"

    article_dir.mkdir(parents=True, exist_ok=True)

    if metadata_path.exists() and not overwrite and not merge_existing:
        fail(f"metadata già presente: {metadata_path}. Usa --merge-existing per preservare e normalizzare, oppure --overwrite solo dopo verifica diff.")

    metadata_path.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return metadata_path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="PROMETEO real-data pilot scaffold: crea metadata controllato per un articolo reale."
    )
    parser.add_argument("--article", required=True, help="Codice articolo, es. 12056 o 12191A")
    parser.add_argument("--operational-class", required=True, help="STANDARD / REFERENCE_ONLY / ONE_SHOT / RICAMBIO / DA_VERIFICARE")
    parser.add_argument("--drawing", default="", help="Disegno sanificato, opzionale")
    parser.add_argument("--rev", default="", help="Revisione, opzionale")
    parser.add_argument("--planner-eligible", default=None, help="true/false. Default true solo per STANDARD")
    parser.add_argument("--route-status", default=None, help="CERTO / INFERITO / DA_VERIFICARE")
    parser.add_argument("--source", default=None, help="Fonte sanificata, es. TL")
    parser.add_argument("--notes", default="", help="Note sanificate")
    parser.add_argument("--overwrite", action="store_true", help="Sovrascrive metadata esistente solo se esplicito")
    parser.add_argument("--merge-existing", action="store_true", help="Preserva metadata esistente e aggiunge/normalizza i campi pilota V1")

    args = parser.parse_args()

    article = normalize_article(args.article)
    existing = read_existing_metadata(article) if args.merge_existing else {}

    if args.overwrite and args.merge_existing:
        fail("usa --overwrite oppure --merge-existing, non entrambi.")

    metadata = build_metadata(args, existing=existing)
    metadata_path = write_metadata(metadata, overwrite=args.overwrite, merge_existing=args.merge_existing)

    print("PROMETEO_REAL_DATA_PILOT_OK")
    print(f"metadata: {metadata_path.relative_to(ROOT)}")
    print(f"article: {metadata['article']}")
    print(f"operational_class: {metadata['operational_class']}")
    print(f"planner_eligible: {metadata['planner_eligible']}")
    print(f"route_status: {metadata['route_status']}")
    if metadata["assets"]["spec_image_filename"]:
        print(f"spec_image_expected: specs_finitura/{metadata['article']}/{metadata['assets']['spec_image_filename']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
