#!/usr/bin/env python3
import json
import re
import shlex
import sys
from pathlib import Path
from datetime import datetime

OUT_DIR = Path("/Users/davidepiangiolino/PROMETEO/data/local_reports/ocr_010")
OUT_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_COMMANDS = {"CONFERMO", "CORREGGO", "SKIP", "DA_VERIFICARE"}
ALLOWED_FIELDS = {
    "REV",
    "QTA_IMBALLO",
    "IMBALLO",
    "LOTTO",
    "DISEGNO",
    "COMPONENTI_ADD",
    "COMPONENTI_REMOVE",
    "ROUTE_ADD",
    "ROUTE_REMOVE",
    "NOTE_TL",
    "MOTIVO",
}

def parse_value(raw):
    raw = raw.strip()
    if "," in raw:
        return [x.strip() for x in raw.split(",") if x.strip()]
    if re.fullmatch(r"\d+", raw):
        return int(raw)
    return raw

def parse_line(line):
    line = line.strip()
    if not line or line.startswith("#"):
        return None

    try:
        parts = shlex.split(line)
    except ValueError as e:
        return {
            "raw": line,
            "valid": False,
            "error": f"SHLEX_ERROR: {e}",
        }

    if len(parts) < 2:
        return {
            "raw": line,
            "valid": False,
            "error": "Formato minimo richiesto: COMANDO ARTICOLO",
        }

    command = parts[0].upper()
    article = parts[1]

    if command not in ALLOWED_COMMANDS:
        return {
            "raw": line,
            "valid": False,
            "error": f"Comando non ammesso: {command}",
        }

    if not re.fullmatch(r"\d{5}", article):
        return {
            "raw": line,
            "valid": False,
            "error": f"Article code non valido: {article}",
        }

    fields = {}
    for token in parts[2:]:
        if "=" not in token:
            return {
                "raw": line,
                "valid": False,
                "error": f"Token correzione non valido: {token}",
            }

        key, value = token.split("=", 1)
        key = key.upper()

        if key not in ALLOWED_FIELDS:
            return {
                "raw": line,
                "valid": False,
                "error": f"Campo non ammesso: {key}",
            }

        fields[key] = parse_value(value)

    risk = "LOW"
    requires_strong_confirmation = False

    if command == "CORREGGO":
        risk = "MEDIUM"
        sensitive_fields = {
            "COMPONENTI_ADD",
            "COMPONENTI_REMOVE",
            "ROUTE_ADD",
            "ROUTE_REMOVE",
        }
        if any(k in fields for k in sensitive_fields):
            risk = "HIGH"
            requires_strong_confirmation = True

    return {
        "raw": line,
        "valid": True,
        "command": command,
        "article_code": article,
        "fields": fields,
        "risk": risk,
        "requires_strong_confirmation": requires_strong_confirmation,
        "writes_to_smf": False,
        "writes_to_database": False,
        "writes_to_planner": False,
        "next_action": "BUILD_DIFF_PREVIEW_ONLY",
    }

def main():
    if len(sys.argv) < 2:
        print("USO: parse_ocr_010_tl_response_preview.py 'CONFERMO 12066'", file=sys.stderr)
        sys.exit(2)

    raw_input_text = " ".join(sys.argv[1:])
    lines = [x for x in raw_input_text.splitlines() if x.strip()]

    result = {
        "status": "PREVIEW_ONLY",
        "capability": "OCR_010_TL_RESPONSE_PARSER_PREVIEW",
        "timestamp": datetime.now().isoformat(),
        "writes_to_smf": False,
        "writes_to_database": False,
        "writes_to_planner": False,
        "parsed": []
    }

    for line in lines:
        parsed = parse_line(line)
        if parsed:
            result["parsed"].append(parsed)

    out = OUT_DIR / "OCR_010_TL_RESPONSE_PARSER_PREVIEW.json"
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    print(out)
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
