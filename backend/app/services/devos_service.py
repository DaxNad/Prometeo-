from __future__ import annotations

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[3]
BOARD_DIR = BASE_DIR / "board"


def _read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def _extract_bullets_under_section(markdown: str, title: str) -> list[str]:
    lines = markdown.splitlines()
    items: list[str] = []
    in_section = False

    for raw in lines:
        line = raw.rstrip()

        if line.startswith("## "):
            current = line[3:].strip().lower()
            in_section = current == title.lower()
            continue

        if not in_section:
            continue

        if line.startswith("- "):
            items.append(line[2:].strip())

    return items


def _extract_table_after_heading(markdown: str, heading: str) -> list[list[str]]:
    lines = markdown.splitlines()
    capture = False
    table_lines: list[str] = []

    for raw in lines:
        line = raw.rstrip()

        if line.startswith("## "):
            current = line[3:].strip().lower()

            if capture:
                break

            if current == heading.lower():
                capture = True
                continue

        if capture:
            if line.strip().startswith("|"):
                table_lines.append(line.strip())
            elif table_lines and not line.strip():
                break

    rows: list[list[str]] = []

    for line in table_lines:
        parts = [part.strip() for part in line.strip("|").split("|")]
        if not parts:
            continue
        if all(set(part) <= {"-", ":"} for part in parts):
            continue
        rows.append(parts)

    return rows


def _extract_general_modules(markdown: str) -> list[dict]:
    rows = _extract_table_after_heading(markdown, "Stato generale")
    modules: list[dict] = []

    for row in rows:
        if len(row) < 3:
            continue
        if row[0].lower() == "modulo" and row[1].lower() == "stato":
            continue

        modules.append(
            {
                "modulo": row[0],
                "stato": row[1],
                "note": row[2],
            }
        )

    return modules


def _extract_maturity_matrix(markdown: str) -> list[dict]:
    rows = _extract_table_after_heading(markdown, "Maturity matrix")
    matrix: list[dict] = []

    for row in rows:
        if len(row) < 3:
            continue
        if row[0].lower() == "modulo" and row[1].lower().startswith("livello attuale"):
            continue

        matrix.append(
            {
                "modulo": row[0],
                "maturity_level": row[1],
                "target_level": row[2],
            }
        )

    return matrix


def get_dev_status() -> dict:
    path = BOARD_DIR / "MASTER_CONTROL.md"
    raw = _read_text(path)

    return {
        "ok": True,
        "source": "board/master_control.md",
        "modules": _extract_general_modules(raw),
        "priority_modules": _extract_bullets_under_section(raw, "Modulo prioritario corrente"),
        "immediate_objectives": _extract_bullets_under_section(raw, "Obiettivo immediato"),
        "open_blocks": _extract_bullets_under_section(raw, "Blocchi aperti"),
        "next_steps": _extract_bullets_under_section(raw, "Prossimi passi immediati"),
        "maturity_matrix": _extract_maturity_matrix(raw),
        "raw": raw,
    }


def get_dev_tasks() -> dict:
    path = BOARD_DIR / "TASK_BOARD.md"
    raw = _read_text(path)
    return {
        "ok": True,
        "source": "board/task_board.md",
        "raw": raw,
    }


def get_dev_logs() -> dict:
    path = BOARD_DIR / "SYSTEM_LOG.md"
    raw = _read_text(path)
    return {
        "ok": True,
        "source": "board/system_log.md",
        "raw": raw,
    }


def get_dev_milestones() -> dict:
    path = BOARD_DIR / "MASTER_CONTROL.md"
    raw = _read_text(path)
    milestones = _extract_bullets_under_section(raw, "Milestone corrente")
    return {
        "ok": True,
        "source": "board/master_control.md",
        "items": milestones,
        "raw": raw,
    }
