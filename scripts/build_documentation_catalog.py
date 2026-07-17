#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "DOCUMENTATION_CATALOG.md"
ROOTS = (ROOT / "docs", ROOT / "board", ROOT / "memory")

CANONICAL = {
    "docs/DOCUMENTATION_CATALOG.md",
    "docs/DOCUMENTATION_GOVERNANCE.md",
    "docs/CURRENT_STATE.md",
    "docs/PROMETEO_MASTER.md",
    "docs/architecture/PROMETEO_MANIFESTO_v1.md",
}

ACTIVE = {
    "docs/PROMETEO_DEVELOPMENT_CLOSURE_CANON_001.md",
    "docs/PROMETEO_INPUT_INTERFACE_V1.md",
    "docs/PROMETEO_PATTERN_LEARNING_IMPERATIVE.md",
    "docs/PROMETEO_PRODUCT_COMPLETE_ROADMAP_V1.md",
    "docs/RUNTIME_OPERATION_GUIDE_001.md",
    "memory/README_MEMORY.md",
    "memory/domain/invariants.md",
    "memory/retrieval/retrieval_policy.md",
}

SUPERSEDED = {
    "docs/PRODUCT_READINESS_AUDIT_001.md": "docs/CURRENT_STATE.md",
    "docs/PROMETEO_PRODUCT_CORE_CLOSURE_V1.md": "docs/CURRENT_STATE.md",
    "docs/PROMETEO_GOAL_MAP.md": "docs/CURRENT_STATE.md",
    "docs/PROMETEO_CAPABILITY_MATRIX.md": "docs/CURRENT_STATE.md",
    "board/MASTER_CONTROL.md": "docs/CURRENT_STATE.md",
    "board/TASK_BOARD.md": "docs/CURRENT_STATE.md",
    "memory/project_state.md": "docs/CURRENT_STATE.md",
    "memory/capabilities/capability_status.md": "docs/CURRENT_STATE.md",
}

ARCHIVED = {
    "docs/BACKEND_FREEZE_v1.md",
    "docs/POSTGRESQL_CONSOLIDATION_v1.md",
}

CLASSIFICATION_OVERRIDES = {
    "docs/PROMETEO_PORTABLE_WORK_METHOD_001.md": {
        "lifecycle": "ACTIVE",
    },
    "docs/capabilities/PRODUCTION_PROGRAM_IMAGE_OCR_UI_INTAKE_VERTICAL_SLICE_001.md": {
        "category": "EVIDENCE",
        "lifecycle": "ARCHIVED",
    },
    "docs/capabilities/TL_CHAT_PRODUCTION_SPEC_SUMMARY_001.md": {
        "category": "EVIDENCE",
        "lifecycle": "ARCHIVED",
    },
    "docs/capabilities/TL_CHAT_UNIFIED_DATA_ACCESS_001.md": {
        "category": "EVIDENCE",
        "lifecycle": "ARCHIVED",
    },
    "docs/capabilities/TL_CHAT_UNIFIED_DATA_ACCESS_VERTICAL_SLICE_002.md": {
        "category": "EVIDENCE",
        "lifecycle": "ARCHIVED",
    },
    "docs/capabilities/TL_CHAT_UNIFIED_DATA_ACCESS_VERTICAL_SLICE_003.md": {
        "category": "EVIDENCE",
        "lifecycle": "ARCHIVED",
    },
    "docs/capabilities/TL_CHAT_UNIFIED_DATA_ACCESS_VERTICAL_SLICE_004.md": {
        "category": "EVIDENCE",
        "lifecycle": "ARCHIVED",
    },
    "docs/capabilities/PRODUCTION_PROGRAM_IMAGE_OCR_API_INTAKE_001.md": {
        "category": "CONTRACT",
    },
    "docs/capabilities/PRODUCTION_PROGRAM_IMAGE_OCR_INTAKE_001.md": {
        "category": "CONTRACT",
    },
    "docs/capabilities/PRODUCTION_PROGRAM_IMAGE_OCR_UI_INTAKE_001.md": {
        "category": "CONTRACT",
    },
}


