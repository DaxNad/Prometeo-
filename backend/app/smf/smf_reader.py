from __future__ import annotations

from pathlib import Path

import pandas as pd

CODE_COLUMN_CANDIDATES = ("Codice", "codice", "Code", "code")
STATION_COLUMN_CANDIDATES = ("Postazione", "postazione", "Stazione", "stazione", "Linea", "linea")


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

    def code_exists(self, code: str, sheet: str = "Codici", column: str = "Codice") -> dict:
        normalized_code = str(code or "").strip()
        if not self.exists():
            return {
                "ok": False,
                "found": False,
                "sheet": sheet,
                "column": column,
                "matched_column": None,
                "code": normalized_code,
                "error": "file not found",
            }

        if not normalized_code:
            return {
                "ok": True,
                "found": False,
                "sheet": sheet,
                "column": column,
                "matched_column": None,
                "code": normalized_code,
            }

        xls = pd.ExcelFile(self.path)
        if sheet not in xls.sheet_names:
            return {
                "ok": False,
                "found": False,
                "sheet": sheet,
                "column": column,
                "matched_column": None,
                "code": normalized_code,
                "error": f"sheet {sheet} not found",
            }

        df = pd.read_excel(self.path, sheet_name=sheet)
        candidate_columns = [c for c in (column, *CODE_COLUMN_CANDIDATES) if c in df.columns]
        candidate_columns = list(dict.fromkeys(candidate_columns))
        if not candidate_columns:
            return {
                "ok": False,
                "found": False,
                "sheet": sheet,
                "column": column,
                "matched_column": None,
                "code": normalized_code,
                "error": f"column {column} not found",
            }

        found = False
        matched_column = None
        target = normalized_code.upper()
        for candidate in candidate_columns:
            values = df[candidate].fillna("").astype(str).str.strip().str.upper()
            if bool((values == target).any()):
                found = True
                matched_column = candidate
                break
        return {
            "ok": True,
            "found": found,
            "sheet": sheet,
            "column": column,
            "matched_column": matched_column,
            "code": normalized_code,
        }

    def station_exists(self, station: str, sheet: str = "Postazioni", column: str = "Postazione") -> dict:
        normalized_station = str(station or "").strip()
        if not self.exists():
            return {
                "ok": False,
                "found": False,
                "sheet": sheet,
                "column": column,
                "matched_column": None,
                "station": normalized_station,
                "error": "file not found",
            }

        if not normalized_station:
            return {
                "ok": True,
                "found": False,
                "sheet": sheet,
                "column": column,
                "matched_column": None,
                "station": normalized_station,
            }

        xls = pd.ExcelFile(self.path)
        if sheet not in xls.sheet_names:
            return {
                "ok": False,
                "found": False,
                "sheet": sheet,
                "column": column,
                "matched_column": None,
                "station": normalized_station,
                "error": f"sheet {sheet} not found",
            }

        df = pd.read_excel(self.path, sheet_name=sheet)
        candidate_columns = [c for c in (column, *STATION_COLUMN_CANDIDATES) if c in df.columns]
        candidate_columns = list(dict.fromkeys(candidate_columns))
        if not candidate_columns:
            return {
                "ok": False,
                "found": False,
                "sheet": sheet,
                "column": column,
                "matched_column": None,
                "station": normalized_station,
                "error": f"column {column} not found",
            }

        found = False
        matched_column = None
        target = normalized_station.upper()
        for candidate in candidate_columns:
            values = df[candidate].fillna("").astype(str).str.strip().str.upper()
            if bool((values == target).any()):
                found = True
                matched_column = candidate
                break
        return {
            "ok": True,
            "found": found,
            "sheet": sheet,
            "column": column,
            "matched_column": matched_column,
            "station": normalized_station,
        }
