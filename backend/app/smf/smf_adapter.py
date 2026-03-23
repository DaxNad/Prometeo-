from __future__ import annotations

from pathlib import Path


DEFAULT_SMF_DIR = Path.home() / "Documents" / "local_smf"


class SMFAdapter:
    def __init__(self, base_path: Path | None = None) -> None:
        self.base_path = base_path or DEFAULT_SMF_DIR

    def available(self) -> bool:
        return self.base_path.exists()

    def list_files(self) -> list[str]:
        if not self.available():
            return []

        return sorted(
            [
                item.name
                for item in self.base_path.iterdir()
                if item.is_file()
            ]
        )

    def info(self) -> dict:
        return {
            "path": str(self.base_path),
            "exists": self.available(),
            "files": self.list_files(),
        }
