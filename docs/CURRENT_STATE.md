# PROMETEO Current State

Lifecycle: `CANONICAL`

Fonte semantica: `docs/PROMETEO_MASTER.md`.

Questo documento descrive lo stato corrente verificabile del repository. Non autorizza da solo modifiche runtime e non incorpora SHA come autorità permanente.

## Stato sintetico

PROMETEO è un sistema assistivo governato e verificabile per acquisire, classificare, collegare, conservare e recuperare conoscenza operativa. Non è ancora un prodotto SaaS/MES completo.

## Chiuso

- backend FastAPI e runtime locale di base;
- TL Chat con retrieval governato, provenance e risposte prudenti;
- gestione esplicita di `CERTO`, `INFERITO`, `DA_VERIFICARE` e sorgenti mancanti;
- guard privacy, data leak e TL semantic eval;
- acquisizione PNG/JPEG con boundary OCR e parser specifica;
- adapter OCR runtime locale Tesseract, attivabile solo tramite configurazione esplicita;
- esposizione UI dell'acquisizione specifica e conferma umana separata;
- `TL_CHAT_UNIFIED_DATA_ACCESS_001 / VERTICAL_SLICE_001`: chiusa, testata e mergiata;
- `TL_CHAT_UNIFIED_DATA_ACCESS_001 / VERTICAL_SLICE_002`: chiusa, testata e mergiata per customer-demand read-only;
- registrazione metadata-only di `customer_demand_registry`;
- grant runtime separato, deny-by-default, limitato a `tl_chat_readonly_runtime`;
- reader customer-demand read-only con provenienza canonica;
- binding reader → Context Resolver → TL Chat;
- risposta TL Chat su articolo, quantità, data richiesta dal cliente e priorità cliente, senza trasformare la data in promessa produttiva;
- percorso deny che non invoca il reader e non apre la connessione database;
- nessuna scrittura database, eleggibilità planner o promozione automatica.

## Capability attiva

- `ACTIVE_CAPABILITY`: `TL_CHAT_UNIFIED_DATA_ACCESS_001`;
- `STATUS`: `ACTIVE`;
- `MODE`: `READ_ONLY_FIRST`;
- slice chiuse:
  - `VERTICAL_SLICE_001`: articolo + componenti/operazioni;
  - `VERTICAL_SLICE_002`: customer demand + data richiesta dal cliente;
- nessuna slice successiva è autorizzata automaticamente;
- per aprire un nuovo perimetro serve preflight e decisione umana esplicita.

## Contratto corrente della slice 002

Fonte runtime: `customer_demand_registry`.

Campi autorizzati, esattamente:

- `articolo`;
- `codice_articolo`;
- `quantita`;
- `data_spedizione`;
- `priorita_cliente`.

Semantica obbligatoria:

- `data_spedizione` è trattata come data richiesta dal cliente, non come promessa, scadenza interna o decisione di piano;
- confidence e stato semantico restano `DA_VERIFICARE`;
- conferma TL obbligatoria;
- `planner_eligible: false`;
- `automatic_promotion: false`;
- `DATABASE_WRITE: NONE`;
- policy runtime predefinita: `deny`.

## Evidenza slice 002

Catena consegnata tramite PR consecutive:

- #478 — perimetro runtime read-only;
- #479 — boundary database;
- #480–#481 — registrazione fonte;
- #482 — reader read-only;
- #483 — binding reader → Context Resolver;
- #484–#485 — mappa e autorizzazione implementativa;
- #486 — binding TL Chat customer-demand;
- #487 — supporto fonte database registry senza path filesystem;
- #488 — mappatura end-to-end;
- #489 — allineamento governance/runtime.

Commit di chiusura governance/runtime: `f5c39c3a0f317861cc0c32697a11f1044472096a`.

Verifica post-merge:

- percorso autorizzato: PASS;
- percorso deny: PASS;
- reader chiamato su deny: NO;
- connessione database su deny: NO;
- scritture: NONE;
- guard repository: verdi sulla PR di chiusura.

## Parziale

- la persistenza autorevole non copre tutte le destinazioni classificate;
- planner presente ma non validato su uno scenario turno completo;
- eventi e blocchi non sono chiusi come timeline prodotto completa;
- PWA non validata come workflow unico di reparto;
- audit backend non esposto come timeline TL completa;
- Pattern Learning non alimentato end-to-end dalla nuova catena intake;
- la capability unified data access non è chiusa integralmente: sono chiuse soltanto le slice esplicitamente elencate.

## Fuori fase

- multi-tenant e provisioning cliente;
- SaaS/MES readiness;
- autonomia decisionale produttiva;
- nuovi agenti o architetture parallele;
- cloud per dati industriali;
- nuove scritture o fonti runtime senza autorizzazione dedicata.

## Vincoli permanenti

- repository e contratti canonici prevalgono sulla conversazione;
- una capability alla volta;
- nessun accesso a path arbitrari;
- nessuna mutazione implicita;
- nessuna promozione automatica a `CERTO`;
- nessuna decisione autonoma di pianificazione;
- ogni nuova slice richiede scope, file ammessi, test, stop condition e decisione umana;
- ogni conteggio test deve dichiarare comando, suite, selected, deselected, total collected e stato `executed` o `collect-only`.

## Prossima autorizzazione

`NONE`.

Lo stato corrente non seleziona automaticamente la prossima fonte o capability. La prossima mossa deve essere determinata mediante `docs/development/PROMETEO_INTERACTION_PREFLIGHT.md`, verificando priorità, valore verticale minimo e assenza di scope creep.
