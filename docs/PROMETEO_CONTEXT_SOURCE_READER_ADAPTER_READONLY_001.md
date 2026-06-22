# PROMETEO_CONTEXT_SOURCE_READER_ADAPTER_READONLY_001

## Stato

PASS tecnico iniziale.

## Scopo

Implementare un ContextSourceReaderAdapter minimale, read-only, basato su:

`memory/context_source_index.json`

L'adapter consente il primo accesso governato a fonti locali già indicizzate, usando esclusivamente `source_id` logici.

## Capability

ContextSourceReaderAdapter read-only minimale.

## Vincoli rispettati

L'adapter:

- accetta solo `source_id` logici;
- non accetta path diretti come input;
- legge solo fonti presenti nel Context Source Index;
- verifica `access_mode = read_only`;
- blocca fonti con `runtime_enabled = true`;
- blocca path traversal;
- blocca path vietati;
- restituisce metadata sicuri;
- non espone path assoluti locali nei metadata;
- limita il contenuto restituito tramite `max_chars`.

## Cosa fa

Dato un `source_id` ammesso:

1. legge il Context Source Index;
2. verifica che la fonte sia dichiarata;
3. verifica governance e modalità read-only;
4. verifica il path;
5. restituisce metadata o excerpt limitato.

## Cosa NON fa

L'adapter non:

- collega TL Chat;
- collega ATLAS Engine;
- collega planner;
- collega database reale;
- accede a SMF reale;
- promuove contenuto recuperato a dato certo;
- esegue decisioni autonome;
- modifica file sorgente;
- abilita runtime retrieval.

## Codici di errore governati

Sono previsti errori espliciti per:

- INDEX_NOT_FOUND
- INDEX_INVALID
- NO_SOURCES_DECLARED
- SOURCE_ID_INVALID
- SOURCE_NOT_FOUND
- SOURCE_NOT_ALLOWED
- RUNTIME_SOURCE_BLOCKED
- SOURCE_PATH_MISSING
- PATH_TRAVERSAL_BLOCKED
- FORBIDDEN_PATH_BLOCKED
- SOURCE_FILE_NOT_FOUND

## Test

Test sintetici:

`tests/test_context_source_reader_adapter.py`

Coprono:

- lettura metadata ammessa;
- lettura excerpt ammesso;
- content limit;
- source_id sconosciuto;
- input path-like rifiutato;
- path vietato bloccato;
- path traversal bloccato;
- runtime_enabled bloccato.

Smoke test su indice reale:

`tests/test_context_source_reader_adapter_real_index.py`

Copre:

- lettura metadata da `memory/context_source_index.json`;
- lettura excerpt limitato da fonte reale indicizzata;
- blocco input path diretto;
- blocco source_id sconosciuto.

Esito locale:

`12 passed`

## Valore ottenuto

PROMETEO possiede ora il primo meccanismo operativo per leggere fonti indicizzate in modo governato, isolato e read-only.

Questo chiude il passaggio mancante tra:

- fonti documentate;
- indice sorgenti;
- contratti;
- test contract;

e:

- prima lettura reale governata.

## Limite intenzionale

Questa capability non abilita ancora il retrieval dentro TL Chat.

Il collegamento alla TL Chat resta fuori scope finché questo adapter non viene consolidato, revisionato e mergiato.

## Prossimo step consentito

Dopo merge:

definire il binding controllato tra TL Chat Context Resolver e ContextSourceReaderAdapter.

## Non fare ora

- non collegare TL Chat in questa PR;
- non collegare ATLAS Engine;
- non collegare planner;
- non aprire nuova capability AI;
- non usare dati industriali reali.
