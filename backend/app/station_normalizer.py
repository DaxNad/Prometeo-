import re
from typing import Optional


def normalize_station(value: Optional[str]) -> str:
    if value is None:
        return "NON_ASSEGNATA"

    s = str(value).strip().upper()
    if not s:
        return "NON_ASSEGNATA"

    s = s.replace("_", "-").replace(" ", "-")
    s = re.sub(r"-{2,}", "-", s)

    exact_map = {
        "ZAW1": "ZAW-1",
        "ZAW-1": "ZAW-1",
        "ZAW2": "ZAW-2",
        "ZAW-2": "ZAW-2",
        "HENN": "HENN",
        "PID": "PIDMILL",
        "PID-MILL": "PIDMILL",
        "PIDMILL": "PIDMILL",
        "CP": "CP",
        "NON-ASSEGNATA": "NON_ASSEGNATA",
        "NON_ASSEGNATA": "NON_ASSEGNATA",
    }

    if s in exact_map:
        return exact_map[s]

    # Riconosci forme testuali/di fase che contengono riferimenti alla stazione
    if re.search(r"\bZAW[- ]?1\b", s):
        return "ZAW-1"

    if re.search(r"\bZAW[- ]?2\b", s):
        return "ZAW-2"

    if "HENN" in s:
        return "HENN"

    if s.startswith("PID") or "PID-MILL" in s or "PIDMILL" in s:
        return "PIDMILL"

    if s == "CP" or s.startswith("CP-"):
        return "CP"

    m = re.fullmatch(r"([A-Z]+)-?([0-9]+)", s)
    if m:
        return f"{m.group(1)}-{m.group(2)}"

    m = re.fullmatch(r"([A-Z]+)-?([A-Z])", s)
    if m:
        return f"{m.group(1)}-{m.group(2)}"

    return s
