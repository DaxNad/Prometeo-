from __future__ import annotations

from pathlib import Path

from .smf_reader import SMFReader
from .smf_writer import SMFWriter
from .smf_updater import SMFUpdater


DEFAULT_SMF_DIR = Path.home() / "Documents" / "local_smf"
MASTER_NAME = "SuperMegaFile_Master.xlsx"


class SMFAdapter:
    def __init__(self, base_path: Path | None = None) -> None:
        self.base_path = base_path or DEFAULT_SMF_DIR

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
