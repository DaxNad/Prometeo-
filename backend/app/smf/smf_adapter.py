from __future__ import annotations

import os
from pathlib import Path

from .smf_reader import SMFReader
from .smf_writer import SMFWriter
from .smf_updater import SMFUpdater


MASTER_NAME = "SuperMegaFile_Master.xlsx"


def _default_smf_dir() -> Path:
    env_dir = os.getenv("SMF_BASE_PATH", "").strip()
    if env_dir:
        return Path(env_dir)

    return Path.home() / "Documents" / "local_smf"


class SMFAdapter:
    def __init__(self, base_path: Path | None = None) -> None:
        self.base_path = base_path or _default_smf_dir()

    def master_path(self) -> Path:
        return self.base_path / MASTER_NAME

    def available(self) -> bool:
        return self.master_path().exists()

    def reader(self) -> SMFReader:
        return SMFReader(self.master_path())

    def writer(self) -> SMFWriter:
        return SMFWriter(self.master_path())

    def updater(self) -> SMFUpdater:
        return SMFUpdater(self.master_path())

    def info(self) -> dict:
        return {
            "base_path": str(self.base_path),
            "path": str(self.master_path()),
            "exists": self.available(),
        }

    def structure(self) -> dict:
        reader = self.reader()
        return {
            "exists": reader.exists(),
            "sheets": reader.sheets(),
        }

    def preview(self, sheet: str | None = None, rows: int = 5) -> dict:
        reader = self.reader()
        return reader.preview(sheet=sheet, rows=rows)

    def append_order(self, data: dict) -> dict:
        return self.writer().append_row("Pianificazione", data)

    def update_order(self, order_id: str, updates: dict) -> dict:
        return self.updater().update_row(
            sheet="Pianificazione",
            id_column="ID ordine",
            id_value=order_id,
            updates=updates,
        )
