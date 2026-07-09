# STRUCTURED_INTAKE_ORCHESTRATION_FACADE_CONTRACT_001

## Scopo

Comporre, per un singolo payload strutturato, la catena:

`payload → build_intake_item → orchestrate_intake_item`

senza introdurre API, TL Chat, batch o nuovi writer.

## Ingresso

- un solo payload mapping;
- ruolo richiedente opzionale.

## Sequenza vincolante

1. `build_intake_item(payload)`
2. se l’adapter rifiuta il payload:
   - non chiamare l’orchestratore;
   - restituire `REJECTED`;
   - preservare `error_code`.
3. se l’adapter costruisce l’item:
   - chiamare `orchestrate_intake_item(...)` una sola volta;
   - propagare risultato, `source_id`, `writer_called` ed `error_code`.

## Stati

- `ORCHESTRATED`
- `NOT_EXECUTED`
- `ORCHESTRATION_FAILED`
- `REJECTED`

## Risultato

Il risultato tipizzato deve preservare separatamente:

- risultato adapter;
- risultato orchestratore, se presente;
- stato facade;
- `writer_called`;
- `source_id`;
- `error_code`.

## Regole di sicurezza

- nessun batch;
- nessun retry;
- nessun dynamic dispatch;
- nessun accesso a file;
- nessuna rete;
- nessuna API;
- nessun frontend;
- nessun collegamento TL Chat;
- nessun writer diretto;
- nessun hardcode articolo;
- una sola chiamata all’adapter;
- una sola chiamata all’orchestratore.

## Scope autorizzato

Il facade non amplia le destinazioni eseguibili.

L’unico percorso persistente resta quello già governato da:

`HUMAN_CONFIRMATIONS`
→ `operational_class`
→ dry-run `READY`
→ execution bridge
→ `confirm_article_operational_status`

## Test minimi

- payload valido: adapter costruisce item e orchestratore chiamato una volta;
- payload rifiutato: orchestratore non chiamato;
- errore adapter preservato;
- mancata esecuzione orchestratore preservata;
- failure del writer distinto da `NOT_EXECUTED` e preservato con `writer_called=True`;
- assenza di batch, retry, I/O e dynamic dispatch;
- assenza di hardcode articolo.
