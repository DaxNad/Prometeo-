from .policy import TaskType


KEYWORDS = {
    TaskType.CI_FIX: [
        "ci",
        "workflow",
        "github action",
        "pipeline",
        "pytest",
        "vercel"
    ],

    TaskType.SMF_MAPPING_CHANGE: [
        "smf",
        "excel",
        "mapping",
        "supermegafile"
    ],

    TaskType.PLANNER_LOGIC_CHANGE: [
        "planner",
        "sequence",
        "machine-load",
        "turn-plan",
        "station"
    ],

    TaskType.ARCH_REVIEW: [
        "architecture",
        "design",
        "model",
        "domain"
    ],

    TaskType.SMALL_PATCH: [
        "fix",
        "bug",
        "patch",
        "small change"
    ]
}


def classify_task(text: str) -> TaskType:
    t = text.lower()

    for task_type, words in KEYWORDS.items():
        for w in words:
            if w in t:
                return task_type

    return TaskType.DOMAIN_TRANSLATION
