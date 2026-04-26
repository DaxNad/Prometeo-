# PROMETEO MASTER — Documento di contesto primario
> Unica fonte autorevole. Aggiornare solo a cambio architettura o milestone.
> Limite: 150 righe. Riferimento per Claude Code, Codex CLI, ChatGPT/Atlas.

---

## 1. Identità del sistema

PROMETEO non è un MES classico e non è un gestionale generico.
PROMETEO trasforma eventi di produzione in decisioni operative TL (DEFER/ALLOW/...).

Obiettivo operativo: trasformare segnalazioni di reparto in decisioni leggibili per il Team Leader.
Non sostituisce il TL — lo supporta con contesto, priorità e anomalie già elaborate.

Fuori perimetro: automazione PLC, CQRS, microservizi, full-automation.

---

## 2. Stack corrente

| Layer | Tecnologia |
|---|---|
| Backend | Python 3.11, FastAPI, SQLAlchemy |
| Database | PostgreSQL (Railway) + fallback SQLite locale |
| Frontend | React + Vite + TypeScript |
| Deploy | Railway (backend + DB) |
| Dati SMF | Excel SuperMegaFile → bridge `smf_update.py` |
| AI tools | Claude Code (arch), Codex CLI (patch), ChatGPT/Atlas (orchestrazione) |
| Auth | `X-API-Key` / `Bearer` via middleware, `PROMETEO_API_KEY` env |

---

## 3. Modello di dominio

Aggregate root: **Order**

```
Order → Phase → Station → ProductionEvent
```

Vocabolario tecnico (backend/DB): `ProductionEvent`, `Machine Load`, `Severity`, `Rule`, `Cluster`
Vocabolario TL (frontend/mobile): `Segnalazione operativa`, `Saturazione postazione`, `Impatto operativo`

Postazioni reali: ZAW-1, ZAW-2, PIDMILL, HENN, ULTRASUONI, CP, GUAINE
Chiave decisionale TL: **disegno** → famiglia articoli → postazioni → sequenza turno

Componenti condivisi tra articoli diversi sono il principale collo di bottiglia non ovvio.

---

## 4. Architettura layer

```
SMF (Excel) → smf_core → /smf/* API → BOMFamilyService → drawing_registry_service
                                                               ↓
ProductionEvent → /events/* → anomaly detection (atlas_engine)
                                    ↓
                         /planner/* decision layer
                         (DEFER / ALLOW + tl_actions)
                                    ↓
                         ATLAS Engine (constraint merge, explainability)
                                    ↓
                         Executor (run_test, crosscheck_bom — read-only)
                                    ↓
                         /production/sequence → TL board
```

Layer separator invariante: nessun layer scrive direttamente nel layer superiore.
Planner = overlay decisionale, non modifica dati di dominio.

---

## 5. Vincoli permanenti

1. Non cambiare architettura senza necessità esplicita.
2. Nessuna biforcazione tra smf_core / backend / planner / ATLAS / executor.
3. ProductionEvent è il log canonico operativo. Executor scrive solo eventi `TECHNICAL`.
4. Il planner non delega ranking a ATLAS — ATLAS arricchisce, SQL ordina.
5. SMF è bridge input, non fonte di verità primaria.
6. Drawing registry ha un solo reader canonico: `app/domain/drawing_registry_service.py`.
7. Executor: solo azioni read-only (run_test, crosscheck_bom). Nessuna mutazione domain.
8. ATLAS gate: decisioni BLOCK/DEFER non triggano executor salvo `executor_allowed=True` esplicito.
9. Signal classifier (`/signals/classify`): nessuna dipendenza da DB, puro compute.
10. Auth middleware: `/health`, `/ping`, `/db/ping`, `/postgres/ping`, `/`, `/docs` sempre pubblici.
11. Il disegno è la chiave primaria della decisione TL (famiglia → postazione → sequenza).

---

