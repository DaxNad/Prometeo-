# CLAUDE.md — Guida per assistenti AI

Questo file descrive la struttura, i workflow e le convenzioni del progetto PROMETEO per garantire continuità tra sessioni AI.

---

## 1. Panoramica del progetto

**PROMETEO** è una piattaforma modulare di monitoraggio e orchestrazione per reparti produttivi manifatturieri. Il sistema raccoglie eventi di produzione, li analizza tramite un layer AI (ATLAS/Claude), e li espone tramite una dashboard operativa.

- **Versione corrente backend:** 0.3.1
- **Deployment:** Railway (NIXPACKS)
- **Repository:** monorepo Git

### Stato attuale dei moduli

| Modulo | Stato |
|---|---|
| Backend API (FastAPI) | ATTIVO |
| Deploy Railway | ATTIVO |
| Swagger/OpenAPI | ATTIVO |
| Event Engine | ATTIVO |
| Search Engine | ATTIVO MA VUOTO (dati da popolare) |
| Frontend Dashboard | PARZIALE |
| Database PostgreSQL | PARZIALE (configurato, non ancora sorgente primaria) |
| AI Layer / ATLAS | IN SVILUPPO |
| Development OS | ATTIVO |

---

## 2. Struttura del monorepo

```
Prometeo-/
├── backend/            # API FastAPI, logica server, database
├── frontend/           # PWA/dashboard React+TypeScript (attiva)
├── frontend_legacy/    # Vecchio frontend JavaScript (archiviato)
├── smf_core/           # SuperMegaFile — logica Excel produzione
├── integrations/       # Webhook e integrazioni esterne
├── board/              # Governance: MASTER_CONTROL, TASK_BOARD, SYSTEM_LOG
├── docs/               # Documentazione tecnica e ADR
├── scripts/            # Script operativi e di deploy
├── railway.json        # Configurazione deploy Railway
└── CLAUDE.md           # Questo file
```

---

## 3. Stack tecnologico

### Backend
- **Framework:** FastAPI (Python)
- **Server ASGI:** Uvicorn
- **ORM:** SQLAlchemy
- **Database:** PostgreSQL (produzione) / SQLite (sviluppo locale fallback)
- **Driver DB:** psycopg2-binary (Postgres), sqlite3 (stdlib)
- **Elaborazione dati:** pandas 2.2.3, openpyxl 3.1.5
- **HTTP client:** requests
- **AI:** Anthropic Claude API (`claude-sonnet-4-20250514`) via chiamate HTTP dirette

### Frontend
- **Framework:** React 19.2.0
- **Linguaggio:** TypeScript 5.9.3
- **Build tool:** Vite 7.3.1
- **Linting:** ESLint 9.39.1

### Deployment
- **Piattaforma:** Railway
- **Builder:** NIXPACKS (autodiscovery)
- **Start command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Restart policy:** ON_FAILURE, max 10 tentativi

---

## 4. Struttura del backend in dettaglio

