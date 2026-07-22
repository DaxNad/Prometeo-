# PRODUCTION_PROGRAM_OCR_CONFIRMED_READ_FLOW_CLOSURE_001

## Stato

- `STATUS`: `CHIUSA`
- `LIFECYCLE`: `ARCHIVED`
- `CATEGORY`: `EVIDENCE`
- `ESITO`: `CLOSED_END_TO_END_VERIFIED`
- `DATE`: `2026-07-22`

## Commit e PR

- commit di merge: `2ca30c2`;
- PR: `#536`;
- titolo: `feat: production program OCR confirmed read flow`.

Il commit `2ca30c2` chiude la verticale cumulativa dopo le integrazioni multipagina `74e1063` e `71c5dc2`.

## Obiettivo chiuso

La verticale rende verificabile il passaggio da immagini sintetiche del programma di produzione a uno snapshot confermato, versionato e rileggibile dalla TL Chat. La preview OCR resta non autorevole fino alla conferma umana esplicita; la conferma produce `CONFERMATO`, mai `CERTO`.

## Flusso verificato

```text
PNG/JPEG
→ OCR Tesseract locale
→ preview DA_VERIFICARE non persistita
→ parsing deterministico dei record osservati
→ conferma umana autorizzata
→ registry versionato CONFERMATO
→ read-back governato e non mutante
→ TL Chat per periodo confermato
```

## Contratti osservati

- acquisizione singola: `POST /production-program/image-ocr/acquire`;
- acquisizione multipagina: `POST /production-program/image-ocr/acquire-multipage`;
- conferma esplicita: `POST /production-program-snapshot/confirm`;
- interrogazione TL Chat: `POST /tl/chat`;
- preview: `semantic_status=DA_VERIFICARE`, `requires_confirmation=true`, `persisted=false`;
- conferma: attore, ruolo autorizzato, timestamp, nota audit, `source_id`, `source_hash`, testo osservato e preview coerente sono obbligatori;
- record persistito: `status=CONFERMATO`, `semantic_status=CONFERMATO`, `requires_confirmation=false`, `persisted=true`;
- registry: identità deterministica, versionamento, idempotenza sul contenuto invariato, storico preservato e scrittura atomica;
- reader: `read_latest` per `registry_id` e `read_latest_by_period` per periodo esplicito, limitati a snapshot confermati e persistiti;
- risposta TL Chat valida: `source=production_program_snapshot_registry`, `source_status=SOURCE_FOUND`, `semantic_status=CONFERMATO`, `confidence=CONFERMATO`;
- provenance: ogni campo osservato conserva il riferimento alla riga OCR di origine; il record conserva fonte, hash, attore, ruolo, timestamp, versione e audit.

## File runtime principali

- `backend/app/api/production_program_image_ocr_acquisition.py`;
- `backend/app/ingest/production_program_image_ocr_acquisition.py`;
- `backend/app/services/production_program_tesseract_ocr.py`;
- `backend/app/services/production_program_snapshot_preview.py`;
- `backend/app/api/production_program_snapshot_confirmation.py`;
- `backend/app/services/production_program_snapshot_confirmation.py`;
- `backend/app/domain/production_program_snapshot_registry.py`;
- `backend/app/api/tl_chat.py`;
- `frontend/src/pages/ProductionProgramImageOCRAcquisitionPage.tsx`.

## Test principali

