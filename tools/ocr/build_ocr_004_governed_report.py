#!/usr/bin/env python3
import json
from pathlib import Path

SRC_DIR = Path("/Users/davidepiangiolino/PROMETEO/data/local_reports/ocr_003")
OUT_DIR = Path("/Users/davidepiangiolino/PROMETEO/data/local_reports/ocr_004")
OUT_DIR.mkdir(parents=True, exist_ok=True)

def verdict(data):
    if data.get("parse_quality") == "SKIP_DOCUMENT_TYPE":
        return "SKIP_DOCUMENT_TYPE"

    required = [
        "article_code",
        "drawing",
        "revision",
        "lot_quantity",
        "package_code",
        "package_quantity",
    ]

    present = sum(1 for k in required if data.get(k) not in (None, "", []))
    components = len(data.get("components", []))
    route = len(data.get("route_preview", []))

    if present >= 6 and components >= 3 and route >= 5:
        return "PASS"
    if present >= 3 or components >= 1 or route >= 2:
        return "PARTIAL"
    return "FAIL"

report = {
    "status": "PREVIEW_ONLY",
    "capability": "OCR_004_GOVERNED_REPORT",
    "writes_to_smf": False,
    "writes_to_database": False,
    "writes_to_planner": False,
    "summary": {
        "total": 0,
        "PASS": 0,
        "PARTIAL": 0,
        "FAIL": 0,
        "SKIP_DOCUMENT_TYPE": 0
    },
    "items": []
}

for p in sorted(SRC_DIR.glob("*_structured.json")):
    data = json.loads(p.read_text(encoding="utf-8"))
    v = verdict(data)

    report["summary"]["total"] += 1
    report["summary"][v] += 1

    report["items"].append({
        "file": p.name,
        "article_code": data.get("article_code"),
        "document_type": data.get("document_type"),
        "quality": v,
        "drawing": data.get("drawing"),
        "revision": data.get("revision"),
        "lot_quantity": data.get("lot_quantity"),
        "package_code": data.get("package_code"),
        "package_quantity": data.get("package_quantity"),
        "components_count": len(data.get("components", [])),
        "route_steps_count": len(data.get("route_preview", [])),
        "next_action": (
            "candidate_for_review"
            if v == "PASS"
            else "needs_tl_or_parser_review"
            if v == "PARTIAL"
            else "excluded_from_standard_parser"
            if v == "SKIP_DOCUMENT_TYPE"
            else "ocr_or_parser_fail"
        )
    })

out_json = OUT_DIR / "OCR_004_GOVERNED_REPORT.json"
out_txt = OUT_DIR / "OCR_004_GOVERNED_REPORT.txt"

out_json.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

lines = []
lines.append("OCR_004 GOVERNED REPORT")
lines.append("=" * 80)
lines.append(f"STATUS: {report['status']}")
lines.append(f"CAPABILITY: {report['capability']}")
lines.append("NO SMF / NO DATABASE / NO PLANNER")
lines.append("")
lines.append("SUMMARY")
for k, v in report["summary"].items():
    lines.append(f"- {k}: {v}")

lines.append("")
lines.append("ITEMS")
for item in report["items"]:
    lines.append("-" * 80)
    lines.append(f"FILE: {item['file']}")
    lines.append(f"ARTICLE: {item['article_code']}")
    lines.append(f"TYPE: {item['document_type']}")
    lines.append(f"QUALITY: {item['quality']}")
    lines.append(f"DRAWING: {item['drawing']}")
    lines.append(f"REV: {item['revision']}")
    lines.append(f"LOT: {item['lot_quantity']}")
    lines.append(f"IMBALLO: {item['package_code']}")
    lines.append(f"QTA_IMBALLO: {item['package_quantity']}")
    lines.append(f"COMPONENTS_COUNT: {item['components_count']}")
    lines.append(f"ROUTE_STEPS_COUNT: {item['route_steps_count']}")
    lines.append(f"NEXT_ACTION: {item['next_action']}")

out_txt.write_text("\n".join(lines) + "\n", encoding="utf-8")

print(out_json)
print(out_txt)
print(json.dumps(report["summary"], indent=2))
