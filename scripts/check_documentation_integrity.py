#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "docs" / "DOCUMENTATION_CATALOG.md"
ROOTS = (ROOT / "docs", ROOT / "board", ROOT / "memory")
LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def main() -> int:
    errors: list[str] = []
    markdown = sorted(path for root in ROOTS for path in root.rglob("*.md"))
    catalog_text = CATALOG.read_text(encoding="utf-8") if CATALOG.is_file() else ""

    for path in markdown:
        relative = path.relative_to(ROOT).as_posix()
        if f"`{relative}`" not in catalog_text:
            errors.append(f"not cataloged: {relative}")

        text = path.read_text(encoding="utf-8")
        for target in LINK.findall(text):
            target = target.split("#", 1)[0].strip()
            if not target or "://" in target or target.startswith(("mailto:", "#")):
                continue
            resolved = (path.parent / target).resolve()
            try:
                resolved.relative_to(ROOT)
            except ValueError:
                errors.append(f"link escapes repository: {relative} -> {target}")
                continue
            if not resolved.exists():
                errors.append(f"broken link: {relative} -> {target}")

    required = (
        "docs/PROMETEO_MASTER.md",
        "docs/architecture/PROMETEO_MANIFESTO_v1.md",
        "docs/CURRENT_STATE.md",
        "docs/DOCUMENTATION_GOVERNANCE.md",
    )
    for path in required:
        if f"`{path}`" not in catalog_text:
            errors.append(f"canonical document missing from catalog: {path}")

    if errors:
        print("[PROMETEO DOCUMENTATION INTEGRITY] FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"[PROMETEO DOCUMENTATION INTEGRITY] OK files={len(markdown)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