## 6. Stato loop decisionale (operativo)

Loop attivo:

```
eventi reali → anomaly detection → vincolo planner → DEFER/ALLOW → tl_actions
```

Endpoint operativi:
- `/events/anomaly` — anomalie rilevate da atlas_engine
- `/planner/sequence` — sequenza con decisione planner applicata
- `/planner/explain` — spiegazione decisione TL
- `/production/sequence` — dati grezzi (no overlay decisionale)
- `/signals/classify` — classificazione segnali esterni (email, notifiche)

Stato componenti:
- Backend API: ATTIVO
- PostgreSQL: ATTIVO
- Planner decision layer: ATTIVO (rule_v2)
- ATLAS Engine: ATTIVO (constraint merge, explainability)
- Executor: ATTIVO (read-only, guarded)
- SMF bridge: ATTIVO
- Auth middleware: ATTIVO
- Frontend dashboard: PARZIALE
- PWA mobile: IN SVILUPPO

---

## 7. Prossima milestone

Decision layer TL-aligned:
- introduzione stati: BLOCK / DEFER / ALLOW / BOOST
- integrazione severità evento nel decision layer
- gestione componenti condivisi come vincolo esplicito planner

File chiave da non toccare senza review: `api_production.py`, `sequence_planner.py`,
`drawing_registry_service.py`, `bom_family_service.py`, `executor/service.py`.

---

## Riferimenti

- Regole operative Claude Code: `CLAUDE.md` (root)
- Regole operative Codex: `AGENTS.md` (root)
- ADR decisioni architetturali: `docs/decisions/`
- TL strategy domain: `docs/domain/TL_strategy_guideline.md`
- Drawing behavior registry: `docs/domain/drawing_behavior_registry.json`

---

## PROMETEO — Colonna Vertebrale Operativa

PROMETEO non deve generare regressioni, biforcazioni o branch logici paralleli.

La colonna vertebrale operativa è unica:

1. `docs/PROMETEO_MASTER.md`
2. Agent Mod
3. Guard rails pre-modifica
4. Test minimi obbligatori
5. Codex CLI per patch operative
6. Claude Code solo per validazione architetturale
7. Executor solo dopo decisione valida

### Regola primaria

Nessun agente, tool o modifica codice può operare senza:

- obiettivo dichiarato
- file ammessi
- file vietati
- test minimi
- impatto previsto su Order → Route → Station → ProductionEvent
- conferma che non crea biforcazioni tra SMF bridge, backend e frontend

### Divieto di dispersione memoria

È vietato creare nuovi layer documentali paralleli per contesto operativo.

Tutto ciò che è stabile, permanente o architetturale deve convergere in:

`docs/PROMETEO_MASTER.md`

Sono ammessi file secondari solo se tecnici, esecutivi o derivati, ma non devono diventare fonte primaria di verità.

### Regola anti-branch separati

Ogni branch deve avere uno scope chiuso e ricongiungibile.

Sono vietati branch che introducono:

- nuova logica parallela
- nuovo modello dominio alternativo
- nuovo planner non allineato
- nuovo executor non validato
- nuovo SMF bridge separato
- documentazione primaria duplicata

### Gate obbligatorio prima di ogni modifica

Prima di ogni modifica PROMETEO devono essere definiti:

1. obiettivo
2. file ammessi
3. file vietati
4. test minimi
5. rischio regressione
6. impatto dominio
7. agente corretto da usare

### Ordine agenti

Ordine stabile:

1. ChatGPT = orchestratore logico e dominio TL
2. Codex CLI = patch codice, test, fix mirati
3. Claude Code = validazione architetturale
4. Agent Mod = gate obbligatorio
5. Executor = esecuzione controllata solo dopo decisione valida

### Regola finale

Se una modifica non può essere spiegata rispetto alla catena:

`Order → Route → Station → ProductionEvent`

allora la modifica deve essere bloccata o riportata a scope.

