from __future__ import annotations

# Canonical SMF workbook schema used across adapter/writer/updater

REQUIRED_SCHEMA: dict[str, list[str]] = {
    "Codici": [
        "Codice",
        "Descrizione",
    ],
    "Postazioni": [
        "Postazione",
        "Note",
    ],
    "Pianificazione": [
        "ID ordine",
        "Cliente",
        "Codice",
        "Q.ta",
        "Data richiesta cliente",
        "Priorità",
        "Postazione assegnata",
        "Stato (da fare/in corso/finito)",
        "Progress %",
        "Semaforo scadenza",
        "Note",
    ],
    "DiscrepanzeLog": [
        "Timestamp",
        "Sorgente",
        "Voce",
        "Valore atteso",
        "Valore trovato",
        "Azione eseguita",
        "Esito",
    ],
}

