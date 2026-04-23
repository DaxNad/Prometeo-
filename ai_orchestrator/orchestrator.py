import json
from pathlib import Path
from typing import Dict, Any

BASE_DIR = Path(__file__).resolve().parents[1]
AI_STATE_DIR = BASE_DIR / "backend" / "data" / "ai_state"


def load_latest_plan() -> Dict[str, Any] | None:
    plans_dir = AI_STATE_DIR / "plans"
    files = sorted(plans_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not files:
        return None
    return json.loads(files[0].read_text())


def route_task(task: Dict) -> str:
    task_type = task.get("type")

    if task_type == "plan":
        return "chatgpt"

    if task_type in {"execution", "backend", "frontend", "test", "file_patch"}:
        return "codex"

    if task_type in {"validation", "architecture_review", "security_review"}:
        return "claude"

    return "unknown"



def build_codex_prompt(task: Dict[str, Any]) -> str:
    files = task.get("files", [])
    files_text = ", ".join(files) if files else "not specified"

    return f"""TASK: {task.get("action", "No action provided")}

CONTEXT:
- project: PROMETEO
- target files: {files_text}
- task id: {task.get("id")}
- task type: {task.get("type")}

REQUIREMENTS:
- modify only the specified files when possible
- preserve existing architecture
- do not create duplicate documentation layers
- do not bypass guard rails
- keep changes minimal and testable

OUTPUT:
- direct file changes
- concise final report only
"""

def orchestrate():
    plan = load_latest_plan()

    if not plan:
        print("No plan found")
        return

    print(f"Loaded plan: {plan.get('id')}")

    for task in plan.get("tasks", []):
        target = route_task(task)
        print(f"Task {task.get('id')} → {target}")

        if target == "codex":
            print("--- CODEX PROMPT START ---")
            print(build_codex_prompt(task))
            print("--- CODEX PROMPT END ---")


if __name__ == "__main__":
    orchestrate()
