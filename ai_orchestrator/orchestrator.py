import json
from pathlib import Path
from typing import Dict, Any
try:
    from .loop_state import init_run, mark_requires_claude
except ImportError:
    from loop_state import init_run, mark_requires_claude

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





import subprocess

def run_codex_task(task_id: str):
    file = Path("ai_orchestrator/generated_tasks") / f"{task_id}.txt"

    if not file.exists():
        print(f"Task file not found: {file}")
        return

    print(f"Running Codex task: {task_id}")

    subprocess.run([
        "codex"
    ], input=file.read_text(), text=True)

def write_codex_task(task_id: str, prompt: str):
    out_dir = Path("ai_orchestrator/generated_tasks")
    out_dir.mkdir(parents=True, exist_ok=True)
    file = out_dir / f"{task_id}.txt"
    file.write_text(prompt)
    print(f"Saved Codex task: {file}")


def get_changed_files() -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--name-only"],
        text=True,
        capture_output=True,
        check=False,
    )
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def evaluate_claude_requirement(task_id: str) -> bool:
    changed_files = get_changed_files()
    requires = mark_requires_claude(task_id, changed_files)
    print(f"Changed files: {changed_files if changed_files else 'none'}")
    print(f"Requires Claude: {requires}")
    return requires

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
            prompt = build_codex_prompt(task)
            print("--- CODEX PROMPT START ---")
            print(prompt)
            print("--- CODEX PROMPT END ---")
            task_id = task.get("id")
            write_codex_task(task_id, prompt)

            from loop_state import load_run
            existing = load_run(task_id)

            if existing is None:
                init_run(task_id, plan.get("id"))
                print(f"Loop state: TASK_GENERATED for {task_id}")
            else:
                print(f"Loop state già esistente per {task_id} → skip")
            print(f"Manual run: codex < ai_orchestrator/generated_tasks/{task_id}.txt")

            requires_claude = evaluate_claude_requirement(task_id)

            if requires_claude:
                print(f"Claude review required for {task_id}")
            else:
                print(f"No Claude review needed for {task_id}")


if __name__ == "__main__":
    orchestrate()
