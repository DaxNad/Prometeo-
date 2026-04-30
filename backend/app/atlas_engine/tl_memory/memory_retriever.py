import json
from pathlib import Path

RULES_PATH = Path(__file__).with_name("rules.json")


def load_rules() -> list[dict]:
    if not RULES_PATH.exists():
        return []

    try:
        return json.loads(RULES_PATH.read_text(encoding="utf-8"))
    except Exception:
        return []


def retrieve_relevant_rules(text: str, limit: int = 5) -> list[dict]:
    query = (text or "").lower()
    if not query:
        return []

    matches = []

    for rule in load_rules():
        tags = rule.get("tags", [])
        searchable = " ".join(str(tag).lower() for tag in tags)

        if any(str(tag).lower() in query for tag in tags) or searchable in query:
            matches.append(rule)

    priority_order = {"high": 0, "medium": 1, "low": 2}
    matches.sort(key=lambda r: priority_order.get(r.get("priority", "low"), 9))

    return matches[:limit]


def format_rules_for_prompt(rules: list[dict]) -> str:
    if not rules:
        return "Nessuna regola TL rilevante trovata."

    return "\n".join(f"- {r.get('rule', '')}" for r in rules if r.get("rule"))
