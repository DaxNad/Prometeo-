#!/usr/bin/env python3
import json
from pathlib import Path
from datetime import datetime

SRC = Path("/Users/davidepiangiolino/PROMETEO/data/local_reports/ocr_007/OCR_007_SPEC_DENSIFICATION_PREVIEW.json")
OUT_DIR = Path("/Users/davidepiangiolino/PROMETEO/data/local_reports/ocr_parser_001")
OUT_DIR.mkdir(parents=True, exist_ok=True)

data = json.loads(SRC.read_text(encoding="utf-8"))

def codes(item):
    return [str(c.get("code")) for c in item.get("components_preview", []) if c.get("code")]

def classify(item):
    article = str(item.get("article_code"))
    quality = item.get("quality")
    route = item.get("route_preview", [])
    comps = codes(item)

    rules = []
    missing = []
    conflicts = []
    confidence = "DA_VERIFICARE"
    domain_quality = "PARTIAL"

    if article.startswith("500"):
        return {
            "article_code": article,
            "input_quality": quality,
            "domain_quality": "SKIP_DOCUMENT_TYPE",
            "article_class_preview": "COMPONENT_REFERENCE_ONLY",
            "confidence": "DA_VERIFICARE",
            "known_domain_rules_applied": ["500xx escluso dal parser standard"],
            "components_preview": item.get("components_preview", []),
            "route_preview": route,
            "missing_fields": [],
            "conflicts": [],
            "planner_eligible": False,
            "requires_tl_confirmation": False,
        }

    if "COLLAUDO_PRESSIONE_VERTICALE" in route:
        rules.append("Collaudo verticale trattato come modalità CP, non postazione autonoma")

    if "ZAW1_DA_CONFERMARE" in route:
        rules.append("ZAW rilevata genericamente: non inferire ZAW2 automaticamente")

    if "COLLAUDO_PRESSIONE" in route:
        rules.append("CP considerato collaudo pressione finale quando presente")

    if article == "12066":
        rules.append("12066: profilo OCR coerente con route nota preview")
        if quality == "PASS" and len(comps) >= 5 and len(route) >= 8:
            domain_quality = "PASS_DOMAIN_PREVIEW"
            confidence = "INFERITO"
            rules.append("Preview OCR subordinata: non promuovere automaticamente a CERTO")
        else:
            domain_quality = "PARTIAL"
            confidence = "DA_VERIFICARE"

    elif article == "12056":
        rules.append("12056: non inferire HENN automaticamente da OCR parziale")
        rules.append("12056: route OCR parziale, richiede controllo TL")
        domain_quality = "PARTIAL_DOMAIN_REVIEW_REQUIRED"
        confidence = "DA_VERIFICARE"
        if len(comps) < 3:
            missing.append("COMPONENTI")
        if len(route) < 5:
            missing.append("ROUTE")
        if "HENN" in route:
            conflicts.append("HENN presente in preview: da verificare perché 12056 non ha HENN nella specifica iniziale")

    elif article == "12102":
        rules.append("12102: componenti/route buoni ma metadati incompleti mantengono review")
        domain_quality = "PARTIAL_DOMAIN_REVIEW_REQUIRED"
        confidence = "DA_VERIFICARE"
        if item.get("revision") in (None, "", []):
            missing.append("REV")
        if item.get("packaging", {}).get("package_quantity") in (None, "", []):
            missing.append("QTA_IMBALLO")

    else:
        domain_quality = "UNKNOWN_DOMAIN_REVIEW_REQUIRED"
        confidence = "DA_VERIFICARE"
        rules.append("Articolo non ancora coperto da regole dominio OCR_PARSER_001")

    return {
        "article_code": article,
        "input_quality": quality,
        "domain_quality": domain_quality,
        "article_class_preview": item.get("article_class_preview"),
        "confidence": confidence,
        "known_domain_rules_applied": rules,
        "components_preview": item.get("components_preview", []),
        "route_preview": route,
        "missing_fields": missing,
        "conflicts": conflicts,
        "planner_eligible": False,
        "requires_tl_confirmation": confidence != "CERTO",
    }

out = {
    "status": "PREVIEW_ONLY",
    "capability": "OCR_PARSER_001_DOMAIN_PREVIEW",
    "timestamp": datetime.now().isoformat(),
    "writes_to_smf": False,
    "writes_to_database": False,
    "writes_to_planner": False,
    "items": [classify(item) for item in data.get("items", [])]
}

json_out = OUT_DIR / "OCR_PARSER_001_DOMAIN_PREVIEW.json"
txt_out = OUT_DIR / "OCR_PARSER_001_DOMAIN_PREVIEW.txt"

json_out.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")

lines = ["OCR_PARSER_001 DOMAIN PREVIEW", "=" * 80, "STATUS: PREVIEW_ONLY", "NO SMF / NO DATABASE / NO PLANNER", ""]
for item in out["items"]:
    lines.append("-" * 80)
    lines.append(f"ARTICLE: {item['article_code']}")
    lines.append(f"INPUT_QUALITY: {item['input_quality']}")
    lines.append(f"DOMAIN_QUALITY: {item['domain_quality']}")
    lines.append(f"CONFIDENCE: {item['confidence']}")
    lines.append(f"PLANNER_ELIGIBLE: {item['planner_eligible']}")
    lines.append(f"REQUIRES_TL_CONFIRMATION: {item['requires_tl_confirmation']}")
    lines.append(f"MISSING: {item['missing_fields']}")
    lines.append(f"CONFLICTS: {item['conflicts']}")
    lines.append(f"RULES: {item['known_domain_rules_applied']}")

txt_out.write_text("\n".join(lines) + "\n", encoding="utf-8")

print(json_out)
print(txt_out)
print(txt_out.read_text(encoding="utf-8"))
