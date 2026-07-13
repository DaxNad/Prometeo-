# PROMETEO Current State

Lifecycle: `CANONICAL`

Fonte semantica: `docs/PROMETEO_MASTER.md`.

Verificato contro il `main` usato come base della modifica documentale il
2026-07-13. Lo stato va riconfermato tramite codice e test a ogni aggiornamento,
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
- conferma umana autorevole dalla UI tramite endpoint governato separato,
  senza promozione automatica dei dati OCR e con assunzione esplicita
  dell'autorità operativa;
- gestione UI degli esiti di persistenza positivi, dei fallimenti governati
  e degli errori di trasporto senza dichiarare persistenza inesistente;
- `VERTICAL_SLICE_001` della capability
  `TL_CHAT_UNIFIED_DATA_ACCESS_001`: `CLOSED` / `TESTED` / `MERGED`;
- `VERTICAL_SLICE_002` della capability
  `TL_CHAT_UNIFIED_DATA_ACCESS_001`: `CLOSED` / `TESTED` / `MERGED`;
- `VERTICAL_SLICE_003` della capability
  `TL_CHAT_UNIFIED_DATA_ACCESS_001`: `CLOSED` / `TESTED` / `MERGED`;
- `VERTICAL_SLICE_004` della capability
  `TL_CHAT_UNIFIED_DATA_ACCESS_001`: `CLOSED` / `TESTED` / `MERGED`;
- capability `TL_CHAT_UNIFIED_DATA_ACCESS_001`: `CLOSED` / `TESTED` / `MERGED`;
- customer-demand registry registrato metadata-only con grant runtime separato,
  read-only e deny-by-default;
- reader customer-demand, binding Context Resolver e risposta TL Chat limitata
  ai cinque campi autorizzati;
- percorso deny verificato senza invocazione reader, connessione database o
  scrittura;
- rilevazione deterministica dei conflitti tra fonti già autorizzate, con
  `SOURCE_AMBIGUOUS`, `DA_VERIFICARE`, conferma TL obbligatoria e nessuna
  riconciliazione automatica;
- percorso `/tl/chat` multi-fonte con conflict readback strutturato end-to-end;
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

## Capability chiusa

- `CAPABILITY`: `TL_CHAT_UNIFIED_DATA_ACCESS_001`;
- `STATUS`: `CLOSED` / `TESTED` / `MERGED`;
- `MODE`: `READ_ONLY_FIRST`;
- stato slice:
  - `VERTICAL_SLICE_001`: chiusa, testata e mergiata;
  - `VERTICAL_SLICE_002`: chiusa, testata e mergiata;
  - `VERTICAL_SLICE_003`: chiusa, testata e mergiata;
  - `VERTICAL_SLICE_004`: chiusa, testata e mergiata;
- scope consegnato da `VERTICAL_SLICE_001`:
  - risposta TL Chat su articolo;
  - risposta TL Chat su componenti e operazioni;
  - mantenimento di `source`, `status` e `confidence`;
- scope consegnato da `VERTICAL_SLICE_002`:
  - intent ordini e date di spedizione;
  - source `customer_demand_registry`;
  - autorizzazione runtime separata dall'indice metadata-only;
  - reader e binding read-only;
  - risposta TL Chat su `articolo`, `codice_articolo`, `quantita`,
    `data_spedizione`, `priorita_cliente`;
  - `data_spedizione` resa come data richiesta dal cliente e non come promessa,
    deadline interna o decisione di piano;
  - `DA_VERIFICARE`, conferma TL richiesta, planner e promozione automatica
    disabilitati;
- scope consegnato da `VERTICAL_SLICE_003`:
  - confronto deterministico dei campi operativi sovrapposti tra fonti già
    autorizzate;
  - esclusione dei metadata di provenance e governance dal confronto;
  - dichiarazione strutturale di campi, fonti e valori conflittuali;
  - esito `SOURCE_AMBIGUOUS` con `DA_VERIFICARE`;
  - conferma TL obbligatoria;
  - `planner_eligible=false` e `can_promote=false`;
  - priorità delle fonti invariata quando non esiste conflitto;
  - nessuna riconciliazione automatica;
