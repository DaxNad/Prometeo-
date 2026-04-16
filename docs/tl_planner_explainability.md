# TL Planner – Explainability demo riproducibile

Questo documento spiega come attivare rapidamente una demo riproducibile per la spiegazione (post‑hoc) delle decisioni del sequence planner lato TL, senza modificare l’architettura esistente.

## Obiettivi
- Popolare l’ambiente (Railway) con un mini dataset di ordini ed eventi operativi.
- Verificare che machine‑load e sequence riflettano la pressione eventi.
- Ottenere una vista "explainable" della sequenza con motivazioni sintetiche per ogni item.

## Prerequisiti
- Backend PROMETEO deployato (Railway).
- BASE_URL dell’istanza, ad es.:
  - `https://prometeo-production-3855.up.railway.app`

## Seed e Smoke (GitHub Actions)
1. Orders Seed
   - Actions → `Orders Seed`
   - input `base_url` = BASE_URL
2. Events Seed
   - Actions → `Events Seed`
   - input `base_url` = BASE_URL, `station` = `ZAW-1`
3. Postdeploy Smoke
   - Actions → `Postdeploy Smoke`
   - input `base_url` = BASE_URL

Tutti e tre i workflow sono idempotenti ed utilizzano solo le API pubbliche.

## Verifica “live” da shell
- Snapshot forma + pressione eventi:
  ```bash
  BASE_URL="$BASE_URL" scripts/demo_snapshot.sh ZAW-1
  ```
- Controllo rapido machine‑load e sequence:
  ```bash
  curl -sS "$BASE_URL/production/machine-load" | jq '.items[] | select(.station=="ZAW-1") | {station, open_events_total, event_titles}'
  curl -sS "$BASE_URL/production/sequence" | jq '.items[] | select(.critical_station=="ZAW-1") | {critical_station, open_events_total, event_impact}'
  ```

## Explainability endpoint
- Endpoint diagnostico (non invasivo):
  - `GET /production/sequence/explain`
  - Restituisce la sequenza arricchita con campo `explain` per ciascun item:
    ```json
    {
      "ok": true,
      "explainable": true,
      "items": [
        {
          "critical_station": "ZAW-1",
          "open_events_total": 1,
          "event_impact": true,
          "explain": {
            "station": "ZAW-1",
            "summary": "Presenza di 1 evento/i OPEN su ZAW-1; Priorità planner: ...; Carico stimato: ...",
            "signals": {
              "events": {"open": 1, "impact": true},
              "priority": 1,
              "workload": 5
            }
          }
        }
      ]
    }
    ```

## Note di progetto
- Nessun cambio architetturale: l’explainability è un builder post‑hoc (`explain_global_sequence`) che lavora su payload esistenti.
- Idempotenza: gli script di seed possono essere rilanciati più volte senza effetti collaterali.
- Compatibilità DB: demo e seed usano solo le API pubbliche; lato test, SQLite in‑proc.

## Troubleshooting
- Se `open_events_total` resta 0:
  - rieseguire Events Seed su `ZAW-1`
  - verificare normalizzazione station (endpoint machine‑load mostra le chiavi `station` presenti)
- Se `/production/sequence/explain` restituisce `{ok:false}`:
  - controllare `/production/sequence` e lo stato dell’istanza ( `/health` )

