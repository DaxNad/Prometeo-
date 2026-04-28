#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ALLOWED = {
    "specs_finitura/index.json",
    "specs_finitura/_templates/metadata.template.json",
}

BLOCKED_SUFFIXES = {
    ".png", ".jpg", ".jpeg", ".pdf", ".heic", ".webp", ".tif", ".tiff"
}

def tracked_files() -> list[str]:
    result = subprocess.run(
        ["git", "ls-files"],
        capture_output=True,
        text=True,
        check=True,
    )
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]

def main() -> int:
    violations: list[str] = []

    for path in tracked_files():
        if not path.startswith("specs_finitura/"):
            continue

        if path in ALLOWED:
            continue

        p = Path(path)

        if p.name == "metadata.json":
            violations.append(path)
            continue

        if p.suffix.lower() in BLOCKED_SUFFIXES:
            violations.append(path)
            continue

        # Default-deny: anything under article folders is private unless explicitly allowed.
        parts = p.parts
        if len(parts) >= 2 and parts[0] == "specs_finitura" and not parts[1].startswith("_"):
            violations.append(path)

    if violations:
        print("[PROMETEO PRIVACY GUARD] REPOSITORY VIOLATION")
        print("Le specifiche di finitura sono materiale strettamente privato e non divulgabile.")
        print("Sono vietati file articolo, immagini, PDF e metadata locali sotto specs_finitura.")
        print("")
        print("File vietati tracciati:")
        for v in violations:
            print(f" - {v}")
        print("")
        print("Consentiti solo:")
        for a in sorted(ALLOWED):
            print(f" - {a}")
        return 1

    print("[PROMETEO PRIVACY GUARD] OK")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
