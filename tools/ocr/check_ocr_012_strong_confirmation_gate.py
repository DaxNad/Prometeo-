#!/usr/bin/env python3
import json
import sys
from pathlib import Path
from datetime import datetime

OUT_DIR = Path("/Users/davidepiangiolino/PROMETEO/data/local_reports/ocr_012")
OUT_DIR.mkdir(parents=True, exist_ok=True)

def main():
    if len(sys.argv) != 3:
        print(
            "USO: check_ocr_012_strong_confirmation_gate.py /path/diff.json 'CONFERMO MODIFICA 12056'",
            file=sys.stderr
        )
        sys.exit(2)

    diff_path = Path(sys.argv[1])
    phrase = sys.argv[2].strip()

    diff = json.loads(diff_path.read_text(encoding="utf-8"))
    article = str(diff.get("article_code"))
    requires_strong = bool(diff.get("requires_strong_confirmation"))

    expected = f"CONFERMO MODIFICA {article}"

    accepted = True
    reason = "LIGHT_CONFIRMATION_ALLOWED"

    if requires_strong:
        accepted = phrase == expected
        reason = "STRONG_CONFIRMATION_MATCH" if accepted else "STRONG_CONFIRMATION_REQUIRED_EXACT_PHRASE"

    result = {
        "status": "PREVIEW_ONLY",
        "capability": "OCR_012_STRONG_CONFIRMATION_GATE",
        "timestamp": datetime.now().isoformat(),
        "diff_source": str(diff_path),
        "article_code": article,
        "risk": diff.get("risk"),
        "requires_strong_confirmation": requires_strong,
        "provided_phrase": phrase,
        "expected_phrase": expected if requires_strong else None,
        "accepted": accepted,
        "reason": reason,
        "writes_to_smf": False,
        "writes_to_database": False,
        "writes_to_planner": False,
        "next_action": "CAN_BUILD_APPROVED_PREVIEW" if accepted else "BLOCKED"
    }

    out_json = OUT_DIR / f"OCR_012_STRONG_CONFIRMATION_GATE_{article}.json"
    out_txt = OUT_DIR / f"OCR_012_STRONG_CONFIRMATION_GATE_{article}.txt"

    out_json.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    txt = f"""OCR_012 STRONG CONFIRMATION GATE
================================================================================
STATUS: PREVIEW_ONLY
ARTICLE: {article}
RISK: {result['risk']}
REQUIRES_STRONG_CONFIRMATION: {requires_strong}
PROVIDED: {phrase}
EXPECTED: {result['expected_phrase']}
ACCEPTED: {accepted}
REASON: {reason}
NO SMF / NO DATABASE / NO PLANNER
NEXT_ACTION: {result['next_action']}
"""
    out_txt.write_text(txt, encoding="utf-8")

    print(out_json)
    print(out_txt)
    print(txt)

if __name__ == "__main__":
    main()
