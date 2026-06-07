#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime
import json

OUT_DIR = Path("/Users/davidepiangiolino/PROMETEO/data/local_reports/ocr_006")
OUT_DIR.mkdir(parents=True, exist_ok=True)

report = {
    "status": "CAPABILITY_CLOSED",
    "capability": "OCR_001_TO_OCR_006",
    "timestamp": datetime.now().isoformat(),
    "scope": [
        "OCR_001_SINGLE_SPEC",
        "OCR_002_BATCH_PREVIEW",
        "OCR_003_DOCUMENT_FILTER",
        "OCR_004_GOVERNED_REPORT",
        "OCR_005_TL_REVIEW_QUEUE"
    ],
    "results": {
        "tested_documents": 5,
        "pass": 1,
        "partial": 2,
        "skip_document_type": 2,
        "fail": 0
    },
    "achievements": [
        "OCR Vision Apple funzionante",
        "Estrazione JSON strutturata",
        "Riconoscimento componenti",
        "Riconoscimento route operative",
        "Filtro documenti 500xx",
        "TL Review Queue",
        "Nessuna scrittura su dati reali"
    ],
    "limitations": [
        "Parser ancora basato su pattern",
        "Nessun registry componenti completo",
        "Nessun confronto automatico con specifiche storiche",
        "Nessun retrieval"
    ],
    "safety": {
        "writes_to_smf": False,
        "writes_to_database": False,
        "writes_to_planner": False,
        "human_in_the_loop": True
    },
    "next_capability": "OCR_007_SPEC_DENSIFICATION_PREVIEW"
}

json_file = OUT_DIR / "OCR_006_CAPABILITY_CLOSURE.json"
txt_file = OUT_DIR / "OCR_006_CAPABILITY_CLOSURE.txt"

json_file.write_text(
    json.dumps(report, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

txt = f"""
OCR_006 CAPABILITY CLOSURE
================================================================

STATUS: CAPABILITY_CLOSED

TESTED_DOCUMENTS: 5
PASS: 1
PARTIAL: 2
SKIP_DOCUMENT_TYPE: 2
FAIL: 0

ACHIEVEMENTS:
- OCR Vision Apple funzionante
- JSON strutturato
- Component extraction
- Route extraction
- 500xx filter
- TL review queue

SAFETY:
- NO SMF
- NO DATABASE
- NO PLANNER
- HUMAN IN THE LOOP

NEXT CAPABILITY:
OCR_007_SPEC_DENSIFICATION_PREVIEW
"""

txt_file.write_text(txt, encoding="utf-8")

print(json_file)
print(txt_file)
