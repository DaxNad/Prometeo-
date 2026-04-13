from __future__ import annotations

from pathlib import Path
import pandas as pd
import os

from .smf_schema import REQUIRED_SCHEMA

HEADER_ALIASES = {
    "ID ordine": "order_id",
    "Cliente": "cliente",
    "Codice": "codice",
    "Q.ta": "qta",
    "Data richiesta cliente": "due_date",
    "Priorità": "priority",
    "Postazione assegnata": "postazione",
    "Stato (da fare/in corso/finito)": "stato",
    "Progress %": "progress",
    "Semaforo scadenza": "semaforo",
    "Note": "note",
}


class SMFWriter:

    def __init__(self, path: Path):
        self.path = path

    def append_row(self, sheet: str, row: dict) -> dict:
        mode = os.getenv("SMF_SCHEMA_MODE", "validate").strip().lower() or "validate"
        try:
            xls = pd.ExcelFile(self.path)
        except Exception:
            return {"ok": False, "error": "workbook not readable"}

        if sheet not in xls.sheet_names:
            return {"ok": False, "error": f"sheet {sheet} not found"}

        try:
            df = pd.read_excel(self.path, sheet_name=sheet)
        except Exception:
            return {"ok": False, "error": "sheet read error"}

        # schema guard: ensure required columns for the sheet
        required = REQUIRED_SCHEMA.get(sheet, [])
        missing = [c for c in required if c not in df.columns]
        if missing:
            if mode == "repair":
                for c in missing:
                    df[c] = None
            else:
                return {"ok": False, "error": f"missing columns: {', '.join(missing)}"}
        normalized_row = self._normalize_row(row, list(df.columns))
        requested_columns = list(row.keys())
        written_columns = [
            column for column, value in normalized_row.items()
            if value is not None and str(value) != ""
        ]

        df = pd.concat([df, pd.DataFrame([normalized_row], columns=df.columns)], ignore_index=True)

        try:
            with pd.ExcelWriter(
                self.path,
                engine="openpyxl",
                mode="a",
                if_sheet_exists="replace"
            ) as writer:
                df.to_excel(writer, sheet_name=sheet, index=False)
        except Exception:
            return {"ok": False, "error": "write failed"}

        return {
            "ok": True,
            "rows": len(df),
            "requested_columns": requested_columns,
            "written_columns": written_columns,
            "matched_column": None,
            "schema_mode": mode,
        }

    def _normalize_row(self, row: dict, columns: list[str]) -> dict:
        normalized = {column: None for column in columns}

        for column in columns:
            if column in row:
                normalized[column] = row[column]
                continue

            alias = HEADER_ALIASES.get(column)
            if alias and alias in row:
                normalized[column] = row[alias]
                continue

            reverse_alias = self._reverse_alias(column)
            if reverse_alias and reverse_alias in row:
                normalized[column] = row[reverse_alias]

        return normalized

    def _reverse_alias(self, column: str) -> str | None:
        for canonical, alias in HEADER_ALIASES.items():
            if alias == column:
                return canonical
        return None
