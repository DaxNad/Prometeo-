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


def build_metadata(args: argparse.Namespace) -> dict[str, Any]:
    article = normalize_article(args.article)
    operational_class = normalize_class(args.operational_class)

    drawing = validate_safe_text("disegno", args.drawing)
    if drawing and not DRAWING_PATTERN.match(drawing):
        fail("disegno contiene caratteri non ammessi. Usa lettere/numeri/underscore/punto/trattino.")

    rev = validate_safe_text("rev", args.rev)
    source = validate_safe_text("source", args.source or "TL", required=True)
    route_status = validate_safe_text("route_status", args.route_status or "DA_VERIFICARE", required=True)
    notes = validate_safe_text("notes", args.notes)

    planner_default = operational_class == "STANDARD"
    planner_eligible = normalize_bool(args.planner_eligible, default=planner_default)

    if operational_class in {"REFERENCE_ONLY", "ONE_SHOT", "RICAMBIO"} and planner_eligible:
        fail("REFERENCE_ONLY / ONE_SHOT / RICAMBIO non possono avere planner_eligible=true senza gestione esplicita separata.")

    now = datetime.now(timezone.utc).isoformat()

    return {
        "schema": "PROMETEO_REAL_DATA_PILOT_V1",
        "article": article,
        "drawing": drawing,
        "rev": rev,
        "operational_class": operational_class,
        "planner_eligible": planner_eligible,
        "route_status": route_status,
        "source": source,
        "confidence": "DA_VERIFICARE",
        "created_at": now,
        "updated_at": now,
        "assets": {
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


def write_metadata(metadata: dict[str, Any], *, overwrite: bool) -> Path:
    article = metadata["article"]
    article_dir = SPECS_ROOT / article
    metadata_path = article_dir / "metadata.json"

    article_dir.mkdir(parents=True, exist_ok=True)

    if metadata_path.exists() and not overwrite:
        fail(f"metadata già presente: {metadata_path}. Usa --overwrite solo dopo verifica diff.")

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
    parser.add_argument("--route-status", default="DA_VERIFICARE", help="CERTO / INFERITO / DA_VERIFICARE")
    parser.add_argument("--source", default="TL", help="Fonte sanificata, es. TL")
    parser.add_argument("--notes", default="", help="Note sanificate")
    parser.add_argument("--overwrite", action="store_true", help="Sovrascrive metadata esistente solo se esplicito")

    args = parser.parse_args()
    metadata = build_metadata(args)
    metadata_path = write_metadata(metadata, overwrite=args.overwrite)

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
