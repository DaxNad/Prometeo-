# CONTROLLED_IMPORT_AUDIT_DB_SCHEMA_CONTRACT_V1

## SCOPO

Definire il contratto dello schema PostgreSQL futuro per l'audit persistente
della pipeline controlled import.

Questo documento non crea migration, non crea tabelle, non modifica modelli DB,
non implementa runtime, non crea endpoint e non implementa apply.

```text
AUDIT_DB_SCHEMA_RUNTIME_IMPLEMENTED = FALSE
AUDIT_DB_MIGRATION_IMPLEMENTED = FALSE
PERSISTENT_AUDIT_RUNTIME_IMPLEMENTED = FALSE
APPLY_RUNTIME_IMPLEMENTED = FALSE
```

## TABLE_NAME

Nome tabella proposto:

```text
controlled_import_audit_events
```

## PRIMARY_KEY

Chiave primaria proposta:

- `id`: UUID o BIGSERIAL tecnico interno.

`audit_event_id` resta identificativo logico univoco e deve avere vincolo
unique.

## REQUIRED_COLUMNS

Colonne minime future:

- `id`;
- `audit_event_id`;
- `audit_event_type`;
- `actor`;
- `source`;
- `timestamp_utc`;
- `preview_reference`;
- `dry_run_reference`;
- `confirmation_token_hash`;
- `strong_confirmation_status`;
- `risk_level`;
- `write_mode`;
- `rollback_id`;
- `before_state_hash`;
- `before_state_ref`;
- `after_state_hash`;
- `after_state_ref`;
- `side_effects_summary`;
- `persistence_status`;
- `apply_allowed`;
- `apply_executed`;
- `failure_reason`;
- `created_at`.

## AUDIT_EVENT_ID

`audit_event_id` deve essere un identificativo logico stabile, non riusabile e
indicizzato.

Uso previsto:

- correlare preview, dry-run, conferma e apply futuro;
- ricostruire timeline audit;
- evitare ambiguita fra eventi.

## ACTOR_SOURCE_TIMESTAMP

Campi obbligatori:

- `actor`: soggetto/sistema che genera o conferma l'evento;
- `source`: origine della richiesta;
- `timestamp_utc`: timestamp UTC dell'evento;
- `created_at`: timestamp DB di inserimento.

## PREVIEW_DRY_RUN_REFERENCES

Campi obbligatori:

- `preview_reference`;
- `dry_run_reference`.

Devono riferirsi a preview e audit dry-run gia calcolati, senza duplicare
payload produttivi completi.

## CONFIRMATION_TOKEN_HASH

Il contratto vieta salvataggio del confirmation token in chiaro.

Campo richiesto:

- `confirmation_token_hash`.

Il token originale resta fuori dallo storage audit.

## STRONG_CONFIRMATION_STATUS

Campo richiesto:

- `strong_confirmation_status`.

Valori futuri minimi:

- `NOT_REQUIRED_FOR_PREVIEW`;
- `REQUIRED`;
- `CONFIRMED`;
- `MISSING`;
- `INVALID`.

## RISK_WRITE_MODE

Campi richiesti:

- `risk_level`;
- `write_mode`.

Valori ammessi per `risk_level`:

- `LOW`;
- `MEDIUM`;
- `HIGH`;
- `BLOCKED`.

Valori ammessi per `write_mode` nella fase attuale:

- `PREVIEW_ONLY`.

## ROLLBACK_RELATION

Campo richiesto:

- `rollback_id`.

Per eventi pre-apply futuri puo essere valorizzato come rollback previsto.
Per qualunque apply futuro deve essere valorizzato prima della scrittura.

## BEFORE_AFTER_STATE

Campi previsti:

- `before_state_hash`;
- `before_state_ref`;
- `after_state_hash`;
- `after_state_ref`.

Il contratto preferisce hash o riferimenti sanificati, non snapshot completi di
dati produttivi reali.

## SIDE_EFFECTS_SUMMARY

Campo richiesto:

- `side_effects_summary`.

Deve indicare in modo strutturato e sintetico:

- DB write;
- SMF write;
- planner update;
- file write;
- external call;
- OCR;
- AI runtime.

## PERSISTENCE_STATUS

Campo richiesto:

- `persistence_status`.

Valori futuri minimi:

- `PENDING`;
- `RECORDED`;
- `FAILED`;
- `BLOCKED`.

## APPLY_FLAGS

Campi richiesti:

- `apply_allowed`;
- `apply_executed`.

Nella fase attuale entrambi devono restare `false` in qualunque runtime
preview/dry-run.

## FAILURE_REASON

Campo richiesto:

- `failure_reason`.

Deve essere valorizzato quando:

- audit non registrabile;
- dati sensibili rilevati;
- conferma forte mancante;
- rollback id mancante;
- risk policy blocca;
- target write non autorizzato.

## IMMUTABLE_LOG_POLICY

Policy futura:

- append-only;
- nessun update distruttivo;
- nessun delete operativo ordinario;
- correzioni solo con evento compensativo;
- rollback tracciato come evento separato.

## RETENTION_POLICY

Retention futura:

- durata definita da policy aziendale;
- nessuna retention indefinita senza motivazione;
- esportazione sanificata se richiesta;
- cancellazione governata solo da processo autorizzato.

## SENSITIVE_DATA_FORBIDDEN

Vietato salvare:

- token in chiaro;
- dati cliente completi;
- nomi operatori non autorizzati;
- path locali sensibili;
- immagini/PDF/Excel;
- specifiche reali;
- payload produttivi completi;
- BOM o SMF reali.

## APPLY_RELATION

Apply futuro e vietato se:

- tabella audit non esiste;
- schema non passa i test;
- audit pre-apply non e registrabile;
- `confirmation_token_hash` manca;
- `rollback_id` manca;
- `apply_allowed` non e coerente con risk policy.

Questo contratto non implementa apply.

## ROLLBACK_RELATION_FUTURE

Rollback futuro deve collegarsi a:

- `rollback_id`;
- `audit_event_id` originale;
- evento apply;
- evento compensativo.

Rollback non deve cancellare audit storico.

## TEST_DI_CONTRATTO

Comandi minimi:

```bash
bash scripts/controlled_import_audit_db_schema_contract_v1_check.sh
make controlled-import-audit-db-schema-contract-v1
```

## NON_OBIETTIVI

Questo contratto non deve:

- creare migration;
- creare modello DB;
- scrivere su DB;
- implementare runtime audit persistente;
- implementare endpoint audit;
- implementare apply;
- toccare SMF;
- toccare planner;
- toccare frontend.

## PROSSIMO_PASSO

Prima di qualunque migration, aggiungere un guard che impedisca schema DB o
storage audit runtime non autorizzati fuori dal percorso controlled import.
