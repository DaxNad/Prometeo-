# PROMETEO_TL_CHAT_CONTEXT_READER_BINDING_001

## Stato

DRAFT vincolante.

## Scopo

Definire il binding controllato tra:

- TL Chat Context Resolver
- ContextSourceReaderAdapter read-only

Il binding stabilisce quando e come il resolver della TL Chat potra richiedere contenuto governato da fonti indicizzate.

Questa capability non collega ancora il resolver all'adapter in esecuzione operativa.

## Capability

TL Chat Context Resolver verso ContextSourceReaderAdapter binding contract.

## Contesto

PROMETEO dispone ora di:

- Context Source Index;
- ContextSourceReaderAdapter read-only;
- test di sicurezza minimi;
- smoke test su indice reale.

Il prossimo passaggio non deve essere un collegamento diretto e libero.

Serve prima un binding che definisca:

- quali richieste sono ammesse;
- quali source_id sono ammessi;
- quale output puo ricevere il resolver;
- come impedire promozione indebita a dato certo;
- quali test devono bloccare regressioni, leak e scope creep.

## Principio

Il TL Chat Context Resolver non deve leggere file, path o sorgenti direttamente.

Deve poter richiedere solo source_id logico.

Il ContextSourceReaderAdapter resta l'unico componente autorizzato alla lettura read-only delle fonti indicizzate.

## Confine architetturale

Confine autorizzato:

TL Chat Context Resolver
-> source_id logico ammesso
-> ContextSourceReaderAdapter
-> metadata sicuri / excerpt limitato
-> risultato governato

## Input ammessi

Il resolver puo passare all'adapter solo:

- source_id logico;
- richiesta metadata;
- richiesta excerpt limitato;
- finalita contestuale dichiarata.

Non sono ammessi:

- path diretti;
- path relativi;
- path assoluti;
- richieste libere a file system;
- richieste verso fonti non indicizzate;
- richieste verso fonti non read-only.

## Source ID ammessi

Sono ammessi solo source_id presenti in memory/context_source_index.json e con:

- access_mode = read_only;
- runtime flag non abilitato;
- exists = true.

## Output ammessi

Il resolver puo ricevere solo:

- source_id;
- status governato;
- metadata sicuri;
- excerpt limitato;
- indicazione di limite applicato;
- codice errore governato.

Il resolver non deve ricevere:

- path assoluti locali;
- contenuti illimitati;
- dati produttivi reali non autorizzati;
- informazioni non presenti nell'indice;
- contenuto promosso automaticamente a dato certo.

## Regola di interpretazione

Qualsiasi contenuto recuperato tramite adapter deve essere trattato come contesto recuperato da fonte indicizzata.

Non deve essere trattato automaticamente come:

- dato certo;
- decisione operativa;
- istruzione esecutiva.

La TL Chat puo usare il contenuto solo per generare una risposta contestuale con tracciabilita della fonte.

## Risposte TL Chat consentite

Quando usa contenuto proveniente dall'adapter, la TL Chat deve indicare:

- fonte usata;
- stato della fonte;
- eventuale limite dell'excerpt;
- grado di certezza;
- eventuale necessita di verifica TL.

## Risposte TL Chat vietate

La TL Chat non deve:

- inventare contenuti mancanti;
- dedurre dati non presenti nella fonte;
- fondere piu fonti senza dichiararlo;
- trasformare preview o excerpt in dato certo;
- generare ordini operativi autonomi;
- usare il contenuto per modificare stato applicativo.

## Errori governati

Il resolver deve propagare o tradurre in modo esplicito errori come:

- SOURCE_NOT_FOUND;
- SOURCE_ID_INVALID;
- SOURCE_NOT_ALLOWED;
- SOURCE_PATH_MISSING;
- PATH_TRAVERSAL_BLOCKED;
- FORBIDDEN_PATH_BLOCKED;
- SOURCE_FILE_NOT_FOUND;
- CONTENT_LIMIT_APPLIED.

## Comportamento su errore

In caso di errore, la TL Chat deve rispondere in modo controllato:

- dichiarare che la fonte non e disponibile;
- non inventare contenuto;
- non proporre azioni esecutive;
- indicare che serve verifica o fonte valida.

## Cosa abilita questo binding

Questo binding abilita la progettazione del prossimo step:

TL Chat Context Resolver governed reader integration.

## Cosa NON abilita

Questo binding non abilita ancora:

- collegamento operativo diretto in TL Chat;
- uso dell'adapter per decisioni autonome;
- accesso a fonti non indicizzate;
- uso di sistemi produttivi reali;
- collegamenti ad altri motori o componenti orchestration;
- modifica dello stato applicativo.

## Test attesi per il prossimo step

La futura integrazione dovra dimostrare almeno:

1. il resolver invia solo source_id logici;
2. il resolver non accetta path diretti;
3. il resolver riceve metadata sicuri;
4. il resolver riceve excerpt limitato;
5. il resolver gestisce SOURCE_NOT_FOUND;
6. il resolver gestisce CONTENT_LIMIT_APPLIED;
7. la TL Chat dichiara la fonte usata;
8. la TL Chat non promuove excerpt a dato certo;
9. nessun path assoluto locale viene esposto;
10. nessuna fonte non indicizzata viene letta.

## Definition of Done

Questa capability e chiusa quando:

- il binding e documentato;
- il test documentale conferma i vincoli minimi;
- non viene introdotto collegamento operativo;
- tutti i guard restano verdi.

## Prossimo step consentito dopo merge

Dopo merge di questo binding:

implementare una integrazione minima e testata tra TL Chat Context Resolver e ContextSourceReaderAdapter.

## Non fare ora

- non implementare ancora il collegamento operativo;
- non cambiare comportamento della TL Chat;
- non collegare componenti orchestration;
- non collegare motori reasoning esterni;
- non usare fonti produttive reali;
- non aprire nuove capability AI.
