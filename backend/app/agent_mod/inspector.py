from __future__ import annotations

from app.agent_mod.models import RunContext


CATEGORIES = (
    "sql",
    "service",
    "api",
    "planner",
    "rule_engine",
    "runtime_data",
    "smf",
    "other",
)


def classify_files(files: list[str]) -> dict[str, list[str]]:
    categories = {name: [] for name in CATEGORIES}

    for f in files:
        if f.startswith("backend/sql"):
            categories["sql"].append(f)
        elif f.startswith("backend/app/services"):
            categories["service"].append(f)
        elif f.startswith("backend/app/api"):
            categories["api"].append(f)
        elif f.startswith("backend/app/planners"):
            categories["planner"].append(f)
        elif f.startswith("backend/app/rule_engine"):
            categories["rule_engine"].append(f)
        elif f.startswith("backend/app/data"):
            categories["runtime_data"].append(f)
        elif (
            f.startswith("backend/app/smf")
            or f.startswith("backend/app/ingest")
            or f.startswith("backend/app/api_smf.py")
            or f.startswith("smf_core")
        ):
            categories["smf"].append(f)
        else:
            categories["other"].append(f)

    return categories


def attach_categories(context: RunContext) -> RunContext:
    context.categories = classify_files(context.files)
    return context