```
backend/
├── app/
│   ├── main.py                     # Entry point FastAPI, router registration, startup
│   ├── config.py                   # Settings: versione, DB backend, percorsi
│   ├── db.py                       # Inizializzazione DB, probe postgres
│   ├── schemas.py                  # Modelli Pydantic (EventCreate, EventItem...)
│   ├── rules.py                    # Regole di business
│   ├── events.py                   # Logica eventi (in-memory)
│   ├── search.py                   # Logica motore di ricerca
│   ├── repository.py               # Repository legacy
│   ├── api_production.py           # Endpoint ordini produzione
│   ├── api_search.py               # Endpoint ricerca
│   ├── api_smf.py                  # Adapter SuperMegaFile
│   ├── api_dashboard.py            # Endpoint dashboard
│   ├── api_legacy.py               # Compatibilità API legacy
│   ├── prometeo_client.py          # Utility client
│   │
│   ├── api/                        # Router API modulari
│   │   ├── agent_runtime.py        # Analisi AI in tempo reale
│   │   ├── devos.py                # Development OS endpoints
│   │   ├── devos_status.py         # Status Development OS
│   │   ├── events.py               # CRUD eventi
│   │   ├── postgres_probe.py       # Probe connessione Postgres
│   │   ├── production_events.py    # Eventi produzione
│   │   ├── state.py                # Gestione stato
│   │   └── routes/dev_db_init.py   # Init DB in sviluppo
│   │
│   ├── db/                         # Layer database SQLAlchemy
│   │   ├── session.py              # SessionFactory, Base
│   │   ├── models.py               # ORM: EventRecord, StateRecord
│   │   └── init_db.py              # Bootstrap tabelle
│   │
│   ├── repositories/               # Pattern Repository
│   │   ├── events_repository.py    # Interface astratta
│   │   ├── sqlite_events_repository.py
│   │   ├── postgres_events_repository.py
│   │   └── factory.py              # Selezione backend (sqlite/postgres)
│   │
│   ├── services/                   # Business logic
│   │   ├── event_service.py        # Gestione eventi
│   │   ├── sequence_planner.py     # Pianificazione sequenze produzione
│   │   ├── devos_service.py        # Development OS service
│   │   ├── anthropic_provider.py   # Integrazione Claude API
│   │   └── prompt_builder.py       # Costruzione prompt AI
│   │
│   ├── agent_runtime/              # Runtime AI per analisi eventi
│   │   ├── service.py              # Servizio principale (analyze, list_runs, summary)
│   │   ├── decision_engine.py      # Logica decisionale locale
│   │   ├── run_repository.py       # Persistenza run AI
│   │   ├── schemas.py              # Schemi runtime
│   │   ├── inspectors.py           # Ispezione eventi
│   │   ├── policy.py               # Policy runtime
│   │   ├── registry.py             # Registro
│   │   ├── provider_factory.py     # Selezione provider AI
│   │   ├── runtime_hook.py         # Hook trigger
│   │   ├── tools/event_inspector.py
│   │   └── providers/
│   │       ├── base.py             # Provider base
│   │       ├── atlas.py            # Provider ATLAS
│   │       └── noop.py             # Provider no-op
│   │
│   ├── agent_mod/                  # Validazione modifiche agenti AI
│   │   ├── runtime.py / runner.py  # Esecuzione
│   │   ├── gates.py                # Gate di validazione
│   │   ├── probes.py               # Probe di sistema
│   │   ├── snapshot.py             # Snapshot persistenza
│   │   ├── contracts.py            # Definizione contratti
│   │   ├── contracts_registry.py   # Registro contratti
│   │   └── cli.py                  # Interfaccia CLI
│   │
│   ├── smf/                        # Adapter SuperMegaFile (Excel)
│   │   ├── smf_adapter.py
│   │   ├── smf_reader.py
│   │   ├── smf_writer.py
│   │   └── smf_updater.py
│   │
│   └── importers/                  # Import dati
│       ├── import_bom_json.py
│       ├── import_customer_demand.py
│       └── materialize_component_usage.py
│
├── sql/                            # Schema SQL numerati (001–010)
├── tests/
│   └── test_e2e_production.py      # Test E2E con httpx
└── requirements.txt
```

---

## 5. Modelli dati principali

### ORM SQLAlchemy (`backend/app/db/models.py`)

```python
EventRecord       # event_type, source, payload(JSON), created_at
StateRecord       # state_key (unique), state_value, updated_at
```

### Pydantic schemas (`backend/app/schemas.py`)
- `EventCreate`, `EventItem` — creazione e lettura eventi
- Payload sempre serializzato come JSON text nel DB

### Terminologia di dominio (italiano)
Il codice usa termini italiani per il dominio manifatturiero:
- `stato` — valori: `"da fare"`, `"in corso"`, `"finito"`, `"bloccato"`
- `semaforo` — indicatore visivo stato
- `postazione` — stazione di lavoro
- `linea` — linea di produzione (es: `zaw1`, `zaw2`, `henn`, `pidmill`)
- `operatore` — operatore macchina
- `commessa` / `ordine` — ordine di produzione
- `tl` — team leader

---

## 6. Configurazione e variabili d'ambiente

Il file di configurazione è `backend/app/config.py` (classe `Settings`).

| Variabile | Default | Descrizione |
|---|---|---|
| `DATABASE_URL` | `""` | Connection string PostgreSQL. Se vuota → SQLite |
| `PROMETEO_DB_BACKEND` | auto | `"sqlite"` o `"postgres"` (override manuale) |
| `PROMETEO_DATA_DIR` | `backend/app/data/` | Directory dati e SQLite |
| `PORT` | — | Porta server (iniettata da Railway) |
| `ANTHROPIC_API_KEY` | — | Chiave API Anthropic per Claude |

