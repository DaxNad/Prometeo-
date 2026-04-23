from typing import Dict


def route_task(task: Dict) -> str:
    task_type = task.get("type")

    if task_type == "plan":
        return "chatgpt"

    if task_type == "execution":
        return "codex"

    if task_type == "validation":
        return "claude"

    return "unknown"


if __name__ == "__main__":
    example = {"type": "plan"}
    print(route_task(example))
