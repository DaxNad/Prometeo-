from __future__ import annotations

import json
from pathlib import Path

from app.domain.finishing_specs_densifier import build_densification_preview


ROOT = Path(__file__).resolve().parents[1]
SPECS_ROOT = ROOT / "specs_finitura"
OUT = ROOT / "data" / "local_reports" / "finishing_specs_densification_preview.json"


def _load_metadata(record: dict):
    path = ROOT / str(record.get("metadata_path", ""))
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    preview = build_densification_preview(SPECS_ROOT, metadata_loader=_load_metadata)
    OUT.write_text(json.dumps(preview, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print("PREVIEW_OK", OUT.relative_to(ROOT))
    print("records_count:", preview["records_count"])
    print("counts:", preview["counts"])

    for item in preview["results"]:
        if item["classification"] != "ALREADY_AUTHORITATIVE":
            print(
                item["article"],
                "|",
                item["classification"],
                "|",
                ",".join(item["reasons"]),
            )


if __name__ == "__main__":
    main()
