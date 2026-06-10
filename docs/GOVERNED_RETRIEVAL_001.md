# GOVERNED_RETRIEVAL_001

## Scopo

Questa capability introduce il primo contratto minimo di retrieval governato per PROMETEO.

Il layer produce un evidence pack locale, read-only e auditabile.

Non modifica TL Chat, planner, database, SMF o dati reali.

## Posizione architetturale

Sequenza di riferimento: MAPPARE -> UNIFICARE -> RETRIEVAL -> CONFLICT DETECTION -> EVAL -> KNOWLEDGE GRAPH CODE.

Questa capability copre solo RETRIEVAL.

## File introdotti

- backend/app/atlas_engine/governed_retrieval.py
- backend/tests/test_governed_retrieval_contract.py

## Funzione principale

build_governed_retrieval_pack(question: str, article: str | None = None, limit: int = 5)

## Contratto evidence item

Ogni evidence item deve contenere:

- source_id
- source_type
- authority_rank
- confidence
- text
- reason

## Vincoli dichiarati dal pack

- read-only
- local-only
- no LLM calls
- no DB writes
- no SMF writes
- no planner mutation
- no runtime mutation
- no specs_finitura image access

## Fonti ammesse nella prima versione

- tl_memory_rules
- docs/prometeo_system_map.md
- semantic_registry_confidence

## Fonti bloccate

- .env
- specs_finitura_images
- real_smf
- real_excel
- database_dumps
- secrets

## Cosa non fa

- non riscrive TL Chat
- non introduce vector DB
- non introduce Neo4j
- non crea UI
- non modifica il planner
- non chiama LLM
- non legge immagini o specifiche private

## Test contract

- blank question produce pack controllato
- domanda ZAW produce evidence governata
- ogni evidence item ha campi obbligatori
- il pack dichiara vincoli, fonti ammesse e fonti bloccate
- il modulo non importa il runtime TL Chat

## Stato

PASS locale:

- python3 -m py_compile backend/app/atlas_engine/governed_retrieval.py
- python3 -m pytest backend/tests/test_governed_retrieval_contract.py
- python3 -m pytest backend/tests/test_ai_context_retrieval_001.py

## Limiti residui

Il layer non e ancora collegato a TL Chat runtime.

Il layer non implementa conflict detection.

Il layer non sostituisce context_retrieval.py ma lo incapsula in un contratto piu governato.
