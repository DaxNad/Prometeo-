#!/usr/bin/env python3
import json
import sys
from pathlib import Path
from datetime import datetime

OUT_DIR = Path("/Users/davidepiangiolino/PROMETEO/data/local_reports/ocr_013")
OUT_DIR.mkdir(parents=True, exist_ok=True)

def main():
    if len(sys.argv) != 3:
        print(
            "USO: build_ocr_013_approved_preview_package.py /path/diff.json /path/gate.json",
            file=sys.stderr
        )
        sys.exit(2)

    diff_path = Path(sys.argv[1])
    gate_path = Path(sys.argv[2])

    diff = json.loads(diff_path.read_text(encoding="utf-8"))
    gate = json.loads(gate_path.read_text(encoding="utf-8"))

    article = str(diff.get("article_code"))
    accepted = bool(gate.get("accepted"))
    same_article = str(gate.get("article_code")) == article

    package_status = "APPROVED_PREVIEW" if accepted and same_article else "BLOCKED_PREVIEW"

    result = {
        "status": "PREVIEW_ONLY",
        "capability": "OCR_013_APPROVED_PREVIEW_PACKAGE",
        "timestamp": datetime.now().isoformat(),
        "article_code": article,
        "package_status": package_status,
        "accepted_by_gate": accepted,
        "same_article_check": same_article,
        "risk": diff.get("risk"),
        "requires_strong_confirmation": diff.get("requires_strong_confirmation"),
        "diff_source": str(diff_path),
        "gate_source": str(gate_path),
        "raw_command": diff.get("raw_command"),
        "provided_confirmation": gate.get("provided_phrase"),
        "changes": diff.get("changes", []),
        "approved_after_preview": diff.get("after") if package_status == "APPROVED_PREVIEW" else None,
        "writes_to_smf": False,
        "writes_to_database": False,
        "writes_to_planner": False,
        "ready_for_future_apply": False,
        "future_apply_block_reason": (
            "Capability preview only: serve una capability separata APPLY con audit, backup e rollback."
            if package_status == "APPROVED_PREVIEW"
            else "Gate non accettato o articolo non coerente."
        )
    }

    out_json = OUT_DIR / f"OCR_013_APPROVED_PREVIEW_PACKAGE_{article}.json"
    out_txt = OUT_DIR / f"OCR_013_APPROVED_PREVIEW_PACKAGE_{article}.txt"

    out_json.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = []
    lines.append("OCR_013 APPROVED PREVIEW PACKAGE")
    lines.append("=" * 80)
    lines.append(f"STATUS: {result['status']}")
    lines.append(f"ARTICLE: {article}")
    lines.append(f"PACKAGE_STATUS: {package_status}")
    lines.append(f"ACCEPTED_BY_GATE: {accepted}")
    lines.append(f"SAME_ARTICLE_CHECK: {same_article}")
    lines.append(f"RISK: {result['risk']}")
    lines.append(f"REQUIRES_STRONG_CONFIRMATION: {result['requires_strong_confirmation']}")
    lines.append("NO SMF / NO DATABASE / NO PLANNER")
    lines.append(f"READY_FOR_FUTURE_APPLY: {result['ready_for_future_apply']}")
    lines.append(f"FUTURE_APPLY_BLOCK_REASON: {result['future_apply_block_reason']}")
    lines.append("")
    lines.append("CHANGES")
    for c in result["changes"]:
        lines.append(f"- {c.get('field')}: {c.get('before')} -> {c.get('after')}")

    out_txt.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(out_json)
    print(out_txt)
    print(out_txt.read_text(encoding="utf-8"))

if __name__ == "__main__":
    main()
