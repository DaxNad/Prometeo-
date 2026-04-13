from __future__ import annotations

from pathlib import Path

import pandas as pd

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
        df = pd.read_excel(self.path, sheet_name=sheet)

        match_columns = [column for column in self._candidate_columns(id_column) if column in df.columns]
        if not match_columns:
            return {"error": f"column {id_column} not found"}

        target = str(id_value).strip()
        mask = pd.Series(False, index=df.index)
        matched_column = None
        for column in match_columns:
            values = df[column].fillna("").astype(str).str.strip()
            column_mask = values == target
            if matched_column is None and bool(column_mask.any()):
                matched_column = column
            mask = mask | column_mask

        if int(mask.sum()) == 0:
            return {
                "error": "row not found",
                "matched_column": None,
                "written_columns": [],
            }

        expanded_updates = self._expand_updates(updates)
        requested_columns = list(updates.keys())
        written_columns: list[str] = []
        for key, value in expanded_updates.items():
            if key in df.columns:
                df.loc[mask, key] = value
                written_columns.append(key)

        with pd.ExcelWriter(
            self.path,
            engine="openpyxl",
            mode="a",
            if_sheet_exists="replace",
        ) as writer:
            df.to_excel(writer, sheet_name=sheet, index=False)

        return {
            "ok": True,
            "updated": int(mask.sum()),
            "matched_column": matched_column,
            "requested_columns": requested_columns,
            "written_columns": written_columns,
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
