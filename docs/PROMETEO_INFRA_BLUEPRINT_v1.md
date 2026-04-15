# PROMETEO — Minimal Infra Blueprint v1

> Documento architetturale di riferimento.
> Definisce confini, responsabilità e vincoli dell'infrastruttura minima PROMETEO.
> Basato sul codebase esistente — nessuna speculazione futura.

---

## 1. Schema moduli architettura

```
┌─────────────────────────────────────────────────────────────────┐
│                        PROMETEO SYSTEM                          │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    BACKEND CENTRALE                      │   │
│  │                                                          │   │
│  │  ┌─────────────┐   ┌──────────────┐   ┌─────────────┐   │   │
│  │  │  PROMETEO   │   │    PLANNER   │   │  DECISION   │   │   │
│  │  │    CORE     │──▶│ (determin.)  │──▶│   MERGE     │   │   │
│  │  │  FastAPI    │   │ sequence_    │   │ atlas_merge  │   │   │
│  │  │  API routes │   │ planner.py   │   │    .py      │   │   │
│  │  │  db / cfg   │   └──────────────┘   └─────────────┘   │   │
│  │  └──────┬──────┘           │                 │           │   │
│  │         │                  ▼                 ▼           │   │
│  │         │     ┌────────────────┐   ┌──────────────────┐  │   │
│  │         │     │  ATLAS ENGINE  │   │ SIGNAL CLASSIFIER│  │   │
│  │         │     │  (ottimizz.)   │   │  agent_runtime/  │  │   │
│  │         │     │  OR-Tools /    │   │  inspectors.py   │  │   │
│  │         │     │  Pyomo         │   │  + Claude enrich │  │   │
│  │         │     └────────────────┘   └──────────────────┘  │   │
│  │         │                                                 │   │
│  │         ▼                                                 │   │
│  │  ┌─────────────┐                                          │   │
│  │  │ SMF BRIDGE  │◀────── sync controllata ────────────┐   │   │
│  │  │ smf/adapter │                                      │   │   │
│  │  │ smf_reader  │                                      │   │   │
│  │  │ smf_writer  │                                      │   │   │
│  │  └──────┬──────┘                                      │   │   │
│  └─────────┼────────────────────────────────────────────-┘   │   │
│            │                                                  │   │
│  ┌─────────▼──────────────────────────────────────────────┐  │   │
│  │                    PROMETEO EDGE                        │  │   │
│  │                      smf_core/                          │  │   │
│  │          lettura/scrittura Excel autonoma               │  │   │
│  │          zero dipendenze da backend                     │  │   │
│  └─────────────────────────────────────────────────────────┘  │   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Responsabilità per modulo

| Modulo | Path codebase | Responsabilità | Dipendenze ammesse |
|---|---|---|---|
| **PROMETEO CORE** | `backend/app/` | API FastAPI, routing, config, session DB, health | PostgreSQL, SQLite fallback |
| **PROMETEO EDGE** | `smf_core/` | Lettura/scrittura Excel SMF, autonomia totale | stdlib, openpyxl — nient'altro |
| **ATLAS ENGINE** | `backend/app/atlas_engine/` | Ottimizzazione sequenza, vincoli, obiettivo | OR-Tools / Pyomo (adattatori isolati) |
| **SMF BRIDGE** | `backend/app/smf/` | Adattatore tra EDGE e CORE, ingest OCR, parsing | smf_core (opzionale), stdlib |
| **PLANNER** | `backend/app/services/sequence_planner.py` | Sequenza deterministica per turno, priorità, stazioni | PostgreSQL views, CORE |
| **DECISION MERGE** | `backend/app/services/atlas_merge.py` | Fusione segnali PLANNER + ATLAS + CLASSIFIER → azione finale | PLANNER, ATLAS, CLASSIFIER |
| **SIGNAL CLASSIFIER** | `backend/app/agent_runtime/inspectors.py` | Analisi evento, severity, contesto | CORE, Claude API (opzionale) |

---

## 3. Confini runtime

```
┌────────────────────────────────────────────────────────────┐
│  EDGE LOCALE (reparto, no network)                         │
│                                                            │
│  • smf_core — lettura/scrittura Excel                      │
│  • SQLite — cache locale eventi e sequenza                 │
│  • fallback sequence — ordinamento CRITICA-first offline   │
│                                                            │
│  Garanzia: funziona senza backend attivo                   │
└──────────────────────┬─────────────────────────────────────┘
                       │ sync controllata (pull/push)
