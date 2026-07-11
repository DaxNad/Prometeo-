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
- conferma umana autorevole dalla UI tramite endpoint governato separato,
  senza promozione automatica dei dati OCR e con assunzione esplicita
  dell'autorità operativa;
- gestione UI degli esiti di persistenza positivi, dei fallimenti governati
  e degli errori di trasporto senza dichiarare persistenza inesistente;
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

- nessuna capability successiva autorizzata in questo documento;
- la prossima capability deve essere selezionata dopo nuova verifica del
  repository, dei test e delle priorità di prodotto.

## Fuori fase

- multi-tenant e provisioning cliente;
- SaaS/MES readiness;
- autonomia decisionale produttiva;
- nuovi agenti o architetture parallele.

## Prove correnti

I seguenti `PASS` derivano da esecuzioni registrate nelle rispettive closure o
CI; non sono risultati delle raccolte `collect-only` riportate più sotto:

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

Questa pagina descrive stato e gap. Non autorizza modifiche operative né
sostituisce specifica reale, conferma umana o contratti di capability.