def lifecycle(path: str) -> tuple[str, str]:
    override = CLASSIFICATION_OVERRIDES.get(path, {})
    if "lifecycle" in override:
        return override["lifecycle"], ""
    if path in CANONICAL:
        return "CANONICAL", ""
    if path in SUPERSEDED:
        return "SUPERSEDED", SUPERSEDED[path]
    if path in ACTIVE:
        return "ACTIVE", ""
    if path in ARCHIVED:
        return "ARCHIVED", ""
    name = Path(path).name.upper()
    if "HANDOFF" in name or "SNAPSHOT" in name or "CLOSURE" in name or "AUDIT_20" in name:
        return "ARCHIVED", ""
    if "/MEMORY_ARCHIVE/" in path.upper() or path.startswith("board/"):
        return "ARCHIVED", ""
    if any(token in name for token in ("CONTRACT", "POLICY", "GOVERNANCE", "GUIDE", "PROTOCOL")):
        return "ACTIVE", ""
    return "REFERENCE", ""


def function(path: str) -> str:
    override = CLASSIFICATION_OVERRIDES.get(path, {})
    if "category" in override:
        return override["category"]
    name = Path(path).name.upper()
    if path == "docs/CURRENT_STATE.md":
        return "STATE"
    if path in CANONICAL or any(token in name for token in ("MASTER", "GOVERNANCE", "POLICY", "CONSTITUTION")):
        return "GOVERNANCE"
    if path == "docs/CURRENT_STATE.md" or "STATE" in name or path.startswith("board/"):
        return "STATE"
    if "CONTRACT" in name or "BINDING" in name or "GATE" in name:
        return "CONTRACT"
    if any(token in name for token in ("GUIDE", "SETUP", "BOOT", "README")):
        return "HOW_TO"
    if "/DECISIONS/" in path.upper() or "/ADR" in path.upper():
        return "DECISION"
    if any(token in name for token in ("CLOSURE", "AUDIT", "VALIDATION", "CHECKPOINT", "PILOT")):
        return "EVIDENCE"
    if "/MEMORY_ARCHIVE/" in path.upper() or "SNAPSHOT" in name or "HANDOFF" in name:
        return "ARCHIVE"
    return "REFERENCE"


def title(path: Path) -> str:
    if path == OUTPUT and not path.exists():
        return "PROMETEO Documentation Catalog"
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.startswith("# "):
                return line[2:].strip().replace("|", "\\|")
    except UnicodeDecodeError:
        pass
    return path.stem.replace("_", " ")


def render_catalog() -> str:
    paths = sorted(
        path
        for root in ROOTS
        for path in root.rglob("*.md")
        if path != OUTPUT
    )
    paths.append(OUTPUT)
    paths.sort()

    rows: list[tuple[str, str, str, str, str]] = []
    for absolute in paths:
        relative = absolute.relative_to(ROOT).as_posix()
        state, replacement = lifecycle(relative)
        rows.append((function(relative), state, relative, title(absolute), replacement))

    lines = [
        "# PROMETEO Documentation Catalog",
        "",
        "Lifecycle: `CANONICAL`",
        "",
        "Indice deterministico di tutti i documenti sotto `docs/`, `board/` e `memory/`.",
        "La policy di lettura è definita in `docs/DOCUMENTATION_GOVERNANCE.md`.",
        "",
        "## Percorso rapido",
        "",
        "1. `docs/PROMETEO_MASTER.md` — autorità semantica.",
        "2. `docs/architecture/PROMETEO_MANIFESTO_v1.md` — architettura.",
        "3. `docs/CURRENT_STATE.md` — stato corrente.",
        "4. Contratto `ACTIVE` della capability interessata.",
        "5. Evidence e archive solo per ricostruzione storica.",
        "",
        "## Catalogo completo",
        "",
        "| Funzione | Lifecycle | Documento | Titolo | Sostituito da |",
        "|---|---|---|---|---|",
    ]
    for doc_function, state, path, doc_title, replacement in rows:
        lines.append(
            f"| `{doc_function}` | `{state}` | `{path}` | {doc_title} | `{replacement}` |"
        )
    lines.extend(
        [
            "",
            f"Totale documenti catalogati: **{len(rows)}**.",
            "",
            "File generato da `scripts/build_documentation_catalog.py`; non modificare le righe manualmente.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = render_catalog()

    if args.check:
        current = OUTPUT.read_text(encoding="utf-8") if OUTPUT.is_file() else ""
        if current != rendered:
            print("[PROMETEO DOCUMENTATION CATALOG] FAIL stale generated catalog")
            print("Run: make docs-catalog")
            return 1
        print("[PROMETEO DOCUMENTATION CATALOG] OK")
        return 0

    OUTPUT.write_text(rendered, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
