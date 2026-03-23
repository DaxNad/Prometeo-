from __future__ import annotations

from pathlib import Path
import pandas as pd


class SMFWriter:

    def __init__(self, path: Path):
        self.path = path

    def append_row(self, sheet: str, row: dict) -> dict:

        xls = pd.ExcelFile(self.path)

        if sheet not in xls.sheet_names:
            return {"error": f"sheet {sheet} not found"}

        df = pd.read_excel(self.path, sheet_name=sheet)

        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)

        with pd.ExcelWriter(
            self.path,
            engine="openpyxl",
            mode="a",
            if_sheet_exists="replace"
        ) as writer:

            df.to_excel(writer, sheet_name=sheet, index=False)

        return {
            "ok": True,
            "rows": len(df)
        }