┌──────────────────────▼─────────────────────────────────────┐
│  BACKEND CENTRALE (Railway, network required)               │
│                                                            │
│  • FastAPI — API produzione, dashboard, SMF ingest         │
│  • PostgreSQL — source of truth eventi, ordini, sequenza   │
│  • Atlas Engine — ottimizzazione vincoli                   │
│  • Agent Runtime — analisi + decisione                     │
│  • Claude API — enrichment spiegazioni (opzionale)         │
└────────────────────────────────────────────────────────────┘
```

### Matrice offline/sync

| Operazione | Edge locale | Sync richiesta |
|---|---|---|
| Lettura ordini da SMF Excel | ✅ | ✗ |
| Scrittura su SMF Excel | ✅ | ✗ |
| Sequenza fallback (CRITICA-first) | ✅ | ✗ |
| Cache eventi SQLite | ✅ | ✗ |
| Scrittura eventi su PostgreSQL | ✗ | ✅ |
| Ottimizzazione ATLAS | ✗ | ✅ |
| Analisi agent runtime | ✗ | ✅ |
| Spiegazione Claude | ✗ | ✅ (opzionale) |
| Dashboard board | ✗ | ✅ |

---

## 4. Separazione deterministico vs probabilistico

### 4.1 Vincoli hard — deterministici (non delegabili ad AI)

```
REGOLE BLOCCANTI — SEMPRE APPLICATE DAL PLANNER

  CP  →  fase finale bloccante
          nessun ordine può essere messo dopo CP senza completamento
          implementato in: sequence_planner.py

  HENN → ZAW
          HENN deve precedere qualsiasi assegnazione ZAW
          implementato in: sequence_planner.py (ordine stazioni)

  Priorità ordinamento:
          CRITICA (0) > ALTA (1) > MEDIA (2) > BASSA (3)
          implementato in: sequence_planner.py, vw_*_sequence_ranked

  Componenti condivisi (o-ring):
          se componente in uso su ordine attivo → priorità aumentata
          implementato in: component_usage table, constraint_builder.py

  Merge restrittivo:
          in conflitto tra segnali → vince la decisione più conservativa
          implementato in: atlas_merge.py

  Stazioni fisse:
          ZAW-1, ZAW-2, HENN, PIDMILL, CP, NON_ASSEGNATA
          non configurabili a runtime — enum hardcoded
```

### 4.2 Suggerimenti AI — probabilistici (override umano sempre possibile)

```
SEGNALI SOFT — ATLAS / CLASSIFIER / CLAUDE

  ATLAS score       →  suggerisce riordino sequenza entro vincoli hard
  Severity event    →  classifica urgenza evento (non blocca, informa)
  Spiegazione NL    →  Claude genera testo per team leader (mai decisione)
  Anomaly signal    →  inspectors.py segnala pattern anomalo (non agisce)
```

### 4.3 Regola di composizione

```
Input eventi
    │
    ▼
SIGNAL CLASSIFIER  ──→  segnale soft (confidence + severity)
    │
    ▼
PLANNER            ──→  sequenza deterministica (vincoli hard)
    │
    ▼
ATLAS ENGINE       ──→  ottimizzazione entro vincoli (score)
    │
    ▼
DECISION MERGE     ──→  merge restrittivo → azione finale
    │
    ▼
