# PROMETEO CONTEXT INIT

Sistema in sviluppo:
PROMETEO = AI Operating Environment per gestione produzione + orchestrazione workflow tecnici.

Architettura attuale:
MacBook Air M4 → nodo principale sviluppo locale

Stack:

AI orchestration
- ChatGPT desktop
- Codex agent CLI
- Atlas browser AI

Backend
- Python
- FastAPI
- SQLAlchemy
- PostgreSQL

Frontend
- React
- Vite
- Typescript

Pipeline dati
- SuperMegaFile (SMF)
- smf_update.py
- JSON rules PROMETEO

Deploy
- Railway
- GitHub

Obiettivo sistema:
unificare AI, sviluppo software, gestione dati produzione e automazione workflow
in un unico ambiente operativo coerente.

Vincoli architetturali:
- non distruggere repo esistente
- integrazione incrementale
- compatibilità con SMF Core
- compatibilità con local_smf
- stabilità prioritaria

Regole operative:
1. preservare struttura backend esistente
2. non sovrascrivere file esistenti senza verifica
3. mantenere compatibilità PostgreSQL
4. mantenere compatibilità smf_update.py
5. mantenere compatibilità futura PWA
6. essere eseguibile da Terminale Mac
7. essere replicabile su Railway

Modalità risposta richiesta:
- script completi
- file completi
- struttura cartelle completa
- istruzioni terminale passo-passo
- nessuna soluzione parziale

Priorità:
- continuità sviluppo PROMETEO
- stabilità SMF pipeline
- integrazione Codex agent coding
- preparazione PWA gestionale

Contesto operativo:
cartella principale:
~/PROMETEO

cartella dati locale:
~/PROMETEO/data/local_smf

script principale SMF:
smf_update.py

Regola aurea:
ogni proposta deve essere integrabile senza rompere il lavoro già funzionante.
