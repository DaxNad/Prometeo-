from __future__ import annotations

import json
import subprocess
from pathlib import Path


def fetch_planner_sequence() -> dict:
    result = subprocess.run(
        [
            "curl",
            "-s",
            "-H",
            f"X-API-Key: {__import__('os').environ.get('PROMETEO_API_KEY','')}",
            "http://127.0.0.1:8000/planner/sequence",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    return json.loads(result.stdout)


def generate_tasks_from_planner(payload: dict) -> list[dict]:
    items = payload.get("items", [])
    tasks = []

    for item in items:
        if item.get("open_events_total", 0) > 0:
            tasks.append({
                "id": f"T_{item['article']}",
                "type": "backend",
                "action": f"resolve anomaly at {item['critical_station']}",
                "files": [],
                "notes": item.get("event_titles", ""),
            })

    return tasks


def save_plan(tasks: list[dict]) -> None:
    base = Path("ai_orchestrator/generated_plans")
    base.mkdir(parents=True, exist_ok=True)

    plan = {
        "id": "plan_auto_generated",
        "tasks": tasks,
    }

    file = base / "plan_auto.json"
    file.write_text(json.dumps(plan, indent=2))
    print(f"Saved plan: {file}")


def main():
    payload = fetch_planner_sequence()
    tasks = generate_tasks_from_planner(payload)

    if not tasks:
        print("No tasks generated")
        return

    save_plan(tasks)


if __name__ == "__main__":
    main()
