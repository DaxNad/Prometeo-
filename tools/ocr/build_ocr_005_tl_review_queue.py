#!/usr/bin/env python3
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

SRC = PROJECT_ROOT / "data/local_reports/ocr_004/OCR_004_GOVERNED_REPORT.json"
OUT_DIR = PROJECT_ROOT / "data/local_reports/ocr_005"
OUT_DIR.mkdir(parents=True, exist_ok=True)

report = json.loads(SRC.read_text(encoding="utf-8"))

queue = {
    "status": "PREVIEW_ONLY",
    "capability": "OCR_005_TL_REVIEW_QUEUE",
    "writes_to_smf": False,
    "writes_to_database": False,
    "writes_to_planner": False,
    "items": []
}

for item in report["items"]:
    quality = item["quality"]

    if quality == "PASS":
        review_level = "TL_REVIEW_LIGHT"
        tl_question = "Verificare se componenti, route e imballo sono coerenti."
        priority = 1
    elif quality == "PARTIAL":
        review_level = "TL_REVIEW_REQUIRED"
        tl_question = "Completare o correggere i campi mancanti/incompleti prima di usare il dato."
        priority = 2
    elif quality == "SKIP_DOCUMENT_TYPE":
        review_level = "NO_TL_REVIEW_STANDARD_PARSER"
        tl_question = "Documento escluso dal parser standard. Non usare per route standard."
        priority = 9
    else:
        review_level = "OCR_OR_PARSER_FAIL"
        tl_question = "Verificare immagine/OCR/parser."
        priority = 5

    queue["items"].append({
        "priority": priority,
        "article_code": item["article_code"],
        "source_file": item["file"],
        "quality": quality,
        "document_type": item["document_type"],
        "review_level": review_level,
        "tl_question": tl_question,
        "drawing": item["drawing"],
        "revision": item["revision"],
        "lot_quantity": item["lot_quantity"],
        "package_code": item["package_code"],
        "package_quantity": item["package_quantity"],
        "components_count": item["components_count"],
        "route_steps_count": item["route_steps_count"],
        "allowed_next_action": item["next_action"]
    })

queue["items"].sort(key=lambda x: (x["priority"], str(x["article_code"])))

out_json = OUT_DIR / "OCR_005_TL_REVIEW_QUEUE.json"
out_txt = OUT_DIR / "OCR_005_TL_REVIEW_QUEUE.txt"

out_json.write_text(json.dumps(queue, indent=2, ensure_ascii=False), encoding="utf-8")

lines = []
lines.append("OCR_005 TL REVIEW QUEUE")
lines.append("=" * 80)
lines.append("STATUS: PREVIEW_ONLY")
lines.append("NO SMF / NO DATABASE / NO PLANNER")
lines.append("")

for item in queue["items"]:
    lines.append("-" * 80)
    lines.append(f"ARTICLE: {item['article_code']}")
    lines.append(f"QUALITY: {item['quality']}")
    lines.append(f"REVIEW_LEVEL: {item['review_level']}")
    lines.append(f"QUESTION: {item['tl_question']}")
    lines.append(f"DRAWING: {item['drawing']}")
    lines.append(f"REV: {item['revision']}")
    lines.append(f"LOT: {item['lot_quantity']}")
    lines.append(f"IMBALLO: {item['package_code']}")
    lines.append(f"QTA_IMBALLO: {item['package_quantity']}")
    lines.append(f"COMPONENTS_COUNT: {item['components_count']}")
    lines.append(f"ROUTE_STEPS_COUNT: {item['route_steps_count']}")
    lines.append(f"NEXT_ACTION: {item['allowed_next_action']}")

out_txt.write_text("\n".join(lines) + "\n", encoding="utf-8")

print(out_json)
print(out_txt)
