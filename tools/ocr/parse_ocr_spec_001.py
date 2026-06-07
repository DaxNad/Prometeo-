#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path

KNOWN_COMPONENTS = {
    "468922": "guaina",
    "469122": "HENN",
    "468728": "rapido / innesto",
    "468796": "O-ring",
    "468786": "molletta plastica / gommotto",
    "467660": "sacchetto",
}

KNOWN_OPERATIONS = [
    ("LAVAGGIO", "LAVAGGIO"),
    ("COLLAUDO VISIVO", "CONTROLLO_VISIVO"),
    ("INSERIMENTO GUAINA", "INSERIMENTO_GUAINA"),
    ("MARCATURA", "MARCATURA"),
    ("MACCHINA HENN", "HENN"),
    ("INSERIMENTO INNESTO RAPIDO", "INSERIMENTO_INNESTO_RAPIDO"),
    ("MACCHINA CRIMP RING ZAW", "ZAW1_DA_CONFERMARE"),
    ("BANCO ASSEMBL PIDMILL", "PIDMILL"),
    ("COLLAUDO A PRESSIONE", "COLLAUDO_PRESSIONE"),
    ("VERTICALE", "COLLAUDO_PRESSIONE_VERTICALE"),
    ("SACCHETTO", "SACCHETTO"),
]

def normalize_text(lines):
    return "\n".join(line.get("text", "") for line in lines)

def compact_digits(s):
    return re.sub(r"\D+", "", s)

def find_article(lines):
    texts = [x.get("text", "") for x in lines]
    for i, t in enumerate(texts):
        if "ARTICOLO" in t.upper() and i + 1 < len(texts):
            m = re.search(r"\b\d{5}\b", texts[i + 1])
            if m:
                return m.group(0)
    for t in texts:
        m = re.search(r"\b\d{5}\b", t)
        if m:
            return m.group(0)
    return None

def find_drawing(lines):
    texts = [x.get("text", "") for x in lines]
    for i, t in enumerate(texts):
        if "DISEGNO" in t.upper() and i + 1 < len(texts):
            raw = texts[i + 1]
            digits = compact_digits(raw)
            if len(digits) >= 10:
                return digits
    return None

def find_revision(lines):
    texts = [x.get("text", "") for x in lines]
    for i, t in enumerate(texts):
        if t.strip().upper() == "REV." and i + 1 < len(texts):
            m = re.search(r"\d+", texts[i + 1])
            if m:
                return m.group(0)
    return None

def find_lot_quantity(lines):
    texts = [x.get("text", "") for x in lines]
    for i, t in enumerate(texts):
        if "Q.TA" in t.upper():
            for j in range(i + 1, min(i + 4, len(texts))):
                raw = texts[j].strip()
                if re.fullmatch(r"\d{2,4}", raw):
                    value = int(raw)
                    if value < 1000:
                        return value
    return None

def find_package_code(lines):
    texts = [x.get("text", "") for x in lines]
    for i, t in enumerate(texts):
        if t.strip().upper() == "IMBALLO":
            for j in range(i + 1, min(i + 3, len(texts))):
                raw = texts[j].strip()
                if re.fullmatch(r"\d{4,5}", raw):
                    return int(raw)
    return None

def find_package_quantity(lines):
    texts = [x.get("text", "") for x in lines]
    for i, t in enumerate(texts):
        if t.strip().upper() == "QUANTITA":
            for j in range(i + 1, min(i + 3, len(texts))):
                raw = texts[j].strip()
                if re.fullmatch(r"\d{1,3}", raw):
                    return int(raw)
    return None

def detect_components(text):
    fixed = text.replace("4G8728", "468728")
    found = []
    for code, desc in KNOWN_COMPONENTS.items():
        if code in fixed:
            found.append({
                "code": code,
                "description": desc,
                "confidence": "CERTO" if code != "468728" else "INFERITO_DA_OCR_CORRETTO"
            })
    return found

def detect_operations(text):
    upper = text.upper()
    result = []
    seen = set()
    for needle, op in KNOWN_OPERATIONS:
        if needle in upper and op not in seen:
            result.append(op)
            seen.add(op)
    return result

def main():
    if len(sys.argv) != 2:
        print("USO: parse_ocr_spec_001.py /path/ocr_preview.json", file=sys.stderr)
        sys.exit(2)

    src = Path(sys.argv[1])
    data = json.loads(src.read_text(encoding="utf-8"))
    lines = data.get("lines", [])
    text = normalize_text(lines)

    article_code = find_article(lines)
    route_preview = detect_operations(text)
    components = detect_components(text)

    if article_code and article_code.startswith("500") and not route_preview and not components:
        document_type = "COMPONENT_500XX_OR_NON_STANDARD"
        parse_quality = "SKIP_DOCUMENT_TYPE"
    else:
        document_type = "SPECIFICA_FINITURA_STANDARD_CANDIDATE"
        parse_quality = "PARSED_PREVIEW"

    structured = {
        "status": "PREVIEW_ONLY",
        "document_type": document_type,
        "parse_quality": parse_quality,
        "source_ocr_json": str(src),
        "source_image": data.get("source_file"),
        "article_code": article_code,
        "drawing": find_drawing(lines),
        "revision": find_revision(lines),
        "lot_quantity": find_lot_quantity(lines),
        "package_code": find_package_code(lines),
        "package_quantity": find_package_quantity(lines),
        "components": components,
        "route_preview": route_preview,
        "warnings": [
            "Preview OCR: non scrive su SMF/database/planner.",
            "ZAW rilevata da testo macchina CRIMP RING ZAW: classificata da confermare, non come ZAW2 automatica.",
            "Codici OCR sporchi possono essere corretti solo se presenti in registry noto."
        ]
    }

    out = src.with_name(src.stem + "_structured.json")
    out.write_text(json.dumps(structured, indent=2, ensure_ascii=False), encoding="utf-8")
    print(out)

if __name__ == "__main__":
    main()