**Logica selezione DB:**
1. Se `PROMETEO_DB_BACKEND` è esplicito → usa quello
2. Se `DATABASE_URL` è presente → postgres
3. Altrimenti → sqlite (sviluppo locale)

---

## 7. API endpoints principali

| Metodo | Path | Descrizione |
|---|---|---|
| GET | `/` | Serve frontend dist o JSON info |
| GET | `/health` | Health check completo (DB, versione, AI status) |
| GET | `/ping` | Liveness probe |
| HEAD | `/ping` | Liveness probe (HEAD) |
| — | `/events/*` | CRUD eventi |
| — | `/production/*` | Ordini e sequenze produzione |
| — | `/search?q=...` | Ricerca dataset |
| — | `/smf/*` | SuperMegaFile adapter |
| — | `/state/*` | Gestione stato |
| — | `/dev/*` | Development OS (status, tasks, logs) |
| — | `/agent-runtime/*` | Analisi AI runtime eventi |
| GET | `/docs` | Swagger UI (auto-generato) |
| GET | `/openapi.json` | Schema OpenAPI |

---

## 8. Integrazione AI (Claude)

Il sistema usa Claude via API diretta HTTP (non SDK):

**File:** `backend/app/services/anthropic_provider.py`
- Funzione: `claude_chat(prompt, model, max_tokens, temperature, system)`
- Modello default: `claude-sonnet-4-20250514`
- Richiede: `ANTHROPIC_API_KEY` in ambiente
- System prompt: risponde sempre in italiano, formato operativo
  ```
  AZIONE_TL: ...
  MOTIVO: ...
  PRIORITA: CRITICA | ALTA | MEDIA | BASSA
  ```

**File:** `backend/app/services/prompt_builder.py`
- Costruisce il prompt per `AgentRuntimeService`

**AgentRuntimeService** (`backend/app/agent_runtime/service.py`):
1. Ispeziona l'evento (`inspect_event`)
2. Decide localmente (`decide`)
3. Arricchisce la spiegazione con Claude
4. Persiste il run (`AgentRunRepository`)

---

## 9. Schema SQL — convenzioni di numerazione

I file SQL in `backend/sql/` seguono una numerazione progressiva:

```
001_create_events_table.sql     # Tabella eventi base
002_postgres_events.sql         # Tabella eventi PostgreSQL
003_bom_registry.sql            # BOM (Bill of Materials)
004_*                           # Varianti BOM, assiemi
005_*                           # Alert varianti TL
006_*                           # Component usage, viste critici, semantiche ZAW
007_*                           # Customer demand, viste sequenze ZAW1/ZAW2
008_*                           # Semantiche HENN, board TL
009_*                           # Semantiche PIDMILL
010_*                           # Machine load summary
dev_bootstrap_views.sql         # Viste per sviluppo
sequence_planner_views.sql      # Viste pianificatore sequenze
```

**Regola:** aggiungere nuovi file con numero progressivo. Non modificare file esistenti in produzione senza migration controllata.

---

## 10. Frontend

```
frontend/
├── src/
│   ├── main.tsx                        # Entry point React
│   ├── App.tsx                         # Root component
│   ├── pages/ProductionDashboard.tsx   # Dashboard principale
│   ├── hooks/useProductionBoard.ts     # Hook stato dashboard
│   ├── lib/api/prometeo.ts             # Client API verso backend
│   └── types/production.ts             # Tipi TypeScript
├── vite.config.ts
├── package.json
└── tsconfig.json
```

**Comandi:**
```bash
cd frontend
npm install
npm run dev       # dev server con proxy verso backend :8000
npm run build     # tsc + vite build → dist/
npm run lint      # ESLint
```

Il backend serve la build da `frontend/dist/` se presente.

---

## 11. Workflow di sviluppo locale