- scope consegnato da `VERTICAL_SLICE_004`:
  - un percorso `/tl/chat` usa due fonti già autorizzate;
  - confronto limitato a `codice`, `disegno` e `rev`;
  - conflict readback strutturato con campo, fonti e valori grezzi;
  - valori equivalenti preservano il comportamento precedente;
  - conflitto esposto come `SOURCE_AMBIGUOUS` / `DA_VERIFICARE`;
  - conferma TL obbligatoria e nessuna promozione o eligibility planner;
  - nessuna modifica al resolver o alla priorità delle fonti;
  - nessuna scrittura;
- criteri di chiusura capability soddisfatti:
  - accesso TL Chat a più fonti autorizzate;
  - source, status e confidence preservati;
  - conflitti e dati mancanti dichiarati;
  - `PREVIEW_ONLY` non promosso;
  - assenza di scritture;
  - copertura di fonte presente, mancante, vietata, ambigua e conflittuale;
- nessuna slice successiva è autorizzata;
- nessuna nuova capability è autorizzata automaticamente da questa chiusura;
- vincoli permanenti:
  - read-only;
  - solo fonti autorizzate;
  - nessun accesso a path arbitrari;
  - nessuna mutazione dati;
  - nessuna promozione automatica a `CERTO`;
  - nessuna decisione autonoma di pianificazione;
  - nessuna nuova UI;
  - nessun nuovo OCR;
  - nessun agente autonomo;
  - nessun cloud per dati industriali.

## Fuori fase

- multi-tenant e provisioning cliente;
- SaaS/MES readiness;
- autonomia decisionale produttiva;
- nuovi agenti o architetture parallele.

## Chiusura slice documentale

### VERTICAL_SLICE_001

`VERTICAL_SLICE_001` registra la chiusura documentale della parte consegnata
della capability `TL_CHAT_UNIFIED_DATA_ACCESS_001`.

- `SLICE_STATUS`: `CLOSED` / `TESTED` / `MERGED`;
- `PR`: `#474`;
- `MERGE_SHA`: `aba083c9e1345bfc8c593d2e23062fc382a3a394`;
- `TEST_EVIDENCE`: `85 passed` con `TMPDIR=/tmp/prometeo_pytest_tmp`;
- `RUNTIME_CHANGED`: `backend/app/api/tl_chat.py`;
- `TESTS_CHANGED`: `backend/tests/test_tl_chat_unified_data_access.py`;
- scope consegnato: articolo + componenti/operazioni con `source`, `status`
  e `confidence`;
- anti-scope-creep:
  - nessuna promozione automatica a `CERTO`;
  - nessuna decisione autonoma di planning;
  - nessuna chiusura totale della capability.

### VERTICAL_SLICE_002

`VERTICAL_SLICE_002` registra la chiusura della parte customer-demand read-only.

- `SLICE_STATUS`: `CLOSED` / `TESTED` / `MERGED`;
- catena di consegna: PR `#478`–`#489`;
- chiusura governance/runtime: PR `#489`;
- `MERGE_SHA`: `f5c39c3a0f317861cc0c32697a11f1044472096a`;
- `SOURCE_ID`: `customer_demand_registry`;
- `RUNTIME_BINDING`: `TL_CHAT_READ_ONLY`;
- `DEFAULT_POLICY`: `DENY`;
- `DATABASE_WRITE`: `NONE`;
- `PLANNER_ELIGIBLE`: `false`;
- `AUTOMATIC_PROMOTION`: `false`;
- percorso autorizzato: verificato;
- percorso deny: verificato;
- reader invocato su deny: no;
- database connection su deny: no;
- documenti di evidenza:
  - `docs/capabilities/TL_CHAT_UNIFIED_DATA_ACCESS_VERTICAL_SLICE_002.md`;
  - `docs/capabilities/CUSTOMER_DEMAND_GOVERNANCE_RUNTIME_ALIGNMENT_001.md`;
