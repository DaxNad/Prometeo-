#!/usr/bin/env python3
import json
import re
import shlex
import sys
from pathlib import Path
from datetime import datetime
from copy import deepcopy

OCR007 = Path("/Users/davidepiangiolino/PROMETEO/data/local_reports/ocr_007/OCR_007_SPEC_DENSIFICATION_PREVIEW.json")
OUT_DIR = Path("/Users/davidepiangiolino/PROMETEO/data/local_reports/ocr_011")
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

def parse_command(line):
    parts = shlex.split(line.strip())
    if len(parts) < 2:
        raise ValueError("Formato minimo richiesto: COMANDO ARTICOLO")

    command = parts[0].upper()
    article = parts[1]

    if command not in ALLOWED_COMMANDS:
        raise ValueError(f"Comando non ammesso: {command}")
    if not re.fullmatch(r"\d{5}", article):
        raise ValueError(f"Article code non valido: {article}")

    fields = {}
    for token in parts[2:]:
        if "=" not in token:
            raise ValueError(f"Token correzione non valido: {token}")
        key, value = token.split("=", 1)
        key = key.upper()
        if key not in ALLOWED_FIELDS:
            raise ValueError(f"Campo non ammesso: {key}")
        fields[key] = parse_value(value)

    return command, article, fields

def find_item(article):
    data = json.loads(OCR007.read_text(encoding="utf-8"))
    for item in data["items"]:
        if str(item.get("article_code")) == str(article):
            return item
    return None

def component_codes(item):
    return [str(c.get("code")) for c in item.get("components_preview", []) if c.get("code")]

def apply_preview(before, command, fields):
    after = deepcopy(before)
    changes = []

    if command == "CONFERMO":
        after["tl_confirmation_preview"] = "CONFIRMED_BY_TL_PREVIEW_ONLY"
        changes.append({
            "field": "tl_confirmation_preview",
            "before": None,
            "after": "CONFIRMED_BY_TL_PREVIEW_ONLY"
        })

    elif command == "SKIP":
        old = after.get("article_class_preview")
        after["article_class_preview"] = "SKIPPED_BY_TL_PREVIEW_ONLY"
        changes.append({
            "field": "article_class_preview",
            "before": old,
            "after": after["article_class_preview"]
        })

    elif command == "DA_VERIFICARE":
        old = after.get("article_class_preview")
        after["article_class_preview"] = "DA_VERIFICARE_BY_TL_PREVIEW_ONLY"
        after["tl_block_reason"] = fields.get("MOTIVO")
        changes.append({
            "field": "article_class_preview",
            "before": old,
            "after": after["article_class_preview"]
        })
        changes.append({
            "field": "tl_block_reason",
            "before": None,
            "after": fields.get("MOTIVO")
        })

    elif command == "CORREGGO":
        field_map = {
            "REV": "revision",
            "LOTTO": "lot_quantity",
            "DISEGNO": "drawing",
        }

        for src, dst in field_map.items():
            if src in fields:
                old = after.get(dst)
                after[dst] = fields[src]
                changes.append({"field": dst, "before": old, "after": after[dst]})

        if "IMBALLO" in fields:
            old = after.get("packaging", {}).get("package_code")
            after.setdefault("packaging", {})["package_code"] = fields["IMBALLO"]
            changes.append({"field": "packaging.package_code", "before": old, "after": fields["IMBALLO"]})

        if "QTA_IMBALLO" in fields:
            old = after.get("packaging", {}).get("package_quantity")
            after.setdefault("packaging", {})["package_quantity"] = fields["QTA_IMBALLO"]
            changes.append({"field": "packaging.package_quantity", "before": old, "after": fields["QTA_IMBALLO"]})

        if "COMPONENTI_ADD" in fields:
            existing = set(component_codes(after))
            add_values = fields["COMPONENTI_ADD"]
            if not isinstance(add_values, list):
                add_values = [add_values]
            for code in add_values:
                if str(code) not in existing:
                    after.setdefault("components_preview", []).append({
                        "code": str(code),
                        "description": None,
                        "confidence": "TL_CORRECTION_PREVIEW"
                    })
                    changes.append({"field": "components_preview", "before": None, "after": str(code)})

        if "COMPONENTI_REMOVE" in fields:
            remove_values = fields["COMPONENTI_REMOVE"]
            if not isinstance(remove_values, list):
                remove_values = [remove_values]
            before_codes = component_codes(after)
            after["components_preview"] = [
                c for c in after.get("components_preview", [])
                if str(c.get("code")) not in {str(x) for x in remove_values}
            ]
            after_codes = component_codes(after)
            changes.append({"field": "components_preview", "before": before_codes, "after": after_codes})

        if "ROUTE_ADD" in fields:
            add_values = fields["ROUTE_ADD"]
            if not isinstance(add_values, list):
                add_values = [add_values]
            for step in add_values:
                if step not in after.setdefault("route_preview", []):
                    after["route_preview"].append(step)
                    changes.append({"field": "route_preview", "before": None, "after": step})

        if "ROUTE_REMOVE" in fields:
            remove_values = fields["ROUTE_REMOVE"]
            if not isinstance(remove_values, list):
                remove_values = [remove_values]
            before_route = list(after.get("route_preview", []))
            after["route_preview"] = [x for x in before_route if x not in remove_values]
            changes.append({"field": "route_preview", "before": before_route, "after": after["route_preview"]})

        if "NOTE_TL" in fields:
            old = after.get("note_tl")
            after["note_tl"] = fields["NOTE_TL"]
            changes.append({"field": "note_tl", "before": old, "after": fields["NOTE_TL"]})

    after["planner_eligible"] = False
    after["planner_block_reason"] = "Diff preview only: nessuna modifica applicata."

    return after, changes

