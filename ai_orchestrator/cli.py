from __future__ import annotations

import json
import sys
from pathlib import Path

RUNS_DIR = Path(__file__).resolve().parent / "runs"


def status() -> None:
    if not RUNS_DIR.exists():
        print("No runs directory found")
        return

    files = sorted(RUNS_DIR.glob("run_*.json"))

    if not files:
        print("No run records found")
        return

    print("PROMETEO LOOP STATUS")
    print("-" * 60)

    for file in files:
        data = json.loads(file.read_text())
        task_id = data.get("task_id", "?")
        plan_id = data.get("plan_id", "?")
        state = data.get("state", "?")
        requires_claude = data.get("requires_claude", False)
        notes = data.get("notes", "")

        print(f"{task_id:8} | {state:18} | claude={requires_claude} | plan={plan_id}")
        if notes:
            print(f"         notes: {notes}")

    print("-" * 60)




def next_action() -> None:
    if not RUNS_DIR.exists():
        print("No runs directory found")
        return

    files = sorted(RUNS_DIR.glob("run_*.json"))

    pending = []
    for file in files:
        data = json.loads(file.read_text())
        state = data.get("state")
        if state not in ("ACCEPTED", "SKIPPED"):
            pending.append(data)

    if not pending:
        print("NEXT ACTION: nessun task pendente")
        return

    # prendi il primo task non chiuso
    task = pending[0]
    task_id = task.get("task_id")
    state = task.get("state")

    print("NEXT ACTION")
    print("-" * 40)
    print(f"task: {task_id}")
    print(f"stato: {state}")

    if state == "TASK_GENERATED":
        print(f"→ eseguire Codex: codex < ai_orchestrator/generated_tasks/{task_id}.txt")
    elif state == "CODEX_APPLIED":
        print("→ eseguire test + import check")
    elif state == "TESTS_PASSED":
        if task.get("requires_claude"):
            print(f"→ eseguire Claude review: claude < ai_orchestrator/generated_reviews/{task_id}_claude_review.txt")
        else:
            print("→ commit diretto")
    else:
        print("→ verificare stato manualmente")


def main() -> None:
    command = sys.argv[1] if len(sys.argv) > 1 else "status"

    if command == "status":
        status()
        return

    if command == "next":
        next_action()
        return

    print(f"Unknown command: {command}")
    print("Available commands: status")


if __name__ == "__main__":
    main()
