# TL CHAT PRACTICAL QUERY SET 001

Stato: `TL_CHAT_PRACTICAL_QUERY_SET_001`

Set minimo di domande operative per verificare la TL Chat PROMETEO dopo ogni avvio runtime.

## Scopo

Verificare che la TL Chat sia realmente utilizzabile da interfaccia PWA, non solo tecnicamente raggiungibile.

Questa verifica non introduce nuova architettura, non scrive dati e non modifica SMF/database/planner.

## Prerequisiti

- backend locale attivo
- frontend locale attivo
- PostgreSQL raggiungibile
- pagina `http://localhost:5173/tl-chat` aperta
- runtime coerente con `APP_RUNTIME_CLOSURE_001`

## Query operative minime

### Q1 — Articolo certo

Domanda:

- `12066?`

Esito atteso:

- risposta presente
- confidence `CERTO`
- route leggibile
- ZAW1 confermata
- ZAW2 esclusa come alternativa automatica
- CP finale obbligatorio
- conferma TL non richiesta

### Q2 — Articolo inferito / non certo

Domanda:

- `12070?`

Esito atteso:

- risposta presente
- confidence non `CERTO` se il profilo non è chiuso
- conferma TL richiesta se il dato è inferito
- nessuna promozione automatica a certezza

### Q3 — Codici da verificare

Domanda:

- `Quali codici sono da verificare?`

Esito atteso:

- risposta sintetica
- nessun dettaglio tecnico superfluo
- nessuna scrittura dati

### Q4 — Codici densificabili

Domanda:

- `Quali codici posso densificare?`

Esito atteso:

- elenco o indicazione operativa utile
- nessuna promozione automatica a planner
- nessuna apertura di nuova architettura

### Q5 — Fuori produzione

Domanda:

- `Quali codici sono fuori produzione?`

Esito atteso:

- risposta consultiva
- nessun inserimento automatico in priorità produttiva

### Q6 — New entry

Domanda:

- `Quali codici sono new entry?`

Esito atteso:

- risposta sintetica
- codici trattati come consultabili, non automaticamente pianificabili

### Q7 — Caso da verificare

Domanda:

- `Il 12402 è da verificare?`

Esito atteso:

- risposta prudente
- nessuna produzione automatica
- eventuale stato reference-only/fuori produzione rispettato se presente nei dati

## Criteri PASS

La verifica pratica passa se:

- la pagina TL Chat risponde senza errore
- almeno Q1 restituisce risposta `CERTO` corretta
- almeno una query non certa richiede prudenza/conferma
- non compaiono errori `unauthorized`
- non compaiono errori `404`
- non compaiono dettagli tecnici inutili per uso operativo
- non vengono prodotte priorità autonome non richieste

## Criteri FAIL

La verifica fallisce se:

- TL Chat non risponde
- compare `unauthorized`
- compare `404`
- la Dashboard o TL Chat puntano a sorgente remota durante runtime locale
- un codice inferito viene promosso a `CERTO` senza base verificata
- una risposta suggerisce produzione automatica senza ordine/richiesta esplicita

## Collegamenti GOAL

- `APP_RUNTIME_CLOSURE_001`
- `RUNTIME_OPERATION_GUIDE_001`
- `GOAL_CLOSURE_BASELINE_001`

## Stato finale

`TL_CHAT_PRACTICAL_QUERY_SET_001` è valido quando le query minime confermano che PROMETEO risponde in modo operativo, prudente e coerente con i guard rail GOAL_CLOSURE.
