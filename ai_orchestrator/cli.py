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


def main() -> None:
    command = sys.argv[1] if len(sys.argv) > 1 else "status"

    if command == "status":
        status()
        return

    print(f"Unknown command: {command}")
    print("Available commands: status")


if __name__ == "__main__":
    main()
