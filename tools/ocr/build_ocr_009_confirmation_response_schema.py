#!/usr/bin/env python3
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
from datetime import datetime

OUT_DIR = PROJECT_ROOT / "data/local_reports/ocr_009"
OUT_DIR.mkdir(parents=True, exist_ok=True)

schema = {
    "status": "PREVIEW_ONLY",
    "capability": "OCR_009_CONFIRMATION_RESPONSE_SCHEMA",
    "timestamp": datetime.now().isoformat(),
    "writes_to_smf": False,
    "writes_to_database": False,
    "writes_to_planner": False,
    "allowed_commands": [
        {
            "command": "CONFERMO",
            "syntax": "CONFERMO <article_code>",
            "meaning": "Il TL conferma la preview così com'è.",
            "risk": "LOW"
        },
        {
            "command": "CORREGGO",
            "syntax": "CORREGGO <article_code> FIELD=VALUE FIELD=VALUE",
            "meaning": "Il TL propone correzioni. Produce solo diff preview.",
            "risk": "MEDIUM"
        },
        {
            "command": "SKIP",
            "syntax": "SKIP <article_code>",
            "meaning": "Il TL conferma esclusione dal parser standard.",
            "risk": "LOW"
        },
        {
            "command": "DA_VERIFICARE",
            "syntax": "DA_VERIFICARE <article_code> MOTIVO=\"testo\"",
            "meaning": "Il TL blocca il dato per verifica.",
            "risk": "LOW"
        }
    ],
    "allowed_fields_for_correction": [
        "REV",
        "QTA_IMBALLO",
        "IMBALLO",
        "LOTTO",
        "DISEGNO",
        "COMPONENTI_ADD",
        "COMPONENTI_REMOVE",
        "ROUTE_ADD",
        "ROUTE_REMOVE",
        "NOTE_TL"
    ],
    "examples": [
        "CONFERMO 12066",
        "CORREGGO 12102 REV=9 QTA_IMBALLO=30",
        "CORREGGO 12056 COMPONENTI_ADD=468922,469122 ROUTE_ADD=HENN,PIDMILL,COLLAUDO_PRESSIONE",
        "SKIP 50034",
        "DA_VERIFICARE 12056 MOTIVO=\"route incompleta da specifica OCR\""
    ],
    "hard_rules": [
        "Questa capability non applica modifiche.",
        "Ogni risposta TL produce solo una preview/diff.",
        "planner_eligible resta sempre false.",
        "Correzioni route/componenti richiedono conferma successiva forte.",
        "ZAW2 non può essere aggiunta automaticamente da OCR.",
        "SPECIFICA + TL restano fonti autorevoli."
    ]
}

out_json = OUT_DIR / "OCR_009_CONFIRMATION_RESPONSE_SCHEMA.json"
out_txt = OUT_DIR / "OCR_009_CONFIRMATION_RESPONSE_SCHEMA.txt"

out_json.write_text(json.dumps(schema, indent=2, ensure_ascii=False), encoding="utf-8")

lines = []
lines.append("OCR_009 CONFIRMATION RESPONSE SCHEMA")
lines.append("=" * 80)
lines.append("STATUS: PREVIEW_ONLY")
lines.append("NO SMF / NO DATABASE / NO PLANNER")
lines.append("")
lines.append("COMMANDS")
for c in schema["allowed_commands"]:
    lines.append(f"- {c['syntax']} | {c['meaning']} | RISK={c['risk']}")

lines.append("")
lines.append("ALLOWED CORRECTION FIELDS")
for f in schema["allowed_fields_for_correction"]:
    lines.append(f"- {f}")

lines.append("")
lines.append("EXAMPLES")
for e in schema["examples"]:
    lines.append(f"- {e}")

lines.append("")
lines.append("HARD RULES")
for r in schema["hard_rules"]:
    lines.append(f"- {r}")

out_txt.write_text("\n".join(lines) + "\n", encoding="utf-8")

print(out_json)
print(out_txt)
