from __future__ import annotations

import csv
import json
from pathlib import Path

from app.domain.finishing_specs_densifier import build_densification_preview


ROOT = Path(__file__).resolve().parents[1]
SPECS_ROOT = ROOT / "specs_finitura"
OUT = ROOT / "data" / "local_reports" / "finishing_specs_densification_preview.json"
LOCAL_SMF = ROOT / "data" / "local_smf"
CODICI_STAGING_PREVIEW = LOCAL_SMF / "codici_staging_preview.json"
BOM_SPECS = LOCAL_SMF / "BOM_Specs.csv"
BOM_OPERATIONS = LOCAL_SMF / "BOM_Operations.csv"


def _load_json(path: Path):
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return data


def _load_codici_staging_support(article: str) -> dict:
    data = _load_json(CODICI_STAGING_PREVIEW)
    if not isinstance(data, dict):
        return {}

    items = data.get("items") or data.get("records") or data.get("codici") or []
    if isinstance(items, dict):
        items = list(items.values())

    for item in items:
        if not isinstance(item, dict):
            continue
        code = str(
            item.get("codice")
            or item.get("article")
            or item.get("articolo")
            or ""
        ).strip()
        if code == article:
            return {
                "drawing": item.get("disegno") or item.get("drawing") or item.get("Disegno associato (link)") or "",
                "revision": item.get("revisione") or item.get("revision") or item.get("Revisione") or "",
                "packaging": item.get("imballo") or item.get("Imballo") or "",
                "support_source": "codici_staging_preview",
            }

    return {}


def _load_bom_support(article: str) -> dict:
    support: dict = {
        "linked_bom": [],
        "stations_expected": [],
        "support_source": "BOM_CSV_DERIVED",
    }

    if BOM_SPECS.exists():
        try:
            with BOM_SPECS.open(encoding="utf-8", newline="") as fh:
                reader = csv.DictReader(fh)
                for row in reader:
                    if str(row.get("articolo") or row.get("article") or row.get("codice") or "").strip() != article:
                        continue
                    support["drawing"] = row.get("disegno") or row.get("drawing") or support.get("drawing", "")
                    support["revision"] = row.get("revisione") or row.get("revision") or support.get("revision", "")
                    support["packaging"] = row.get("imballo") or row.get("packaging") or support.get("packaging", "")
                    raw_json = row.get("raw_json") or row.get("extra") or ""
                    if raw_json:
                        try:
                            payload = json.loads(raw_json)
                        except Exception:
                            payload = {}
                        if isinstance(payload, dict):
                            for comp in payload.get("componenti", []) or []:
                                if isinstance(comp, dict) and comp.get("codice"):
                                    support["linked_bom"].append({"component": comp.get("codice")})
        except Exception:
            pass

    if BOM_OPERATIONS.exists():
        try:
            with BOM_OPERATIONS.open(encoding="utf-8", newline="") as fh:
                reader = csv.DictReader(fh)
                for row in reader:
                    if str(row.get("articolo") or row.get("article") or row.get("codice") or "").strip() != article:
                        continue
                    phase = str(
                        row.get("phase")
                        or row.get("fase")
                        or row.get("operazione")
                        or row.get("station")
                        or row.get("postazione")
                        or ""
                    ).strip().upper()
                    if phase:
                        support["stations_expected"].append(phase)
        except Exception:
            pass

    # Normalizza duplicati mantenendo ordine.
    support["stations_expected"] = list(dict.fromkeys(support["stations_expected"]))
    seen = set()
    linked = []
    for item in support["linked_bom"]:
        code = item.get("component")
        if code and code not in seen:
            linked.append(item)
            seen.add(code)
    support["linked_bom"] = linked

    return {k: v for k, v in support.items() if v}


def _load_metadata(record: dict):
    article = str(record.get("article") or "").strip()
    path = ROOT / str(record.get("metadata_path", ""))

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        data = {}

    if not isinstance(data, dict):
        data = {}

    # Supporti derivati: servono solo a generare ASK_TL, mai CERTO automatico.
    staging = _load_codici_staging_support(article)
    bom = _load_bom_support(article)

    enriched = {}
    enriched.update(staging)
    enriched.update(bom)
    enriched.update(data)

    if staging or bom:
        enriched["support_sources"] = [src for src in [
            staging.get("support_source"),
            bom.get("support_source"),
        ] if src]

    return enriched


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    preview = build_densification_preview(SPECS_ROOT, metadata_loader=_load_metadata)
    OUT.write_text(json.dumps(preview, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print("PREVIEW_OK", OUT.relative_to(ROOT))
    print("records_count:", preview["records_count"])
    print("counts:", preview["counts"])

    for item in preview["results"]:
        if item["classification"] != "ALREADY_AUTHORITATIVE":
            print(
                item["article"],
                "|",
                item["classification"],
                "|",
                ",".join(item["reasons"]),
            )

            questions = item.get("suggested_questions") or []
            for question in questions[:3]:
                print("  -", question)


if __name__ == "__main__":
    main()
