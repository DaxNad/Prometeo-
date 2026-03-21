# PROMETEO SYSTEM MAP v1.0

## 1. Visione generale

PROMETEO è una piattaforma modulare composta da backend operativo, frontend dashboard, persistenza dati, governance di sviluppo e layer AI.

L’obiettivo è trasformare il sistema in una piattaforma reale di monitoraggio e orchestrazione reparto.

---

## 2. Mappa moduli

```text
PROMETEO
│
├── BACKEND CORE
│   ├── FastAPI app
│   ├── API routers
│   ├── business rules
│   ├── repository layer
│   ├── schemas
│   └── config / db
│
├── EVENT ENGINE
│   ├── event model
│   ├── event service
│   ├── events endpoints
│   └── future persistence
│
├── SEARCH ENGINE
│   ├── search endpoint
│   ├── search logic
│   ├── JSON dataset loader
│   └── future DB search
│
├── FRONTEND
│   ├── dashboard web
│   ├── mobile / PWA layer
│   ├── KPI views
│   └── eventi aperti / storico
│
├── DATABASE LAYER
│   ├── PostgreSQL
│   ├── event persistence
│   ├── KPI source data
│   └── future operational records
│
├── DEVELOPMENT OS
│   ├── master control
│   ├── task board
│   ├── system log
│   ├── ADR decisions
│   └── AI protocols
│
└── AI LAYER
    ├── ATLAS Engine
    ├── supporto decisionale
    ├── spiegazione eventi
    └── analisi produzione
3. Backend Core

Percorso principale:

backend/app/

Componenti principali:

backend/app/
├── api/
├── data/
├── models/
├── services/
├── config.py
├── db.py
├── main.py
├── repository.py
├── rules.py
├── schemas.py
├── search.py
└── events.py

Funzione:

esporre API

coordinare logica applicativa

collegare servizi, modelli e persistenza

4. Event Engine

Componenti noti:

backend/app/events.py
backend/app/models/event.py
backend/app/services/event_service.py

Endpoint:

/events
/events?limit=100
/events?open_only=true

Funzione:

registrare eventi produzione

filtrare eventi aperti

preparare base per storico e KPI

Evoluzione prevista:

persistenza database

severità/priorità

assegnazione stato

cronologia completa

5. Search Engine

Componenti noti:

backend/app/api_search.py
backend/app/search.py
backend/app/data/

Endpoint:

/search?q=...

Funzione:

interrogare dataset locali

restituire risultati normalizzati

Stato attuale:

endpoint attivo

cartella dati ancora vuota o non popolata operativamente

risultati attuali limitati o nulli

Evoluzione prevista:

popolamento JSON reale

successiva migrazione a fonte database

6. Frontend / Dashboard

Percorsi presenti nel repository:

frontend/
ui/
mobile

Funzione:

visualizzare eventi aperti

mostrare KPI stazioni

offrire dashboard operativa

Stato attuale:

presente ma parziale

alcune chiamate API ancora da stabilizzare

asset PWA ancora incompleti

Evoluzione prevista:

dashboard stabile

route mobile reale

icone/manifest completi

PWA installabile

7. Database Layer

Tecnologia prevista:

PostgreSQL

Ruolo:

persistenza eventi

supporto ricerche

storico operativo

base dati per KPI reali

Stato attuale:

configurato a livello progetto

non ancora sorgente primaria del sistema

Obiettivo:

spostare PROMETEO da logica volatile / dataset statici a persistenza reale

8. Development OS

Documenti chiave:

board/master_control.md
board/task_board.md
board/system_log.md
docs/decisions/
ai/protocols/

Ruolo:

governance progetto

controllo avanzamento

storicizzazione decisioni

protocollo operativo sviluppo

Funzione architetturale:
il Development OS non è supporto accessorio; è il layer di coordinamento del progetto.

9. AI Layer — ATLAS

Modulo previsto per:

spiegazione eventi

supporto decisionale

correlazione anomalie

lettura contesto produzione

Ruolo futuro:
trasformare PROMETEO da semplice backend operativo a sistema assistito da logica AI.

10. Flusso logico del sistema
Operatore / Frontend
        ↓
   API FastAPI
        ↓
Servizi applicativi
        ↓
Event Engine / Search Engine / KPI logic
        ↓
Repository / Database
        ↓
Dashboard / AI / storico
11. Flusso di sviluppo
TASK
↓
DECISIONE
↓
CODICE
↓
TEST
↓
LOG
↓
DEPLOY

Questo flusso deve essere registrato nel Development OS.

12. Priorità architetturali correnti

stabilizzare search con dati reali

stabilizzare frontend dashboard

collegare PostgreSQL

completare registri Development OS

consolidare Event Engine

preparare integrazione AI

13. Stato del sistema
Backend API      = ATTIVO
Deploy Railway   = ATTIVO
Swagger          = ATTIVO
Event Engine     = ATTIVO
Search Engine    = ATTIVO MA VUOTO
Frontend         = PARZIALE
Database         = NON ANCORA OPERATIVO
AI Layer         = PREVISTO
Development OS   = IMPOSTATO, DA CONSOLIDARE
14. Ruolo del documento

Questo file rappresenta la mappa architetturale ufficiale di PROMETEO.

Serve per:

onboarding rapido

continuità tra sessioni AI

controllo struttura progetto

prevenzione deriva architetturale
