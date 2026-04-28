#!/usr/bin/env python3
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ALLOWED_TRACKED = {
    "specs_finitura/index.json",
    "specs_finitura/_templates/metadata.template.json",
    "scripts/privacy_guard_specs.py",
    ".github/workflows/privacy-guard.yml",
}

PROTECTED_GUARD_FILES = {
    "scripts/privacy_guard_specs.py",
    ".github/workflows/privacy-guard.yml",
}

SENSITIVE_ROOTS = {
    "specs_finitura",
}

BLOCKED_PRIVATE_SUFFIXES = {
    ".png",
    ".jpg",
    ".jpeg",
    ".pdf",
    ".heic",
    ".webp",
    ".tif",
    ".tiff",
    ".zip",
    ".7z",
    ".tar",
    ".gz",
    ".rar",
}

SUSPICIOUS_PRIVATE_NAMES = {
    "metadata.json",
}

SUSPICIOUS_PATH_TOKENS = {
    "spec",
    "specs",
    "specifica",
    "specifiche",
    "finitura",
    "photo",
    "photos",
    "foto",
    "image",
    "images",
    "screenshot",
}


def run_git(args: list[str]) -> list[str]:
    result = subprocess.run(
        ["git", *args],
        capture_output=True,
        text=True,
        check=True,
    )
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def tracked_files() -> list[str]:
    return run_git(["ls-files"])


def changed_files() -> set[str]:
    try:
        return set(run_git(["diff", "--name-only", "origin/main...HEAD"]))
    except Exception:
        return set(run_git(["diff", "--name-only", "HEAD~1...HEAD"]))


def is_under_specs_finitura(path: str) -> bool:
    return path.startswith("specs_finitura/")


def is_article_local_file(path: str) -> bool:
    p = Path(path)
    parts = p.parts
    return len(parts) >= 2 and parts[0] == "specs_finitura" and not parts[1].startswith("_")


def has_suspicious_path_token(path: str) -> bool:
    lowered = path.lower()
    return any(token in lowered for token in SUSPICIOUS_PATH_TOKENS)


def main() -> int:
    violations: list[str] = []
    guard_modifications: list[str] = []

    files = tracked_files()
    changed = changed_files()

    for guard_file in PROTECTED_GUARD_FILES:
        if guard_file in changed and os.getenv("PROMETEO_ALLOW_PRIVACY_GUARD_EDIT") != "1":
            guard_modifications.append(guard_file)

    for path in files:
        if path in ALLOWED_TRACKED:
            continue

        p = Path(path)
        suffix = p.suffix.lower()
        name = p.name.lower()

        # Regola più dura: qualsiasi file articolo sotto specs_finitura è privato
        # salvo eccezioni esplicite in ALLOWED_TRACKED.
        if is_article_local_file(path):
            violations.append(path)
            continue

        # Blocca immagini/documenti/archivi se appaiono in percorsi sospetti.
        if suffix in BLOCKED_PRIVATE_SUFFIXES and has_suspicious_path_token(path):
            violations.append(path)
            continue

        # Blocca metadata locali sospetti in percorsi sensibili.
        if name in SUSPICIOUS_PRIVATE_NAMES and has_suspicious_path_token(path):
            violations.append(path)
            continue

    if guard_modifications:
        non_guard_changes = sorted(changed - PROTECTED_GUARD_FILES)

        if non_guard_changes and os.getenv("PROMETEO_ALLOW_PRIVACY_GUARD_EDIT") != "1":
            print("[PROMETEO PRIVACY GUARD] BLOCCO MODIFICA GUARD")
            print("I file di protezione privacy non possono essere modificati insieme ad altre modifiche.")
            print("Le modifiche al guard devono stare in PR dedicata.")
            print("")
            print("File guard modificati:")
            for v in guard_modifications:
                print(f" - {v}")
            print("")
            print("Altri file modificati nella stessa PR:")
            for v in non_guard_changes:
                print(f" - {v}")
            print("")
            print("Override locale consentito solo per manutenzione controllata:")
            print("  PROMETEO_ALLOW_PRIVACY_GUARD_EDIT=1 python3 scripts/privacy_guard_specs.py")
            return 1

        print("[PROMETEO PRIVACY GUARD] Guard policy edit rilevato in PR dedicata: consentito.")

    if violations:
        print("[PROMETEO PRIVACY GUARD] REPOSITORY VIOLATION")
        print("Le specifiche di finitura sono materiale strettamente privato e non divulgabile.")
        print("Sono vietati file articolo, immagini, PDF, archivi e metadata locali.")
        print("")
        print("File vietati tracciati:")
        for v in violations:
            print(f" - {v}")
        print("")
        print("Consentiti solo:")
        print(" - specs_finitura/index.json")
        print(" - specs_finitura/_templates/metadata.template.json")
        print("")
        print("Se questo è un falso positivo, fermarsi e creare una PR dedicata di guard policy.")
        return 1

    print("[PROMETEO PRIVACY GUARD] OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