- `backend/tests/test_production_program_tesseract_ocr.py`: adapter Tesseract locale, fail-closed, cleanup e assenza di rete;
- `backend/tests/test_production_program_image_ocr_acquisition.py`: acquisizione singola e handoff alla preview;
- `backend/tests/test_production_program_image_ocr_acquisition_endpoint.py`: contratto HTTP dell'acquisizione singola;
- `backend/tests/test_production_program_image_ocr_multipage_acquisition.py`: composizione ordinata multipagina;
- `backend/tests/test_production_program_image_ocr_multipage_acquisition_endpoint.py`: contratto HTTP multipagina;
- `backend/tests/test_production_program_snapshot_preview.py`: parsing deterministico di periodo, ordini, articoli, quantità, postazione e provenance;
- `backend/tests/test_production_program_snapshot_endpoint.py`: contratto della preview snapshot;
- `backend/tests/test_production_program_verified_snapshot_e2e.py`: conferma autorizzata, persistenza atomica, idempotenza, versionamento, read-back e TL Chat per periodo senza mutazione;
- `backend/tests/test_tl_chat_production_program_snapshot_binding.py`: binding TL Chat della preview esplicita e assenza di side effect;
- `frontend/src/pages/ProductionProgramImageOCRAcquisitionPage.test.tsx`: acquisizione, review, conferma esplicita, successo persistito ed errore di conferma.

## Criteri di accettazione raggiunti

- OCR locale osservato disponibile per PNG/JPEG;
- record strutturati estratti senza parser probabilistico;
- `period` valorizzato soltanto da `PERIODO` esplicito;
- `order_id` valorizzato soltanto da `ORDINE` esplicito;
- `missing_fields=[]` nello smoke completo;
- preview non persistita e ancora soggetta a conferma;
- conferma manuale con attore e ruolo autorizzato;
- versione `CONFERMATO` persistita con `registry_id` tracciabile;
- idempotenza della stessa conferma e nuova versione per contenuto modificato;
- read-back del registry non mutante;
- TL Chat restituisce lo snapshot confermato richiesto per periodo;
- `planner_called=false`, `writer_called=false`, `pattern_learning_called=false`;
- nessuna promozione a `CERTO` e nessun fallback inferito.

## Evidenze smoke

Lo smoke ha usato esclusivamente dati sintetici:

- file: `/tmp/prometeo-ocr-smoke/programmazione-produzione-completa-smoke.png`;
- periodo: `2026-W30`;
- ordine 1: `ORD-001`, articolo `12069`, quantità `24`, postazione `Banco assemblaggio`;
- ordine 2: `ORD-002`, articolo `12514`, quantità `12`, postazione `Banco assemblaggio`;
- attore: `TL_SMOKE`;
- ruolo: `RESPONSABILE_PRODUZIONE`;
- nota audit: `Smoke conferma snapshot OCR completo`;
- versione registry: `1`;
- domanda verificata: `Mostrami il programma produzione confermato 2026-W30`;
- fonte restituita: `production_program_snapshot_registry`;
- stato restituito: `CONFERMATO`.

Nessuna chiave API, segreto o dato industriale reale è incluso in questa evidenza.

## Limiti espliciti

La verticale non copre:

- pianificazione automatica;
- scrittura verso produzione o SMF;
- validazione di `customer_requested_date`;
- gestione delle priorità;
- deduplicazione semantica cross-periodo oltre le regole correnti;
- UI dedicata alla consultazione dello storico snapshot;
- gestione avanzata di più snapshot confermati per lo stesso periodo;
- dati reali di produzione diversi dallo smoke sintetico.

## Decisioni governate

- `Data spedizione` non equivale a `customer_requested_date`;
- `period` deriva solo da una riga `PERIODO` esplicita;
- `order_id` deriva solo da una riga `ORDINE` esplicita;
- la conferma umana produce `CONFERMATO`, non `CERTO`;
- TL Chat legge solo snapshot confermati, persistiti e non più soggetti a conferma;
- in assenza o ambiguità della fonte il sistema restituisce uno stato governato e non usa fallback inferiti;
- il read-back non attiva planner, writer o Pattern Learning.

## Esito

```text
CLOSED_END_TO_END_VERIFIED
```

## Prossima mossa

Capability futura proposta, non aperta né autorizzata da questa closure:

`PRODUCTION_PROGRAM_CONFIRMED_SNAPSHOT_HISTORY_UI_001` — mostrare in UI read-only gli snapshot confermati con periodo, versione, `registry_id`, audit e ordini, senza planner né mutazioni.
