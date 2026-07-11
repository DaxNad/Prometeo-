# PROMETEO Current State

Lifecycle: `CANONICAL`

Fonte semantica: `docs/PROMETEO_MASTER.md`.

Verificato contro il `main` usato come base della modifica documentale il
2026-07-11. Lo stato va riconfermato tramite codice e test a ogni aggiornamento,
senza affidarsi a uno SHA incorporato nel documento.

## Stato sintetico

PROMETEO è un sistema interno assistivo avanzato, governato e verificabile.
Non è ancora un prodotto SaaS/MES completo.

## Chiuso

- backend FastAPI e runtime locale di base;
- TL Chat con retrieval governato, provenance e risposte prudenti;
- gestione esplicita di `CERTO`, `INFERITO`, `DA_VERIFICARE` e sorgenti mancanti;
- guard privacy/data leak e TL semantic eval;
- classificazione intake, placement dry-run e orchestrazione strutturata;
- rilevazione delle discrepanze negli input intake strutturati;
- persistenza governata della conferma operativa articolo;
- acquisizione PNG/JPEG con boundary OCR e parser specifica;
- binding governato acquisizione specifica → facade intake, mantenuto
  `DA_VERIFICARE` e senza persistenza;
- esposizione governata del binding tramite `POST /article-specification/acquire`,
  con input Base64, review obbligatoria e comportamento fail-closed;
- adapter OCR runtime locale Tesseract, attivabile solo tramite configurazione
  esplicita, con timeout, rimozione dei file temporanei e nessun servizio cloud;
- esposizione UI operativa dell'acquisizione specifica tramite route dedicata,
  riuso del client API esistente e visualizzazione review-only degli esiti;
- target `make setup`, `make run` e `make doctor` presenti.

## Parziale

- la persistenza autorevole copre la conferma stato articolo, non tutte le
  destinazioni classificate;
- planner presente ma non validato su uno scenario turno completo;
- eventi e blocchi non sono chiusi come timeline prodotto completa;
- PWA disponibile ma non validata come workflow unico di reparto;
- audit backend non ancora esposto come timeline TL completa;
- Pattern Learning presente ma non alimentato end-to-end dalla nuova catena
  intake.

## Aperto

- conferma umana prima di qualsiasi persistenza autorevole dei dati estratti.

## Fuori fase

- multi-tenant e provisioning cliente;
- SaaS/MES readiness;
- autonomia decisionale produttiva;
- nuovi agenti o architetture parallele.

## Prove correnti

- `make goal-complete-v1`: PASS;
- TL Chat contract: 67 test PASS;
- TL semantic eval: PASS;
- Privacy Guard: PASS;
- Data Leak Guard: PASS;
- acquisizione specifica + binding + endpoint + OCR Tesseract: 27 test PASS;
- UI acquisizione specifica: 5 test frontend PASS e build PASS;
- backend guard: 1141 test PASS, 3 deselected;
- real code registry preview: 30 test PASS;
- quality gate: PASS;
- schema guard: PASS.

Questa pagina descrive stato e gap. Non autorizza modifiche operative né
sostituisce specifica reale, conferma umana o contratti di capability.
