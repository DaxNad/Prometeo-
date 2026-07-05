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
- spec_intake_preview
- local_specs_metadata
- article_tl_summary
- lifecycle_registry
- article_route_matrix_preview
- codici_staging_preview
- tl_real_spec_intake

Le fonti runtime aggiunte dichiarano provenance di sorgenti locali gia
consumate dai responder TL Chat. Non introducono nuovi reader, nuove fonti
fisiche o nuove capability di lettura.

## Merge provenance runtime

Il pack mantiene il limite pubblico di 5 evidence item.

Policy di merge:

- se non esistono runtime evidence, il pack resta invariato;
- le evidence prodotte da build_governed_retrieval_pack mantengono l'ordine
  originale;
- la deduplicazione usa la coppia source_id/source_type;
- se il totale non supera il limite, le runtime evidence vengono aggiunte in
  coda;
- se il pack esistente occupa gia tutto il limite e sono presenti runtime
  evidence, le prime evidence esistenti restano nell'ordine originale e solo
  l'ultimo slot viene sostituito deterministicamente dalla prima runtime
  evidence.

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

Il layer e collegato a TL Chat runtime solo per completare la provenance
strutturata di fonti gia consumate dai responder.

Il layer non implementa conflict detection.

Il layer non sostituisce context_retrieval.py ma lo incapsula in un contratto piu governato.