Output: sequenza confermata + spiegazione opzionale Claude
```

**Regola invariante:** nessun segnale AI può violare un vincolo hard.
Se ATLAS suggerisce una sequenza che viola HENN→ZAW, il PLANNER la rigetta prima del merge.

---

## 5. Storage minimale

### Schema autorità dati

```
                    FONTE AUTORITARIA REPARTO
                    ┌──────────────────────┐
                    │   SMF Excel (xlsx)    │
                    │  ordini produzione    │
                    │  leggibile da operai  │
                    └──────────┬───────────┘
                               │ ingest via SMF BRIDGE
                               ▼
                    FONTE AUTORITARIA SISTEMA
                    ┌──────────────────────┐
                    │     PostgreSQL        │
                    │  events, agent_runs   │
                    │  state, BOM, comps    │
                    │  sequence history     │
                    └──────────────────────┘
                               │
                    ┌──────────▼───────────┐
                    │  SQLite (opzionale)   │
                    │  fallback edge locale │
                    │  cache sequenza       │
                    └──────────────────────┘
```

### Tabella storage per tipo dato

| Dato | Storage | Motivo |
|---|---|---|
| Ordini produzione attivi | SMF Excel + PostgreSQL | Excel = reparto, PG = sistema |
| Eventi produzione | PostgreSQL (`event_records`) | persistenza centrale |
| Decisioni agent | PostgreSQL (`agent_runs`) | audit trail |
| Stato sistema | PostgreSQL (`state_records`) | key-value operativo |
| BOM + componenti | PostgreSQL (`bom_registry`, `component_usage`) | vincoli condivisi |
| Sequenza ottimizzata | PostgreSQL (viste `vw_*_board`) | source of truth turno |
| Cataloghi stazioni / codici | JSON file locali | semplici, read-only |
| Schema SMF validazione | JSON (`smf_schema.py` + constants) | non ha senso in DB |
| Cache offline edge | SQLite (`prometeo_edge.db`) | solo fallback, non primario |
| Spiegazioni Claude | PostgreSQL (`agent_runs.explanation`) | parte del run record |

### Tabelle PostgreSQL in uso (effettive)

```sql
event_records       -- eventi produzione (tipo, source, payload, ts)
state_records       -- stato key-value sistema
agent_runs          -- log decisioni agent (inspection, action, explanation)
bom_registry        -- distinta base componenti
component_usage     -- uso componenti per ordine (o-ring conflict detection)

-- Viste materializzate (read-only per PLANNER)
vw_tl_zaw1_board
vw_tl_zaw2_board
vw_zaw1_sequence_ranked
```

---

## 6. Regole anti-complessità

### 6.1 Cosa NON introdurre ora

| Pattern / Tecnologia | Motivo del blocco |
|---|---|
| Message broker (Kafka, RabbitMQ, Redis Pub/Sub) | Event-driven = modello, non bus fisico; PostgreSQL è sufficiente |
| Microservizi separati | Monolite FastAPI copre il perimetro attuale senza overhead |
| WebSocket real-time | Dashboard pull è sufficiente; push streaming non giustificato |
| GraphQL | REST + FastAPI schema è già tipizzato; GraphQL aggiunge layer senza beneficio |
| gRPC | Comunicazione interna via chiamate Python dirette — nessun boundary di rete interno |
| Redis cache | PostgreSQL con viste + SQLite fallback coprono il caching necessario |
| Server AI separato (Ollama, TGI) | Claude API remota è sufficiente; inference locale solo se connectivity muore |
| Alembic / migration framework | Raw SQL migrations in `/sql/` sotto controllo — non aggiungere ORM layer |
| Event sourcing completo | Log eventi è sufficiente; ES completo cambia il modello di query senza vantaggio ora |
| Docker multi-service orchestration | Railway gestisce il deploy; Compose locale solo se necessario per test |
| Separazione smf_core ↔ backend via HTTP | smf_core è edge autosufficiente — il bridge è adattatore Python, non servizio separato |

### 6.2 Componenti da evitare prematuramente

```
❌  Celery / task queue asincrona
    → le operazioni ATLAS sono < 2s su dataset reale; non serve async queue

