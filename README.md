# PROMETEO

[![Guards](https://github.com/DaxNad/Prometeo-/actions/workflows/guards.yml/badge.svg)](https://github.com/DaxNad/Prometeo-/actions/workflows/guards.yml)

PROMETEO e il monorepo operativo per supporto Team Leader in produzione.
Legge eventi, sequenze, vincoli e rischi senza assumere autorita produttiva autonoma.
Il backend espone API FastAPI e guard locali; il frontend espone PWA/dashboard operative.
La TL Chat e i guard servono a verificare risposte prudenti, sanificate e non mutative.
La documentazione backbone resta indicizzata qui per chiusura e runtime locale.

## Indice Operativo

- [PROMETEO_MASTER](docs/PROMETEO_MASTER.md)
- [PROMETEO_GOAL_COMPLETE_V1](docs/PROMETEO_GOAL_COMPLETE_V1.md)
- [GOAL_CLOSURE_BASELINE_001](docs/GOAL_CLOSURE_BASELINE_001.md)
- [RUNTIME_OPERATION_GUIDE_001](docs/RUNTIME_OPERATION_GUIDE_001.md)
- [APP_RUNTIME_CLOSURE_001](docs/APP_RUNTIME_CLOSURE_001.md)

## Check Locale

```bash
make goal-complete-v1
```

Baseline inclusa:

- TL Chat contract
- TL eval
- Data Leak Guard
- Privacy Guard
- controlli locali su file sensibili e session memory

## Dati E Memoria Locale

Nessun dato sensibile deve essere tracciato in git.
La session memory locale sotto `data/local_reports/session_memory/` e ignorata da git.
Appunti operativi locali restano nel repo locale e non nella memoria permanente ChatGPT.

## Struttura

- `backend/` - API FastAPI, servizi, guard e test
- `frontend/` - PWA e dashboard operative
- `docs/` - documentazione runtime, closure e backbone
- `scripts/` - utility operative e guard locali
