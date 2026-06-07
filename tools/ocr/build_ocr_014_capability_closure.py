#!/usr/bin/env python3
import json
from pathlib import Path
from datetime import datetime

OUT_DIR = Path("/Users/davidepiangiolino/PROMETEO/data/local_reports/ocr_014")
OUT_DIR.mkdir(parents=True, exist_ok=True)

closure = {
    "status": "CAPABILITY_CLOSED",
    "capability": "OCR_007_TO_OCR_014",
    "timestamp": datetime.now().isoformat(),
    "scope": [
        "OCR_007_SPEC_DENSIFICATION_PREVIEW",
        "OCR_008_TL_CONFIRMATION_DRAFT",
        "OCR_009_CONFIRMATION_RESPONSE_SCHEMA",
        "OCR_010_TL_RESPONSE_PARSER_PREVIEW",
        "OCR_011_DIFF_PREVIEW_BUILDER",
        "OCR_012_STRONG_CONFIRMATION_GATE",
        "OCR_013_APPROVED_PREVIEW_PACKAGE"
    ],
    "results": {
        "densification_preview": "PASS",
        "tl_confirmation_draft": "PASS",
        "response_schema": "PASS",
        "tl_response_parser": "PASS",
        "diff_preview_builder": "PASS",
        "strong_confirmation_gate": "PASS",
        "approved_preview_package": "PASS"
    },
    "safety": {
        "writes_to_smf": False,
        "writes_to_database": False,
        "writes_to_planner": False,
        "ready_for_future_apply": False,
        "human_in_the_loop": True,
        "strong_confirmation_required_for_high_risk": True
    },
    "validated_behaviors": [
        "PASS/PARTIAL/SKIP trasformati in schede preview articolo",
        "Domande TL generate da quality status",
        "Comandi TL ammessi: CONFERMO, CORREGGO, SKIP, DA_VERIFICARE",
        "Correzioni componenti/route classificate HIGH risk",
        "HIGH risk bloccato senza frase esatta",
        "Frase forte accettata solo se coincide con CONFERMO MODIFICA <article_code>",
        "Pacchetto approvato resta non applicabile"
    ],
    "next_capability_candidate": "OCR_015_APPLY_DESIGN_PREVIEW_ONLY",
    "next_capability_warning": (
        "Non implementare apply reale finché non esistono backup, rollback, audit immutabile, "
        "file target espliciti e test locali."
    )
}

out_json = OUT_DIR / "OCR_014_CAPABILITY_CLOSURE.json"
out_txt = OUT_DIR / "OCR_014_CAPABILITY_CLOSURE.txt"

out_json.write_text(json.dumps(closure, indent=2, ensure_ascii=False), encoding="utf-8")

txt = f"""OCR_014 CAPABILITY CLOSURE
================================================================================

STATUS: CAPABILITY_CLOSED
CAPABILITY: OCR_007_TO_OCR_014

RESULTS:
- OCR_007 densification preview: PASS
- OCR_008 TL confirmation draft: PASS
- OCR_009 response schema: PASS
- OCR_010 TL response parser: PASS
- OCR_011 diff preview builder: PASS
- OCR_012 strong confirmation gate: PASS
- OCR_013 approved preview package: PASS

SAFETY:
- NO SMF
- NO DATABASE
- NO PLANNER
- READY_FOR_FUTURE_APPLY: False
- HUMAN_IN_THE_LOOP: True
- STRONG_CONFIRMATION_FOR_HIGH_RISK: True

VALIDATED:
- PASS/PARTIAL/SKIP -> schede preview articolo
- CONFERMO / CORREGGO / SKIP / DA_VERIFICARE
- HIGH risk per componenti/route
- Gate forte obbligatorio
- Pacchetto approvato ma non applicabile

NEXT CANDIDATE:
OCR_015_APPLY_DESIGN_PREVIEW_ONLY

WARNING:
Non implementare apply reale finché non esistono backup, rollback, audit immutabile,
file target espliciti e test locali.
"""

out_txt.write_text(txt, encoding="utf-8")

print(out_json)
print(out_txt)
print(txt)
