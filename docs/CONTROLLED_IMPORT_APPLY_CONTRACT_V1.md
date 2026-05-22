# CONTROLLED_IMPORT_APPLY_CONTRACT_V1

## SCOPO

Definire il contratto minimo per autorizzare in futuro un apply controllato
della pipeline controlled import.

Questo documento non implementa apply runtime, non autorizza scritture e non
rende disponibile alcun endpoint apply.

```text
APPLY_RUNTIME_IMPLEMENTED = FALSE
```

## ORDINE_OBBLIGATORIO

L'ordine di chiusura resta:

1. preview-only;
2. audit dry-run;
3. no-apply guard;
4. contratto apply;
5. audit persistente;
6. solo dopo, eventuale apply controllato.

## PREREQUISITI_APPLY

Un apply futuro potra essere valutato solo se esistono e passano:

- preview controllata;
- schema contract preview;
- audit dry-run;
- no-apply guard;
- contratto apply;
- audit persistente progettato e testato;
- rollback contract;
- test no-data-leak;
- test no-SMF/DB/planner write non autorizzato.

## STRONG_CONFIRMATION

Ogni apply futuro richiede conferma forte esplicita e separata dalla preview.

La conferma deve includere almeno:

- identificativo operazione;
- utente/ruolo;
- motivazione;
- rischio accettato;
- riferimento preview;
- riferimento audit dry-run;
- dichiarazione `CONFERMO APPLY CONTROLLATO`;
- rollback id previsto.

Senza conferma forte l'apply deve restare bloccato.

## PERSISTENT_AUDIT_REQUIRED

Prima di qualunque apply futuro deve esistere audit persistente.

L'audit persistente deve coprire:

- evento prima dell'apply;
- evento durante l'apply;
- evento dopo l'apply;
- esito;
- errore se presente;
- attore;
- fonte;
- preview usata;
- rischio;
- rollback id;
- side effects dichiarati.

## ROLLBACK_ID_REQUIRED

Ogni apply futuro deve generare o ricevere un `rollback_id` prima della
scrittura.

Senza `rollback_id` valido l'apply e bloccato.

## DRY_RUN_REQUIRED

Ogni apply futuro deve derivare da una preview con audit dry-run gia eseguito.

Sono bloccati:

- apply senza preview;
- apply senza audit dry-run;
- apply con preview modificata dopo la conferma;
- apply con `write_mode` diverso da `PREVIEW_ONLY` nella fase precedente.

## RISK_POLICY

Politica rischio minima:

- `LOW`: ammissibile solo con conferma forte e audit persistente;
- `MEDIUM`: ammissibile solo con conferma forte, audit persistente e motivazione;
- `HIGH`: bloccato salvo processo eccezione non ancora definito;
- `BLOCKED`: sempre bloccato.

In questa versione nessun rischio autorizza apply runtime.

## WRITE_AUTHORIZATION

Le scritture future devono essere autorizzate per target esplicito.

Target possibili solo in versione futura:

- audit persistente;
- staging controllato;
- DB operativo;
- SMF governato;
- planner state.

Nessun target e autorizzato da questo contratto.

## NO_WRITE_UNTIL_TESTED

Nessuna scrittura e consentita finche il contratto non e testato e non esiste
un audit persistente verificato.

Restano vietati:

- DB write;
- SMF write;
- planner update;
- file data write;
- apply endpoint;
- apply service.

## FAILURE_MODES

L'apply futuro deve fallire se:

- manca conferma forte;
- manca audit dry-run;
- manca audit persistente;
- manca rollback id;
- risk_level e `HIGH` o `BLOCKED`;
- preview e audit non corrispondono;
- side effects non sono dichiarati;
- target write non e autorizzato;
- dati sensibili sono presenti;
- no-apply guard non passa.

## TEST_DI_CONTRATTO

Comandi minimi:

```bash
bash scripts/controlled_import_apply_contract_v1_check.sh
make controlled-import-apply-contract-v1
```

## NON_OBIETTIVI

Questo contratto non deve:

- creare endpoint apply;
- creare servizio apply;
- scrivere su DB;
- scrivere su SMF;
- aggiornare planner;
- aggiungere frontend;
- usare OCR;
- usare AI;
- introdurre dati reali.

## PROSSIMO_PASSO

Il prossimo micro-passo corretto e progettare `CONTROLLED_IMPORT_PERSISTENT_AUDIT_CONTRACT_V1`.
Solo dopo un audit persistente testato sara possibile discutere un apply
controllato.
