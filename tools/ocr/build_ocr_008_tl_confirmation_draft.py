#!/usr/bin/env python3
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
from datetime import datetime

SRC = PROJECT_ROOT / "data/local_reports/ocr_007/OCR_007_SPEC_DENSIFICATION_PREVIEW.json"
OUT_DIR = PROJECT_ROOT / "data/local_reports/ocr_008"
OUT_DIR.mkdir(parents=True, exist_ok=True)

data = json.loads(SRC.read_text(encoding="utf-8"))

draft = {
    "status": "PREVIEW_ONLY",
    "capability": "OCR_008_TL_CONFIRMATION_DRAFT",
    "timestamp": datetime.now().isoformat(),
    "writes_to_smf": False,
    "writes_to_database": False,
    "writes_to_planner": False,
    "items": []
}

for item in data["items"]:
    article = item["article_code"]
    quality = item["quality"]

    if quality == "PASS":
        confirmation_type = "LIGHT_CONFIRMATION"
        question = (
            f"CONFERMA TL {article}: componenti, route, disegno, revisione, lotto e imballo "
            f"sono coerenti con la specifica?"
        )
    elif quality == "PARTIAL":
        confirmation_type = "REVIEW_REQUIRED"
        missing = []
        if item.get("revision") in (None, "", []):
            missing.append("REV")
        if item.get("packaging", {}).get("package_quantity") in (None, "", []):
            missing.append("QTA_IMBALLO")
        if len(item.get("components_preview", [])) < 3:
            missing.append("COMPONENTI")
        if len(item.get("route_preview", [])) < 5:
            missing.append("ROUTE")

        missing_txt = ", ".join(missing) if missing else "campi/parsing da verificare"
        question = (
            f"REVIEW TL {article}: dati parziali. Verificare/completare: {missing_txt}."
        )
    elif quality == "SKIP_DOCUMENT_TYPE":
        confirmation_type = "NO_STANDARD_CONFIRMATION"
        question = (
            f"SKIP {article}: documento 500xx/non standard escluso dal parser specifiche. "
            f"Non usare per route standard."
        )
    else:
        confirmation_type = "FAIL_REVIEW"
        question = f"FAIL {article}: verificare OCR, immagine o parser."

    draft["items"].append({
        "article_code": article,
        "quality": quality,
        "article_class_preview": item["article_class_preview"],
        "confirmation_type": confirmation_type,
        "question": question,
        "planner_eligible_after_confirmation": False,
        "note": "Anche dopo conferma TL, questa capability non abilita planner né scrive dati."
    })

out_json = OUT_DIR / "OCR_008_TL_CONFIRMATION_DRAFT.json"
out_txt = OUT_DIR / "OCR_008_TL_CONFIRMATION_DRAFT.txt"

out_json.write_text(json.dumps(draft, indent=2, ensure_ascii=False), encoding="utf-8")

lines = []
lines.append("OCR_008 TL CONFIRMATION DRAFT")
lines.append("=" * 80)
lines.append("STATUS: PREVIEW_ONLY")
lines.append("NO SMF / NO DATABASE / NO PLANNER")
lines.append("")

for item in draft["items"]:
    lines.append("-" * 80)
    lines.append(f"ARTICLE: {item['article_code']}")
    lines.append(f"QUALITY: {item['quality']}")
    lines.append(f"TYPE: {item['confirmation_type']}")
    lines.append(f"QUESTION: {item['question']}")
    lines.append(f"PLANNER_AFTER_CONFIRMATION: {item['planner_eligible_after_confirmation']}")

out_txt.write_text("\n".join(lines) + "\n", encoding="utf-8")

print(out_json)
print(out_txt)