def risk_for(command, fields):
    if command == "CORREGGO":
        high_fields = {"COMPONENTI_ADD", "COMPONENTI_REMOVE", "ROUTE_ADD", "ROUTE_REMOVE"}
        if any(k in fields for k in high_fields):
            return "HIGH", True
        return "MEDIUM", False
    return "LOW", False

def main():
    if len(sys.argv) < 2:
        print("USO: build_ocr_011_diff_preview.py 'CORREGGO 12102 REV=9 QTA_IMBALLO=30'", file=sys.stderr)
        sys.exit(2)

    raw = " ".join(sys.argv[1:])
    command, article, fields = parse_command(raw)

    before = find_item(article)
    if not before:
        raise SystemExit(f"Articolo non trovato in OCR_007: {article}")

    after, changes = apply_preview(before, command, fields)
    risk, strong = risk_for(command, fields)

    result = {
        "status": "PREVIEW_ONLY",
        "capability": "OCR_011_DIFF_PREVIEW_BUILDER",
        "timestamp": datetime.now().isoformat(),
        "raw_command": raw,
        "article_code": article,
        "command": command,
        "risk": risk,
        "requires_strong_confirmation": strong,
        "writes_to_smf": False,
        "writes_to_database": False,
        "writes_to_planner": False,
        "before": before,
        "after": after,
        "changes": changes,
        "next_action": (
            f"REQUIRE_STRONG_CONFIRMATION: CONFERMO MODIFICA {article}"
            if strong else
            "READY_FOR_LIGHT_CONFIRMATION_PREVIEW"
        )
    }

    out = OUT_DIR / f"OCR_011_DIFF_PREVIEW_{article}.json"
    txt = OUT_DIR / f"OCR_011_DIFF_PREVIEW_{article}.txt"

    out.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = []
    lines.append("OCR_011 DIFF PREVIEW")
    lines.append("=" * 80)
    lines.append(f"STATUS: {result['status']}")
    lines.append(f"ARTICLE: {article}")
    lines.append(f"COMMAND: {command}")
    lines.append(f"RISK: {risk}")
    lines.append(f"REQUIRES_STRONG_CONFIRMATION: {strong}")
    lines.append("NO SMF / NO DATABASE / NO PLANNER")
    lines.append("")
    lines.append("CHANGES")
    for c in changes:
        lines.append(f"- {c['field']}: {c['before']} -> {c['after']}")
    lines.append("")
    lines.append(f"NEXT_ACTION: {result['next_action']}")

    txt.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(out)
    print(txt)
    print(txt.read_text(encoding="utf-8"))

if __name__ == "__main__":
    main()
