#!/usr/bin/env python3
from __future__ import annotations

import os
import shlex
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAIN_BRANCH = "main"

TEST_COMMAND = [
    "PYTHONPATH=backend",
    "python3",
    "-m",
    "pytest",
    "backend/tests/test_tl_chat_contract.py",
    "backend/tests/test_llm_service_tl_memory.py",
    "backend/tests/test_ai_output_sanitizer.py",
    "backend/tests/test_ai_inference_contract.py",
    "backend/tests/test_ai_sequence_endpoint.py",
    "-q",
]

GUARD_COMMANDS = [
    ["python3", "scripts/privacy_guard_specs.py"],
    ["python3", "scripts/data_leak_guard.py"],
]


def run(cmd: str | list[str], *, shell: bool = False, check: bool = False) -> subprocess.CompletedProcess:
    print()
    if isinstance(cmd, list):
        print("$", " ".join(shlex.quote(x) for x in cmd))
    else:
        print("$", cmd)

    return subprocess.run(
        cmd,
        cwd=ROOT,
        shell=shell,
        text=True,
        check=check,
    )


def capture(cmd: list[str]) -> str:
    return subprocess.check_output(cmd, cwd=ROOT, text=True).strip()


def branch() -> str:
    return capture(["git", "branch", "--show-current"])


def status_short() -> str:
    return capture(["git", "status", "--short"])


def ensure_repo() -> None:
    if not ROOT.exists():
        raise SystemExit(f"Repo non trovato: {ROOT}")
    if not (ROOT / ".git").exists():
        raise SystemExit(f"Non è una repo Git: {ROOT}")


def block_direct_main_push() -> None:
    if branch() == MAIN_BRANCH:
        raise SystemExit(
            "\nBLOCCO: sei su main. "
            "PROMETEO vieta push diretto su main. "
            "Crea prima un branch dedicato."
        )


def pause() -> None:
    input("\nInvio per continuare...")


def show_status() -> None:
    run(["git", "status"])
    print("\nBranch attuale:", branch())


def show_diff() -> None:
    print("\n== STATUS SHORT ==")
    run(["git", "status", "--short"])

    print("\n== TRACKED DIFF STAT ==")
    run(["git", "diff", "--stat"])

    print("\n== TRACKED DIFF ==")
    run(["git", "diff"])

    untracked = [
        line[3:]
        for line in status_short().splitlines()
        if line.startswith("?? ")
    ]

    if untracked:
        print("\n== UNTRACKED FILES ==")
        for item in untracked:
            print(item)


def create_branch() -> None:
    current = branch()
    print(f"\nBranch attuale: {current}")
    if current != MAIN_BRANCH:
        print("Sei già su un branch dedicato.")
        return

    name = input("Nome branch dedicato, es. fix/tl-chat-parser: ").strip()
    if not name:
        print("Operazione annullata: nome branch vuoto.")
        return
    if name == MAIN_BRANCH:
        raise SystemExit("Nome branch vietato: main.")

    run(["git", "switch", "-c", name], check=True)


def run_tests_and_guards() -> None:
    print("\n== TEST MIRATI ==")
    run(" ".join(TEST_COMMAND), shell=True, check=True)

    print("\n== GUARDRAIL ==")
    for cmd in GUARD_COMMANDS:
        target = ROOT / cmd[-1]
        if target.exists():
            run(cmd, check=True)
        else:
            print(f"SKIP: {cmd[-1]} non trovato.")


def commit_changes() -> None:
    current = branch()
    if current == MAIN_BRANCH:
        raise SystemExit("BLOCCO: commit operativo su main non consentito da questa console.")

    if not status_short():
        print("Nessuna modifica da committare.")
        return

    print("\nDiff/status obbligatorio prima del commit:")
    show_diff()
    confirm = input("\nHai verificato diff e file non tracciati? Scrivi COMMIT per procedere: ").strip()
    if confirm != "COMMIT":
        print("Commit annullato.")
        return

    msg = input("Messaggio commit inline: ").strip()
    if not msg:
        print("Commit annullato: messaggio vuoto.")
        return

    run(["git", "add", "-A"], check=True)
    run(["git", "commit", "-m", msg], check=True)


def push_branch() -> None:
    block_direct_main_push()
    current = branch()
    run(["git", "push", "-u", "origin", current], check=True)


def create_pr() -> None:
    block_direct_main_push()
    current = branch()

    title = input("Titolo PR: ").strip()
    if not title:
        title = f"chore: update {current}"

    body = input("Body PR breve: ").strip()
    if not body:
        body = "## Summary\n- Update PROMETEO branch via protected PR flow.\n\n## Tests\n- Run through PROMETEO Release Console."

    run(
        [
            "gh",
            "pr",
            "create",
            "--base",
            MAIN_BRANCH,
            "--head",
            current,
            "--title",
            title,
            "--body",
            body,
        ],
        check=True,
    )


def watch_checks() -> None:
    pr = input("Numero PR oppure vuoto per branch attuale: ").strip()
    if pr:
        run(["gh", "pr", "checks", pr, "--watch"], check=True)
    else:
        run(["gh", "pr", "checks", "--watch"], check=True)


def merge_pr_and_sync() -> None:
    pr = input("Numero PR da mergiare: ").strip()
    if not pr:
        print("Merge annullato: numero PR vuoto.")
        return

    confirm = input("Confermi che tutti i required checks sono verdi? Scrivi MERGE: ").strip()
    if confirm != "MERGE":
        print("Merge annullato.")
        return

    run(["gh", "pr", "merge", pr, "--squash", "--delete-branch"], check=True)
    run(["git", "switch", MAIN_BRANCH], check=True)
    run(["git", "fetch", "origin"], check=True)
    run(["git", "reset", "--hard", "origin/main"], check=True)
    run(["git", "status"], check=True)


def menu() -> None:
    ensure_repo()

    while True:
        print(
            """
PROMETEO RELEASE CONSOLE

1  Stato repo
2  Mostra diff
3  Crea branch dedicato
4  Test + Privacy/Data Leak Guard
5  Commit guidato
6  Push branch
7  Crea Pull Request
8  Guarda check PR
9  Merge PR + riallinea main
0  Esci

Regola: mai push diretto su main. Sempre branch → PR → check verdi → merge.
"""
        )
        choice = input("Scelta: ").strip()

        try:
            if choice == "1":
                show_status()
            elif choice == "2":
                show_diff()
            elif choice == "3":
                create_branch()
            elif choice == "4":
                run_tests_and_guards()
            elif choice == "5":
                commit_changes()
            elif choice == "6":
                push_branch()
            elif choice == "7":
                create_pr()
            elif choice == "8":
                watch_checks()
            elif choice == "9":
                merge_pr_and_sync()
            elif choice == "0":
                return
            else:
                print("Scelta non valida.")
        except subprocess.CalledProcessError as exc:
            print(f"\nERRORE comando. Exit code: {exc.returncode}")
        except KeyboardInterrupt:
            print("\nOperazione interrotta.")
        pause()


if __name__ == "__main__":
    menu()
