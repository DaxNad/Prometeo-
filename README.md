# PROMETEO

[![Guards](https://github.com/DaxNad/Prometeo-/actions/workflows/guards.yml/badge.svg)](https://github.com/DaxNad/Prometeo-/actions/workflows/guards.yml)

Monorepo ufficiale del sistema PROMETEO.

## Struttura

- backend/ → API FastAPI, logica server, database
- frontend/ → PWA / dashboard operativa
- smf_core/ → logica SuperMegaFile e processi produzione
- integrations/ → webhook e integrazioni esterne
- ai/ → moduli AI ATLAS
- board/ → governance progetto
- docs/ → documentazione tecnica e ADR
- scripts/ → utility operative

## Regola operativa

Le vecchie repository restano archiviate finché il monorepo non è stabile e verificato.

## Operazioni rapide richieste spesso

### Diff dei file modificati

```bash
git status --short
git diff --name-only
git diff
```

### Esempio payload finale JSON

```json
{
  "order_id": "ORD-2026-0007",
  "linea": "TL-ZAW1",
  "stazione": "SMD-03",
  "evento": "produzione_completata",
  "quantita_ok": 120,
  "quantita_ko": 2,
  "timestamp_utc": "2026-04-14T09:30:00Z",
  "operatore": "matricola-451",
  "note": "Batch chiuso senza blocchi"
}
```