❌  Sistema di notifiche push (FCM, APNS)
    → dashboard pull è sufficiente per il reparto attuale

❌  Multi-tenant / multi-plant
    → PROMETEO è mono-reparto; non anticipare generalizzazione

❌  Feature flags / configurazione runtime dinamica
    → le regole di produzione cambiano raramente; hardcode è più sicuro

❌  Caching distribuito (Memcached, Redis)
    → SQLite edge + PostgreSQL views coprono il caso d'uso

❌  API versioning (v1/v2 prefix)
    → con un solo client (dashboard interna) è overhead prematuro
```

### 6.3 Pattern architetturali da evitare

```
❌  Biforcazione smf_core ↔ backend
    smf_core deve restare autosufficiente.
    Non aggiungere chiamate HTTP da smf_core verso backend.

❌  Logica business nelle API route
    Le route espongono; la logica sta nei service e nel planner.

❌  Dipendenze circolari tra moduli
    CORE → PLANNER → ATLAS → MERGE (unidirezionale)
    nessun modulo chiama il padre nella catena.

❌  Vincoli hard delegati ad AI
    HENN→ZAW, CP finale, priorità: mai overridabili da score AI.

❌  Persistenza in memoria (dict globali, variabili di modulo)
    Ogni stato operativo va su PostgreSQL. La memoria è volatile.
```

---

## 7. Mappa flusso operativo completo

```
OPERATORE REPARTO
      │
      │  scrive/aggiorna ordine su SMF Excel
      ▼
PROMETEO EDGE (smf_core)
      │
      │  lettura Excel → struttura ordine validata
      ▼
SMF BRIDGE (backend/app/smf/)
      │
      │  ingest → normalizzazione → scrittura PostgreSQL
      ▼
PROMETEO CORE (FastAPI)
      │
      ├──▶ SIGNAL CLASSIFIER
      │         analisi evento → severity → confidence
      │
      ├──▶ PLANNER
      │         sequenza deterministica → vincoli hard applicati
      │         HENN→ZAW, CP bloccante, priorità
      │
      ├──▶ ATLAS ENGINE
      │         ottimizzazione score entro vincoli confermati
      │
      └──▶ DECISION MERGE
                merge restrittivo → azione finale
                      │
                      ├──▶ SIGNAL CLASSIFIER (Claude enrich, opzionale)
                      │         spiegazione NL per team leader
                      │
                      └──▶ PostgreSQL (agent_runs)
                                persistenza decisione + audit

DASHBOARD (frontend)
      │
      │  pull sequenza / board / load
      ▼
TEAM LEADER
      │
      │  override umano sempre possibile
      ▼
SMF BRIDGE (scrittura)
      │
      └──▶ SMF Excel aggiornato → PROMETEO EDGE
```

---

## 8. Invarianti di sistema — non negoziabili

```
1.  PostgreSQL è l'unica fonte di verità per lo stato del sistema.
    SQLite è solo cache edge temporanea.

2.  smf_core non chiama mai il backend.
    La comunicazione è unidirezionale: BRIDGE legge da EDGE, non viceversa.

3.  Vincoli hard non sono configurabili a runtime.
    CP finale e HENN→ZAW sono nel codice, non in tabelle configurazione.

4.  Merge restrittivo è la policy di default.
    In caso di conflitto di segnali, vince sempre la decisione più conservativa.

5.  AI enrichment è opzionale, mai bloccante.
    Se Claude API non risponde, il sistema produce sequenza e decisione senza spiegazione.

6.  Nessuna dipendenza superflua.
    Prima di aggiungere un package, verificare che stdlib o dipendenze esistenti
    non coprano già il caso d'uso.

7.  Zero biforcazioni smf_core ↔ backend.
    Il modulo edge deve poter girare su un laptop senza Railway attivo.
```

---

*Blueprint generato: 2026-04-15*
*Basato su codebase PROMETEO v0.3.1*
*Branch: claude/prometeo-infra-blueprint-g7CU4*
