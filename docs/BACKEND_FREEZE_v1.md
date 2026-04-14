# PROMETEO BACKEND FREEZE v1

## Scopo
Congelare lo stato attuale del backend PROMETEO come baseline operativa stabile.

---

## Stato attuale riconosciuto

### CORE OPERATIVO
Componenti che fanno parte del cuore reale del sistema:

- FastAPI app principale
- Event Engine
- State Engine
- endpoint health/ping
- persistenza SQLite locale
- integrazione dashboard operativa

### DEVELOPMENT OS
Componenti che servono per governo progetto e visibilità tecnica:

- /dev/status
- /dev/tasks
- /dev/logs
- /dev/milestones
- board/
- pannello DevOS UI

### LEGACY / TRANSIZIONE
Componenti da considerare in osservazione o da riallineare:

- frontend_legacy
- api_legacy.py
- services_legacy.py
- vecchie parti bootstrap non più centrali
- parti cloud non ancora allineate alla dashboard locale avanzata

---

## Albero logico backend congelato

### backend/app/main.py
Ruolo:
entrypoint FastAPI principale

### backend/app/api/events.py
Ruolo:
Event Engine API

### backend/app/api/state.py
Ruolo:
State Engine API

### backend/app/api/devos.py
Ruolo:
Development OS API

### backend/app/services/devos_service.py
Ruolo:
lettura registri board e maturity matrix

### backend/app/db.py
Ruolo:
persistenza SQLite locale

### backend/ui/devos.html
Ruolo:
pannello browser DevOS

---

## Classificazione moduli

| Modulo | Classe | Stato |
|---|---|---|
| main.py | CORE | STABILE |
| api/events.py | CORE | STABILE |
| api/state.py | CORE | STABILE |
| db.py | CORE | STABILE |
| api/devos.py | DEVOS | STABILE |
| services/devos_service.py | DEVOS | STABILE |
| ui/devos.html | DEVOS | STABILE |
| api_legacy.py | LEGACY | DA VALUTARE |
| services_legacy.py | LEGACY | DA VALUTARE |
| frontend_legacy | LEGACY | DA VALUTARE |

---

## Regole freeze

1. Non modificare più la struttura base senza registrazione su board e system log
2. Ogni nuova evoluzione deve dichiarare se appartiene a:
   - CORE
   - DEVOS
   - LEGACY
3. Nessun refactor strutturale non tracciato
4. PostgreSQL sarà evoluzione del CORE, non sostituzione confusa
5. Cloud UI va riallineata senza rompere la baseline locale

---

## Baseline operativa v1

PROMETEO backend v1 congelato come:

- CORE operativo locale funzionante
- DEVOS integrato
- SQLite attivo
- dashboard locale attiva
- pannello DevOS attivo

---

## Nota tecnica mirata: ATLAS Merge v1 adapter (backend)

- Endpoint diagnostico non invasivo: `GET /production/sequence/atlas-merge`
- Integrazione post-hoc lato service/adapter: usa `sequence_planner_service.build_global_sequence(...)` e applica merge deterministico puro Python.
- Payload stabile esposto per consumer backend:
  - `final_outcome`
  - `final_score`
  - `reasons`
  - `active_constraints`
  - `conflicts`
  - `consensus`
  - `explain_brief`
- Nessun accesso DB nel modulo merge (`backend/app/services/atlas_merge.py`), nessuna modifica ai contratti pubblici esistenti `/production/sequence` e `/production/turn-plan`.
