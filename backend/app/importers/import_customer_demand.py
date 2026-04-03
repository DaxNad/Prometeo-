from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text


DEFAULT_SMF_PATH = Path.home() / "Documents" / "local_smf" / "SuperMegaFile_Master.xlsx"


def import_customer_demand_from_smf(path: Path | None = None) -> dict:
    smf_path = Path(path) if path else DEFAULT_SMF_PATH
    if not smf_path.exists():
        raise FileNotFoundError(f"SMF non trovato: {smf_path}")

    df = pd.read_excel(smf_path, sheet_name="Pianificazione")
    df.columns = [str(c).strip() for c in df.columns]

    required_cols = ["Codice", "Q.ta"]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Colonne mancanti nel foglio Pianificazione: {missing}")

    priority_col = "Priorità" if "Priorità" in df.columns else None
    date_col = "Data richiesta cliente" if "Data richiesta cliente" in df.columns else None

    records = []
    for _, row in df.iterrows():
        codice = row.get("Codice")
        quantita = row.get("Q.ta")
        data_richiesta = row.get(date_col) if date_col else None
        priorita = row.get(priority_col) if priority_col else None

        if pd.isna(codice) or pd.isna(quantita):
            continue

        records.append(
            {
                "articolo": str(codice).strip(),
                "codice_articolo": str(codice).strip(),
                "quantita": int(quantita),
                "data_spedizione": None if pd.isna(data_richiesta) else pd.to_datetime(data_richiesta).date(),
                "priorita_cliente": None if pd.isna(priorita) or str(priorita).strip() == "" else str(priorita).strip(),
            }
        )

    engine = create_engine(os.environ["DATABASE_URL"])

    with engine.begin() as conn:
        conn.execute(text("DELETE FROM customer_demand"))
        if records:
            conn.execute(
                text(
                    """
                    INSERT INTO customer_demand (
                        articolo,
                        codice_articolo,
                        quantita,
                        data_spedizione,
                        priorita_cliente
                    )
                    VALUES (
                        :articolo,
                        :codice_articolo,
                        :quantita,
                        :data_spedizione,
                        :priorita_cliente
                    )
                    """
                ),
                records,
            )

    return {"ok": True, "records": len(records), "path": str(smf_path)}


def main() -> None:
    print(import_customer_demand_from_smf())


if __name__ == "__main__":
    main()
