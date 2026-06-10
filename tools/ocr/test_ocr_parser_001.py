#!/usr/bin/env python3
import json
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]

p = PROJECT_ROOT / "data/local_reports/ocr_parser_001/OCR_PARSER_001_DOMAIN_PREVIEW.json"
if not p.exists():
    pytest.skip(
        "OCR_PARSER_001 local preview report not present; run tools/ocr/build_ocr_parser_001_domain_preview.py first.",
        allow_module_level=True,
    )

data = json.loads(p.read_text(encoding="utf-8"))

items = {str(x["article_code"]): x for x in data["items"]}

assert data["writes_to_smf"] is False
assert data["writes_to_database"] is False
assert data["writes_to_planner"] is False

assert items["12066"]["planner_eligible"] is False
assert items["12066"]["confidence"] == "INFERITO"
assert items["12066"]["domain_quality"] == "PASS_DOMAIN_PREVIEW"
assert items["12066"]["requires_tl_confirmation"] is True

assert items["12056"]["confidence"] == "DA_VERIFICARE"
assert items["12056"]["planner_eligible"] is False
assert "COMPONENTI" in items["12056"]["missing_fields"]
assert "ROUTE" in items["12056"]["missing_fields"]

assert items["12102"]["confidence"] == "DA_VERIFICARE"
assert "REV" in items["12102"]["missing_fields"]
assert "QTA_IMBALLO" in items["12102"]["missing_fields"]

assert items["50034"]["article_class_preview"] == "COMPONENT_REFERENCE_ONLY"
assert items["50036"]["article_class_preview"] == "COMPONENT_REFERENCE_ONLY"

print("OCR_PARSER_001 TEST PASS")