### Avvio backend
```bash
cd backend
export PYTHONPATH=.
# opzionale: source .env
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Oppure usa lo script:
```bash
./scripts/dev_start.sh   # avvia uvicorn, attende health, esegue agent runtime gate
./scripts/dev_stop.sh    # termina processo su porta 8000
./scripts/dev_status.sh  # mostra stato sviluppo
```

**Note:** `dev_start.sh` presuppone root in `$HOME/Documents/PROMETEO`. In questo monorepo adatta i percorsi se necessario.

### Verifica salute
```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/ping
```

### Test E2E
```bash
cd backend
pytest tests/test_e2e_production.py
```
I test usano `httpx`. Non c'è un framework di unit test formale al momento.

---

## 12. Deploy su Railway

1. Ogni push su `main` triggera il deploy automatico
2. Builder: NIXPACKS (autodiscovery Python da `requirements.txt`)
3. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Gate pre/post deploy: `scripts/railway_predeploy_gate.sh`, `scripts/railway_postdeploy_gate.sh`
5. Variabili d'ambiente da impostare in Railway: `DATABASE_URL`, `ANTHROPIC_API_KEY`

---

## 13. Development OS (Governance)

Il progetto usa un sistema di governance basato su file Markdown in `board/`:

| File | Scopo |
|---|---|
| `board/MASTER_CONTROL.md` | Stato generale, blocchi aperti, prossimi passi |
| `board/TASK_BOARD.md` | Task attivi e backlog |
| `board/SYSTEM_LOG.md` | Log decisioni e avanzamento |
| `docs/decisions/ADR-001-*.md` | Architecture Decision Records |
| `docs/prometeo_system_map.md` | Mappa architetturale ufficiale |
| `docs/prometeo_boot_protocol.md` | Protocollo di avvio sessioni AI |

**Questi file sono letti via API** da endpoint `/dev/status`, `/dev/tasks`, `/dev/logs`.

**Regola:** ogni decisione architetturale significativa va registrata in `board/SYSTEM_LOG.md` e, se strutturale, in un ADR in `docs/decisions/`.

---

## 14. Convenzioni di codice

### Naming
- **Moduli Python:** `snake_case`
- **Classi:** `PascalCase`
- **Variabili/funzioni:** `snake_case`
- **Route API:** kebab-case prefix (`/production`, `/agent-runtime`, `/dev`)
- **Tabelle DB:** `snake_case` (`event_records`, `state_records`)

### Pattern architetturali
- **Repository Pattern:** interfaccia astratta + implementazioni SQLite/Postgres
- **Factory Pattern:** `factory.py` seleziona l'implementazione a runtime
- **Service Layer:** logica business nei `services/`, non nei router
- **Dependency Injection:** FastAPI `Depends()` per repository/servizi
- **Pydantic:** per tutti i modelli di input/output API

### Risposta API standard
```json
{ "ok": true, "data": ..., "count": ... }
{ "ok": false, "error": "...", "detail": "..." }
```

### AI responses (dominio)
L'AI risponde sempre in italiano con formato strutturato:
```
AZIONE_TL: <azione consigliata al team leader>
MOTIVO: <motivazione sintetica>
PRIORITA: CRITICA | ALTA | MEDIA | BASSA
```

---

## 15. Priorità architetturali correnti

In ordine di priorità (da `board/MASTER_CONTROL.md`):

1. **Stabilizzazione frontend** — completare dashboard operativa
2. **Integrazione PostgreSQL** — rendere Postgres sorgente primaria reale
3. **Consolidamento Event Engine** — persistenza eventi dopo restart
4. **Search Engine** — popolare dati reali nel motore di ricerca
5. **AI Layer ATLAS** — formalizzare dopo consolidamento core

---

## 16. File da non modificare senza consenso esplicito

- `backend/sql/00*_*.sql` — schemi in produzione (usare nuovi file numerati)
- `railway.json` — configurazione deploy
- `board/MASTER_CONTROL.md` — stato ufficiale del progetto
- `docs/decisions/ADR-*.md` — record decisionali storici

---

## 17. Checklist per nuove funzionalità

1. Aggiungere endpoint in un router dedicato (`backend/app/api/`)
2. Definire schema Pydantic in `schemas.py` o modulo apposito
3. Implementare logica in `services/` (non nel router)
4. Se serve nuovo schema DB: aggiungere file SQL numerato in `backend/sql/`
5. Aggiornare `board/TASK_BOARD.md` e `board/SYSTEM_LOG.md`
6. Aggiornare `board/MASTER_CONTROL.md` se cambia lo stato di un modulo
7. Registrare in un ADR se la decisione è architetturalmente significativa
