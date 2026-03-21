from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List


ROOT_DIR = Path(__file__).resolve().parents[3]
BOARD_DIR = ROOT_DIR / "board"
DOCS_DIR = ROOT_DIR / "docs"


def _read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def _extract_bullets_under_heading(markdown: str, heading: str) -> List[str]:
    lines = markdown.splitlines()
    results: List[str] = []
    capture = False

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("## "):
            capture = stripped.lower() == f"## {heading.lower()}"
            continue

        if capture:
            if stripped.startswith("## "):
                break
            if stripped.startswith("- "):
                results.append(stripped[2:].strip())
            elif stripped[:2].isdigit() and ". " in stripped:
                parts = stripped.split(". ", 1)
                if len(parts) == 2:
                    results.append(parts[1].strip())

    return results


def _extract_table_rows(markdown: str) -> List[Dict[str, str]]:
    lines = [line.strip() for line in markdown.splitlines() if line.strip()]
    rows: List[Dict[str, str]] = []

    for line in lines:
        if not line.startswith("|") or not line.endswith("|"):
            continue
        if "---" in line:
            continue

        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) != 3:
            continue
        if cells[0].lower() == "modulo":
            continue

        rows.append(
            {
                "modulo": cells[0],
                "stato": cells[1],
                "note": cells[2],
            }
        )

    return rows


@dataclass
class DevOSService:
    board_dir: Path = BOARD_DIR
    docs_dir: Path = DOCS_DIR

    @property
    def master_control_path(self) -> Path:
        return self.board_dir / "master_control.md"

    @property
    def task_board_path(self) -> Path:
        return self.board_dir / "task_board.md"

    @property
    def system_log_path(self) -> Path:
        return self.board_dir / "system_log.md"

    def get_status(self) -> Dict:
        master_text = _read_text(self.master_control_path)

        return {
            "ok": True,
            "source": str(self.master_control_path.relative_to(ROOT_DIR)),
            "modules": _extract_table_rows(master_text),
            "priority_modules": _extract_bullets_under_heading(master_text, "Modulo prioritario corrente"),
            "immediate_objectives": _extract_bullets_under_heading(master_text, "Obiettivo immediato"),
            "open_blocks": _extract_bullets_under_heading(master_text, "Blocchi aperti"),
            "next_steps": _extract_bullets_under_heading(master_text, "Prossimi passi immediati"),
            "raw": master_text,
        }

    def get_tasks(self) -> Dict:
        task_text = _read_text(self.task_board_path)

        return {
            "ok": True,
            "source": str(self.task_board_path.relative_to(ROOT_DIR)),
            "raw": task_text,
        }

    def get_logs(self) -> Dict:
        log_text = _read_text(self.system_log_path)

        return {
            "ok": True,
            "source": str(self.system_log_path.relative_to(ROOT_DIR)),
            "raw": log_text,
        }

    def get_milestones(self) -> Dict:
        master_text = _read_text(self.master_control_path)
        log_text = _read_text(self.system_log_path)

        milestone_lines = _extract_bullets_under_heading(master_text, "Milestone corrente")

        if not milestone_lines:
            milestone_lines = _extract_bullets_under_heading(log_text, "Prossimi passi")

        return {
            "ok": True,
            "milestones": milestone_lines,
            "master_control_source": str(self.master_control_path.relative_to(ROOT_DIR)),
            "system_log_source": str(self.system_log_path.relative_to(ROOT_DIR)),
        }


devos_service = DevOSService()
