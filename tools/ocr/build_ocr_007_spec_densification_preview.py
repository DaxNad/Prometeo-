#!/usr/bin/env python3
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
from datetime import datetime

QUEUE = PROJECT_ROOT / "data/local_reports/ocr_005/OCR_005_TL_REVIEW_QUEUE.json"
STRUCTURED_DIR = PROJECT_ROOT / "data/local_reports/ocr_003"
OUT_DIR = PROJECT_ROOT / "data/local_reports/ocr_007"
OUT_DIR.mkdir(parents=True, exist_ok=True)

queue = json.loads(QUEUE.read_text(encoding="utf-8"))

def load_structured(source_file):
    p = STRUCTURED_DIR / source_file
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return None

def classify_article(item):
    article = str(item.get("article_code") or "")
    if article.startswith("500"):
        return "COMPONENT_REFERENCE_ONLY"
    if item.get("quality") == "PASS":
        return "STANDARD_CANDIDATE"
    if item.get("quality") == "PARTIAL":
        return "STANDARD_PARTIAL_REVIEW_REQUIRED"
    return "UNKNOWN_OR_UNUSABLE"

densified = {
    "status": "PREVIEW_ONLY",
    "capability": "OCR_007_SPEC_DENSIFICATION_PREVIEW",
    "timestamp": datetime.now().isoformat(),
    "writes_to_smf": False,
    "writes_to_database": False,
    "writes_to_planner": False,
    "source_queue": str(QUEUE),
    "items": []
}

for item in queue["items"]:
    structured = load_structured(item["source_file"])
    article_class = classify_article(item)

    components = []
    route = []
    warnings = []

    if structured:
        components = structured.get("components", [])
        route = structured.get("route_preview", [])
        warnings = structured.get("warnings", [])

    usable_for_planner = False
    if item["quality"] == "PASS":
        planner_block_reason = "Preview validabile dal TL, ma non ancora autorizzata per planner."
    elif item["quality"] == "PARTIAL":
        planner_block_reason = "Dati parziali: serve review TL/parser prima di qualsiasi uso operativo."
    elif item["quality"] == "SKIP_DOCUMENT_TYPE":
        planner_block_reason = "Documento escluso dal parser standard."
    else:
        planner_block_reason = "OCR/parser non affidabile."

    densified["items"].append({
        "article_code": item.get("article_code"),
        "article_class_preview": article_class,
        "document_type": item.get("document_type"),
        "quality": item.get("quality"),
        "review_level": item.get("review_level"),
        "drawing": item.get("drawing"),
        "revision": item.get("revision"),
        "lot_quantity": item.get("lot_quantity"),
        "packaging": {
            "package_code": item.get("package_code"),
            "package_quantity": item.get("package_quantity")
        },
        "components_preview": components,
        "route_preview": route,
        "planner_eligible": usable_for_planner,
        "planner_block_reason": planner_block_reason,
        "tl_review_question": item.get("tl_question"),
        "warnings": warnings,
        "source_structured_file": str(STRUCTURED_DIR / item["source_file"])
    })

out_json = OUT_DIR / "OCR_007_SPEC_DENSIFICATION_PREVIEW.json"
out_txt = OUT_DIR / "OCR_007_SPEC_DENSIFICATION_PREVIEW.txt"

out_json.write_text(json.dumps(densified, indent=2, ensure_ascii=False), encoding="utf-8")

lines = []
lines.append("OCR_007 SPEC DENSIFICATION PREVIEW")
lines.append("=" * 80)
lines.append("STATUS: PREVIEW_ONLY")
lines.append("NO SMF / NO DATABASE / NO PLANNER")
lines.append("PLANNER_ELIGIBLE: always false in this capability")
lines.append("")

for item in densified["items"]:
    lines.append("-" * 80)
    lines.append(f"ARTICLE: {item['article_code']}")
    lines.append(f"CLASS: {item['article_class_preview']}")
    lines.append(f"QUALITY: {item['quality']}")
    lines.append(f"REVIEW: {item['review_level']}")
    lines.append(f"DRAWING: {item['drawing']}")
    lines.append(f"REV: {item['revision']}")
    lines.append(f"LOT: {item['lot_quantity']}")
    lines.append(f"PACKAGING: {item['packaging']}")
    lines.append(f"COMPONENTS: {[c.get('code') for c in item['components_preview']]}")
    lines.append(f"ROUTE: {' -> '.join(item['route_preview'])}")
    lines.append(f"PLANNER_ELIGIBLE: {item['planner_eligible']}")
    lines.append(f"BLOCK_REASON: {item['planner_block_reason']}")
    lines.append(f"TL_QUESTION: {item['tl_review_question']}")

out_txt.write_text("\n".join(lines) + "\n", encoding="utf-8")

print(out_json)
print(out_txt)
