#!/usr/bin/env python3
import json
from pathlib import Path

base = Path("/Users/davidepiangiolino/PROMETEO/data/local_reports/ocr_002")
files = sorted(base.glob("*_structured.json"))

def score(data):
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
    "capability": "OCR_002_BATCH_QUALITY",
    "summary": {
        "total": 0,
        "PASS": 0,
        "PARTIAL": 0,
        "FAIL": 0
    },
    "items": []
}

for p in files:
    data = json.loads(p.read_text(encoding="utf-8"))
    verdict = score(data)
    report["summary"]["total"] += 1
    report["summary"][verdict] += 1
    report["items"].append({
        "file": p.name,
        "article_code": data.get("article_code"),
        "drawing": data.get("drawing"),
        "revision": data.get("revision"),
        "lot_quantity": data.get("lot_quantity"),
        "package_code": data.get("package_code"),
        "package_quantity": data.get("package_quantity"),
        "components_count": len(data.get("components", [])),
        "route_steps_count": len(data.get("route_preview", [])),
        "quality": verdict
    })

out = base / "OCR_002_QUALITY_REPORT.json"
out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

print(out)
print(json.dumps(report["summary"], indent=2))
