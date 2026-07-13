# CUSTOMER_DEMAND_READONLY_READER_001

## Stato

- `CAPABILITY_STATUS`: `IMPLEMENTED_FOR_REVIEW`
- `SOURCE_ID`: `customer_demand_registry`
- `ACCESS_MODE`: `READ_ONLY`
- `RUNTIME_BINDING`: `UNBOUND`
- `TL_CHAT_BINDING`: `OUT_OF_SCOPE`

## Obiettivo unico

Implementare un reader minimo e testabile per interrogazioni esatte su `customer_demand` tramite `articolo` oppure `codice_articolo`.

## File autorizzati

- `backend/app/services/customer_demand_readonly_reader.py`
- `backend/tests/test_customer_demand_readonly_reader.py`
- `docs/capabilities/CUSTOMER_DEMAND_READONLY_READER_001.md`

## Contratto

Il reader:

- usa esclusivamente la connessione applicativa esistente;
- non accetta path, URI, nomi tabella, colonne o SQL dall'utente;
- esegue una sola query `SELECT` costante e parametrizzata;
- limita i risultati a massimo 100 righe;
- restituisce soltanto `articolo`, `codice_articolo`, `quantita`, `data_spedizione`, `priorita_cliente`;
- mantiene `freshness: UNKNOWN` e `semantic_status: DA_VERIFICARE`;
- non esegue `commit`;
- chiude il cursore, effettua rollback difensivo e chiude la connessione;
- non è collegato a resolver o TL Chat.

Un lookup valido senza record restituisce:

```text
source_status: SOURCE_FOUND
records: []
missing_data: record_customer_demand_not_found
```

## Prova di non mutazione

I test verificano:

- una sola istruzione eseguita;
- istruzione iniziante con `SELECT`;
- tabella unica `customer_demand`;
- assenza di keyword mutanti;
- parametri separati dal testo SQL;
- zero chiamate a `commit`;
- dati di input invariati;
- sessione richiesta in modalità read-only quando supportata;
- rifiuto degli input invalidi prima dell'apertura della connessione.

## Fuori scope

- modifica del source index;
- attivazione runtime nel resolver;
- binding TL Chat;
- endpoint API;
- frontend;
- importer o SMF;
- planner, ordini, board state e viste ZAW;
- scritture o migrazioni database.

## Criterio di accettazione

La capability è chiusa quando il diff resta nei tre file autorizzati, i test dimostrano il comportamento read-only e nessun binding runtime viene introdotto.

## NEXT_MOVE

Dopo review e merge, aprire separatamente il binding del reader al resolver. Non aprire automaticamente il binding TL Chat.
