from __future__ import annotations

from pathlib import Path

import pandas as pd


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

        if id_column not in df.columns:
            return {"error": f"column {id_column} not found"}

        mask = df[id_column] == id_value

        if int(mask.sum()) == 0:
            return {"error": "row not found"}

        for key, value in updates.items():
            if key in df.columns:
                df.loc[mask, key] = value

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
        }
