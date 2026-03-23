from __future__ import annotations

from pathlib import Path

import pandas as pd


class SMFReader:
    def __init__(self, path: Path) -> None:
        self.path = path

    def exists(self) -> bool:
        return self.path.exists()

    def sheets(self) -> list[str]:
        if not self.exists():
            return []

        xls = pd.ExcelFile(self.path)
        return list(xls.sheet_names)

    def preview(self, sheet: str | None = None, rows: int = 5) -> dict:
        if not self.exists():
            return {
                "exists": False,
                "sheet": None,
                "columns": [],
                "rows_preview": [],
                "row_count": 0,
                "available_sheets": [],
            }

        xls = pd.ExcelFile(self.path)
        available_sheets = list(xls.sheet_names)

        if not available_sheets:
            return {
                "exists": True,
                "sheet": None,
                "columns": [],
                "rows_preview": [],
                "row_count": 0,
                "available_sheets": [],
            }

        if sheet is None:
            sheet = available_sheets[0]

        if sheet not in available_sheets:
            return {
                "exists": True,
                "sheet": sheet,
                "columns": [],
                "rows_preview": [],
                "row_count": 0,
                "available_sheets": available_sheets,
                "error": f"Foglio non trovato: {sheet}",
            }

        df = pd.read_excel(self.path, sheet_name=sheet)

        return {
            "exists": True,
            "sheet": sheet,
            "columns": list(df.columns),
            "rows_preview": df.head(rows).fillna("").to_dict(orient="records"),
            "row_count": len(df),
            "available_sheets": available_sheets,
        }
