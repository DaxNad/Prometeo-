# PROMETEO CONTEXT SNAPSHOT v1.0

## 1. Ruolo del documento

Questo file serve come snapshot operativo rapido del progetto PROMETEO.

Obiettivo:
consentire a una nuova sessione AI o a una nuova fase di sviluppo di ripartire immediatamente senza perdita di contesto.

Non sostituisce:
- il Boot Protocol
- la System Map
- i registri del Development OS

Li completa con una fotografia sintetica dello stato reale.

---

## 2. Identità del sistema

**PROMETEO** è una piattaforma di orchestrazione e monitoraggio per reparti produttivi.

Visione:
costruire una piattaforma reale, API-driven, con dashboard operative, gestione eventi, ricerca dati, persistenza e supporto AI.

---

## 3. Stato sintetico corrente

### Backend
- FastAPI attivo
- deploy su Railway operativo
- Swagger disponibile
- Event Engine presente
- Search Engine presente

### Frontend
- presente ma ancora parziale
- dashboard esistente
- alcune chiamate API ancora da stabilizzare

### Database
- PostgreSQL previsto/configurato
- non ancora collegato come sorgente reale primaria

### Development OS
- struttura definita
- registri da completare e consolidare

### AI Layer
- previsto come evoluzione ATLAS
- non ancora integrato operativamente nel flusso runtime

---

## 4. Base URL produzione

```text
https://prometeo-railway-bootstrap-production.up.railway.app
5. Endpoint attivi conosciuti
Sistema
/health
/ping
/docs
Development OS
/dev/status
/dev/tasks
/dev/logs
/dev/milestones
Event Engine
/events
/events?limit=100
/events?open_only=true
Search Engine
/search?q=...
6. Stato moduli
Event Engine

Presente e interrogabile via endpoint.

Componenti noti:

backend/app/events.py
backend/app/models/event.py
backend/app/services/event_service.py

Stato:

attivo

base valida

da evolvere verso persistenza, severità, priorità, storico e filtri avanzati

Search Engine

Presente e raggiungibile.

Componenti noti:

backend/app/api_search.py
backend/app/search.py
backend/app/data/

Stato:

endpoint attivo

logica presente

dataset locali ancora non popolati in modo utile

risultati attuali nulli o limitati

Frontend / Dashboard

Percorsi presenti:

frontend/
ui/
mobile

Stato:

base presente

non ancora stabile in tutte le chiamate API

da consolidare per uso operativo reale

Database Layer

Tecnologia prevista:

PostgreSQL

Stato:

predisposto a livello architetturale

non ancora connesso al ciclo operativo principale

7. Struttura backend rilevante
backend/app/
├── api/
├── data/
├── models/
├── services/
├── __init__.py
├── api_legacy.py
├── api_search.py
├── config.py
├── db.py
├── events.py
├── main.py
├── prometeo_client.py
├── repository.py
├── rules.py
├── schemas.py
├── search.py
└── services_legacy.py
8. Registri Development OS previsti
board/master_control.md
board/task_board.md
board/system_log.md
docs/decisions/
ai/protocols/

Funzione:

controllo sviluppo

task tracking

log tecnico

decisioni architetturali

protocolli AI

9. Regole operative permanenti

lavorare dal repository locale come sorgente unica di modifica

evitare modifiche via GitHub web durante sviluppo attivo

usare GitHub principalmente per lettura, storico e controllo deploy

mantenere coerenza architetturale tra backend, frontend, database e Development OS

quando si corregge codice, fornire blocchi completi sostitutivi

documentare i passaggi strutturali in file ufficiali di progetto

10. Problemi aperti principali

Search Engine formalmente attivo ma senza dataset operativo reale

Frontend ancora non del tutto stabile

PostgreSQL non ancora sorgente primaria dati

Registri Development OS da completare

Event Engine da evolvere verso persistenza e storico

11. Priorità correnti

popolare backend/app/data/ per rendere utile il Search Engine

stabilizzare dashboard frontend

collegare PostgreSQL al flusso reale

consolidare i registri del Development OS

evolvere Event Engine

preparare integrazione AI/ATLAS

12. Modalità di utilizzo nelle nuove chat

All’inizio di una nuova sessione, usare questo blocco:

PROMETEO CORE — CONTEXT INIT

Backend FastAPI deployato su Railway.
Development OS attivo.
Event Engine e Search Engine presenti.
Serve proseguire sviluppo architettura PROMETEO.

Per una ripresa più completa, usare anche questo snapshot come riferimento.

13. Distinzione tra i tre documenti
prometeo_boot_protocol.md

Definisce identità, stack, endpoint, regole e obiettivo del sistema.

prometeo_system_map.md

Mostra la mappa architetturale completa dei moduli.

prometeo_context_snapshot.md

Fornisce lo stato operativo sintetico e aggiornabile del progetto.

14. Stato del documento

Versione attuale: v1.0
Ruolo: snapshot operativo ufficiale di continuità per PROMETEO.
