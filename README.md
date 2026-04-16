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

## Demo TL – Explainability (riproducibile)

Per una demo rapida dell’explainability del planner TL su Railway:

- Popola ordini ed eventi (Actions):
  1) `Orders Seed` → input `base_url`
  2) `Events Seed` → input `base_url`, `station` (es. ZAW-1)
  3) `Postdeploy Smoke` → input `base_url`

- Verifica “live” le chiavi attese:
  - `BASE_URL=<url> scripts/demo_snapshot.sh ZAW-1`

- Endpoint diagnostici:
  - `/production/sequence/explain` → sequenza con campo `explain` per item
  - `/production/explain` → item arricchiti con `priority_reason`, `risk_level`, `signals`

Note: gli script sono idempotenti e compatibili con PostgreSQL (via API).
