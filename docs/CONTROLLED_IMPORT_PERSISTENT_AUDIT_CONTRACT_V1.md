# CONTROLLED_IMPORT_PERSISTENT_AUDIT_CONTRACT_V1

## SCOPO

Definire il contratto dell'audit persistente necessario prima di qualunque
futuro apply controllato nella pipeline controlled import.

Questo documento non implementa audit persistente runtime, non crea endpoint,
non scrive su DB, non scrive su file, non tocca SMF, non tocca planner e non
implementa apply.

```text
PERSISTENT_AUDIT_RUNTIME_IMPLEMENTED = FALSE
APPLY_RUNTIME_IMPLEMENTED = FALSE
```

## WHY_PERSISTENT_AUDIT

L'audit persistente serve a rendere verificabile ogni passaggio critico prima
di una scrittura futura.

Senza audit persistente non e possibile dimostrare:

- chi ha richiesto l'operazione;
- quale preview e stata valutata;
- quale rischio e stato accettato;
- quale conferma forte e stata fornita;
- cosa sarebbe scritto;
- quale rollback id esiste;
- se side effects e target write erano autorizzati.

## WHEN_GENERATED

In futuro l'audit persistente dovra essere generato:

- prima dell'apply, per registrare richiesta, preview, dry-run e conferma;
- durante l'apply, per registrare target, stato e side effects;
- dopo l'apply, per registrare esito, errore o rollback necessario.

In questa versione non viene generato nessun audit persistente runtime.

## REQUIRED_FIELDS

Ogni audit persistente futuro deve includere almeno:

- `audit_event_id`;
- `audit_event_type`;
- `actor`;
- `source`;
- `timestamp_utc`;
- `preview_reference`;
- `dry_run_reference`;
- `confirmation_token`;
- `strong_confirmation`;
- `risk_level`;
- `write_mode`;
- `persistence_status`;
- `rollback_id`;
- `before_state`;
- `after_state`;
- `side_effects`;
- `target_write_authorization`;
- `result`;
- `error`.

## PREVIEW_RELATION

L'audit persistente deve riferirsi a una preview controllata esistente e
immutabile.

Sono vietati:

- audit senza preview;
- audit con preview mancante;
- audit con preview modificata dopo conferma;
- audit con `write_mode` non coerente con la fase precedente.

## DRY_RUN_RELATION

L'audit persistente deve riferirsi a un audit dry-run gia generato.

Sono vietati:

- audit persistente senza dry-run;
- apply futuro senza dry-run;
- dry-run non collegato alla preview;
- dry-run con side effects non dichiarati.

## APPLY_RELATION

Un apply futuro e vietato senza audit persistente valido.

L'audit persistente deve essere il ponte obbligatorio tra:

preview -> audit dry-run -> conferma forte -> audit persistente -> eventuale apply.

## ROLLBACK_ID_REQUIRED

`rollback_id` e obbligatorio prima di qualunque apply futuro.

Senza `rollback_id` valido:

- l'audit persistente deve essere marcato non valido;
- l'apply deve essere bloccato;
- nessuna scrittura deve partire.

## STRONG_CONFIRMATION

L'audit persistente deve registrare:

- `confirmation_token`;
- `strong_confirmation`;
- attore;
- ruolo o fonte;
- motivo;
- rischio accettato;
- timestamp.

La conferma forte deve essere separata dalla preview e dal dry-run.

## ACTOR_SOURCE_TIMESTAMP

Ogni evento futuro deve includere:

- `actor`: soggetto o sistema che richiede/approva;
- `source`: origine della richiesta;
- `timestamp_utc`: timestamp UTC ISO;
- `audit_event_type`: fase dell'audit.

## RISK_WRITE_MODE_POLICY

L'audit persistente deve riportare:

- `risk_level`;
- `write_mode`;
- `target_write_authorization`;
- `side_effects`.

Policy minima:

- `LOW`: registrabile, non sufficiente da solo ad applicare;
- `MEDIUM`: registrabile con motivazione;
- `HIGH`: registrabile ma apply bloccato salvo eccezione futura;
- `BLOCKED`: registrabile solo come blocco, mai applicabile.

## BEFORE_AFTER_STATE

`before_state` e `after_state` sono previsti nel contratto ma non ancora
implementati runtime.

In futuro:

- `before_state` descrivera lo stato prima della scrittura;
- `after_state` descrivera lo stato dopo la scrittura;
- entrambi dovranno essere sanificati;
- entrambi dovranno evitare dati sensibili completi.

## PERSISTENCE_STATUS

Valori minimi futuri:

- `NOT_IMPLEMENTED`;
- `PENDING`;
- `RECORDED`;
- `FAILED`;
- `BLOCKED`.

In questa versione lo stato effettivo resta:

```text
persistence_status = NOT_IMPLEMENTED
```

## FAILURE_POLICY

L'audit persistente deve fallire o bloccare se:

- manca preview;
- manca dry-run;
- manca confirmation_token;
- manca strong_confirmation;
- manca actor/source/timestamp;
- manca rollback_id;
- risk_level e `HIGH` o `BLOCKED` e non esiste processo eccezione futuro;
- write target non autorizzato;
- side effects non dichiarati;
- dati sensibili sono presenti;
- apply runtime viene introdotto prima del contratto persistente testato.

## NO_APPLY_WITHOUT_VALID_AUDIT

Qualunque apply futuro e vietato se non esiste audit persistente valido.

Questo contratto non autorizza apply.

## TEST_DI_CONTRATTO

Comandi minimi:

```bash
bash scripts/controlled_import_persistent_audit_contract_v1_check.sh
make controlled-import-persistent-audit-contract-v1
```

## NON_OBIETTIVI

Questo contratto non deve:

- implementare audit persistente runtime;
- creare endpoint audit;
- creare tabelle DB;
- scrivere file;
- toccare SMF;
- toccare planner;
- implementare apply;
- introdurre OCR;
- introdurre AI;
- usare dati reali.

## PROSSIMO_PASSO

Il prossimo micro-passo corretto e definire un test/guard che impedisca audit
persistente runtime non autorizzato e mantenga apply bloccato finche questo
contratto non diventa implementazione testata.
