from __future__ import annotations

from pathlib import Path

import os
import pandas as pd

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


class SMFUpdater:
    def __init__(self, path: Path) -> None:
        self.path = path

    def update_row(
        self,
        sheet: str,
        id_column: str,
        id_value,
        updates: dict,
    ) -> dict:
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

        required = REQUIRED_SCHEMA.get(sheet, [])
        missing = [c for c in required if c not in df.columns]
        if missing:
            if mode == "repair":
                for c in missing:
                    df[c] = None
            else:
                return {"ok": False, "error": f"missing columns: {', '.join(missing)}"}

        match_columns = [column for column in self._candidate_columns(id_column) if column in df.columns]
        if not match_columns:
            return {"ok": False, "error": f"column {id_column} not found"}

        target = str(id_value).strip()
        mask = pd.Series(False, index=df.index)
        matched_column = None
        for column in match_columns:
            values = self._normalized_text(df[column])
            column_mask = values == target
            if matched_column is None and bool(column_mask.any()):
                matched_column = column
            mask = mask | column_mask

        if int(mask.sum()) == 0:
            return {
                "ok": False,
                "error": "row not found",
                "matched_column": None,
                "written_columns": [],
            }

        expanded_updates = self._expand_updates(updates)
        requested_columns = list(updates.keys())
        written_columns: list[str] = []

        for key, value in expanded_updates.items():
            if key not in df.columns:
                continue

            try:
                from pandas.api.types import is_object_dtype

                if isinstance(value, str) and not is_object_dtype(df[key].dtype):
                    df = df.astype({key: "object"})
            except Exception:
                pass

            try:
                current_vals = self._normalized_text(df.loc[mask, key])
                new_val = "" if value is None else str(value).strip()
                if not bool((current_vals == new_val).all()):
                    df.loc[mask, key] = value
                    written_columns.append(key)
            except Exception:
                df.loc[mask, key] = value
                written_columns.append(key)

        try:
            with pd.ExcelWriter(
                self.path,
                engine="openpyxl",
                mode="a",
                if_sheet_exists="replace",
            ) as writer:
                df.to_excel(writer, sheet_name=sheet, index=False)
        except Exception:
            return {"ok": False, "error": "write failed"}

        return {
            "ok": True,
            "updated": int(mask.sum()),
            "matched_column": matched_column,
            "requested_columns": requested_columns,
            "written_columns": written_columns,
            "schema_mode": mode,
        }

    def _candidate_columns(self, column: str) -> list[str]:
        candidates = [column]

        alias = HEADER_ALIASES.get(column)
        if alias:
            candidates.append(alias)

        for canonical, mapped_alias in HEADER_ALIASES.items():
            if mapped_alias == column:
                candidates.append(canonical)

        return list(dict.fromkeys(candidates))

    def _expand_updates(self, updates: dict) -> dict:
        expanded = dict(updates)
        for key, value in list(updates.items()):
            alias = HEADER_ALIASES.get(key)
            if alias and alias not in expanded:
                expanded[alias] = value

            for canonical, mapped_alias in HEADER_ALIASES.items():
                if mapped_alias == key and canonical not in expanded:
                    expanded[canonical] = value

        return expanded

    def _normalized_text(self, series: pd.Series) -> pd.Series:
        def normalize_cell(value) -> str:
            if pd.isna(value):
                return ""

            text = str(value).strip()

            # Excel/pandas may read ID-like cells as floats.
            # Example: "12345.0" must match incoming order_id "12345".
            if text.endswith(".0"):
                integer_part = text[:-2]
                if integer_part.isdigit():
                    return integer_part

            return text

        return series.map(normalize_cell).astype("string").fillna("").str.strip()