- anti-scope-creep:
  - nessun importer o SMF;
  - nessun planner o board state;
  - nessuna attivazione di altre fonti;
  - nessun accesso tramite generic filesystem reader;
  - nessuna nuova slice autorizzata.

### VERTICAL_SLICE_003

`VERTICAL_SLICE_003` registra la chiusura del conflict handling read-only tra
fonti già autorizzate.

- `SLICE_STATUS`: `CLOSED` / `TESTED` / `MERGED`;
- `PR`: `#494`;
- `MERGE_SHA`: `cbfa4793e2c914e2f75fab5fdc43a6ad1cbf8b8b`;
- `RUNTIME_CHANGED`: `backend/app/services/tl_chat_context_resolver.py`;
- `TESTS_ADDED`: `backend/tests/test_tl_chat_context_resolver_conflicts.py`;
- `SOURCE_PRIORITY_CHANGED`: `false`;
- `DATABASE_WRITE`: `NONE`;
- `PLANNER_ELIGIBLE_ON_CONFLICT`: `false`;
- `AUTOMATIC_PROMOTION_ON_CONFLICT`: `false`;
- `REQUIRES_TL_CONFIRMATION_ON_CONFLICT`: `true`;
- conflict status: `SOURCE_AMBIGUOUS`;
- conflict confidence: `DA_VERIFICARE`;
- sei workflow repository PASS;
- anti-scope-creep:
  - nessuna nuova fonte o campo;
  - nessuna modifica API;
  - nessuna riconciliazione automatica;
  - nessun planner, importer, SMF, UI, OCR, agente o cloud;
  - nessuna nuova slice autorizzata.

### VERTICAL_SLICE_004

`VERTICAL_SLICE_004` registra la chiusura del percorso TL Chat multi-fonte e del
conflict readback strutturato end-to-end.

- `SLICE_STATUS`: `CLOSED` / `TESTED` / `MERGED`;
- `PR`: `#497`;
- `MERGE_SHA`: `a397b1df92886f23b70561379fca89eef242d562`;
- `RUNTIME_CHANGED`: `backend/app/api/tl_chat.py`;
- `TESTS_ADDED`: `backend/tests/test_tl_chat_multisource_conflict_endpoint.py`;
- `RESOLVER_CHANGED`: `false`;
- `SOURCE_PRIORITY_CHANGED`: `false`;
- `NEW_SOURCE_REGISTERED`: `false`;
- `DATABASE_WRITE`: `NONE`;
- `PLANNER_ELIGIBLE_ON_CONFLICT`: `false`;
- `AUTOMATIC_PROMOTION_ON_CONFLICT`: `false`;
- `REQUIRES_TL_CONFIRMATION_ON_CONFLICT`: `true`;
- test mirati locali: `9 passed`;
- sei workflow repository PASS;
- anti-scope-creep:
  - nessuna nuova fonte o campo;
  - nessuna riconciliazione automatica;
  - nessun planner, importer, SMF, UI, OCR, agente o cloud;
  - nessuna slice successiva autorizzata.

## Verdetto finale capability

`TL_CHAT_UNIFIED_DATA_ACCESS_001` è `CLOSED` / `TESTED` / `MERGED`.

La chiusura è supportata dalle quattro slice consegnate e dai criteri del
contratto canonico. Non resta un gap runtime interno al perimetro autorizzato.

## Prove correnti

I seguenti `PASS` derivano da esecuzioni registrate nelle rispettive closure o
CI; non sono risultati delle raccolte `collect-only` riportate più sotto:

- `VERTICAL_SLICE_001` / PR #474: 85 test PASS con
  `TMPDIR=/tmp/prometeo_pytest_tmp`;
- `VERTICAL_SLICE_002` / PR #489: test dedicati e sei workflow repository PASS;
- verifica post-merge slice 002: authorized path PASS, deny path PASS, reader
  non chiamato su deny, nessuna scrittura;
- `VERTICAL_SLICE_003` / PR #494: test dedicati e sei workflow repository PASS;
- conflict handling slice 003: valori equivalenti senza falso conflitto,
  conflitto singolo e multiplo, preview coinvolta e metadata di provenance
  esclusi dal confronto;
- `VERTICAL_SLICE_004` / PR #497: 9 test mirati locali e sei workflow repository PASS;
- endpoint multi-fonte slice 004: valori equivalenti senza falso conflitto,
  `SOURCE_AMBIGUOUS`, `DA_VERIFICARE`, readback strutturato e nessuna scrittura;
- `make goal-complete-v1`: PASS;
- TL Chat contract: 67 test PASS;
- TL semantic eval: PASS;
- Privacy Guard: PASS;
- Data Leak Guard: PASS;
- acquisizione specifica + binding + endpoint + OCR Tesseract: 27 test PASS;
- UI acquisizione e conferma specifica: 6 test mirati PASS;
- suite frontend: 8 test PASS;
- build TypeScript/Vite: PASS;
- CI PR #469: 6 workflow PASS;
- real code registry preview: 30 test PASS;
- quality gate: PASS;
- schema guard: PASS.

### Perimetri di raccolta test verificati

Verifica `collect-only` eseguita il 2026-07-11 sul commit
`d00e9ea77f109705c908841cfffb65d457cd065e`:

- backend guard canonico:
  - perimetro effettivo del guard: `backend/tests`, come dichiarato da
    `scripts/goal_guard.sh`;
  - comando di verifica:
    `./tools/py -m pytest --collect-only -q -s -p no:cacheprovider backend/tests`;
  - selected: `1099`;
  - deselected: `3`, per il marker configurato `not e2e`;
  - total collected: `1102`;
  - stato: `collect-only`, quindi nessun `PASS` di esecuzione dichiarato;
- test ATLAS:
  - suite: `backend/app/atlas_engine/tests`;
  - comando di verifica:
    `./tools/py -m pytest --collect-only -q -s -p no:cacheprovider backend/app/atlas_engine/tests`;
  - selected: `48`;
  - deselected: `0`;
  - total collected: `48`;
  - stato: `collect-only`; esecuzione non verificata in questa rilevazione;
  - la suite è esterna al perimetro del backend guard canonico;
- aggregazione esplicita `backend standard + ATLAS`:
  - comando di verifica:
    `./tools/py -m pytest --collect-only -q -s -p no:cacheprovider backend/tests backend/app/atlas_engine/tests`;
  - selected: `1147`;
  - deselected: `3`;
  - total collected: `1150`;
  - stato: aggregazione di raccolte `collect-only` separate;
  - non rappresenta il risultato del solo backend guard e non prova che le due
    suite siano state eseguite.

### Riclassificazione del claim storico `1141`

Il precedente claim `1141 PASS, 3 deselected`, introdotto nel commit
`373ebbdc`, resta tracciato come dato storico, ma il suo perimetro di reporting
non coincide con il backend guard canonico attuale. La ricostruzione numerica
verificabile è:

- `1093 backend storici + 48 ATLAS = 1141`;
- `1093 backend storici + 6 nuovi backend = 1099` correnti;
- delta netto: `48 ATLAS esclusi - 6 backend aggiunti = 42`.

Il log grezzo originale non è disponibile: non è possibile stabilire se ATLAS
fosse stato passato nello stesso comando Pytest oppure sommato successivamente
nel report. Non risultano test mancanti, cancellati o rinominati numericamente
inspiegati. La PR #471 ha modificato soltanto il metodo di sessione portabile e
non ha modificato test o configurazione Pytest.

### Regola permanente di reporting test

Ogni conteggio deve dichiarare: comando, percorso o suite, selected,
deselected, total collected, stato `executed` oppure `collect-only`, commit,
marker o esclusioni rilevanti ed eventuale aggregazione tra suite. È vietato
attribuire a un guard un conteggio che include suite esterne al suo perimetro,
usare `PASS` per una raccolta `collect-only` o presentare un totale aggregato
senza identificarlo esplicitamente come aggregazione.

## Prossima autorizzazione

`NONE`.

Questa pagina descrive stato e gap. Non autorizza modifiche operative, una slice
successiva, una nuova fonte o una nuova capability e non sostituisce specifica
reale, conferma umana o contratti di capability.