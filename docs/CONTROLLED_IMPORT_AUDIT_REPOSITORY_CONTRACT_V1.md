# CONTROLLED_IMPORT_AUDIT_REPOSITORY_CONTRACT_V1

## SCOPO

Definire il contratto del futuro repository audit persistente per controlled
import, dopo lo schema SQL `controlled_import_audit_events`.

Questo documento non implementa repository runtime, non connette il DB, non
esegue migration, non scrive audit, non crea endpoint e non implementa apply.

```text
AUDIT_REPOSITORY_RUNTIME_IMPLEMENTED = FALSE
PERSISTENT_AUDIT_RUNTIME_IMPLEMENTED = FALSE
APPLY_RUNTIME_IMPLEMENTED = FALSE
```

## RESPONSABILITA_REPOSITORY

Il repository futuro dovra:

- validare input audit;
- rifiutare dati sensibili;
- salvare solo record audit ammessi;
- mantenere log append-only;
- restituire esito strutturato;
- garantire idempotenza su `audit_event_id`;
- non eseguire apply;
- non modificare preview, dry-run, SMF o planner.

## INPUT_AMMESSO

Input ammesso:

- record conforme a `controlled_import_audit_events`;
- preview reference;
- dry-run reference;
- actor/source/timestamp;
- confirmation token gia hashato;
- risk/write mode validi;
- rollback id quando richiesto;
- side effects summary sanificato.

## OUTPUT_ATTESO

Output futuro atteso:

- `ok`;
- `audit_event_id`;
- `persistence_status`;
- `created_at`;
- `idempotent_replay`;
- `error`;
- `failure_reason`;
- `apply_allowed`;
- `apply_executed`.

## CAMPI_OBBLIGATORI

Campi obbligatori:

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
- `side_effects_summary`;
- `persistence_status`;
- `apply_allowed`;
- `apply_executed`.

## CAMPI_VIETATI

Il repository futuro deve rifiutare:

- `confirmation_token` in chiaro;
- payload produttivo completo;
- dati cliente completi;
- path locali sensibili;
- immagini/PDF/Excel;
- BOM o SMF reali;
- token/segreti;
- dati non sanificati.

## CONFIRMATION_TOKEN_POLICY

Il repository accetta solo `confirmation_token_hash`.

Sono vietati:

- token in chiaro;
- log del token;
- salvataggio token in payload JSON;
- derivazione hash dentro repository senza contratto separato.

## RISK_LEVEL_VALIDATION

Valori ammessi:

- `LOW`;
- `MEDIUM`;
- `HIGH`;
- `BLOCKED`.

`HIGH` e `BLOCKED` non devono autorizzare apply futuro.

## WRITE_MODE_VALIDATION

Valori ammessi:

- `PREVIEW_ONLY`;
- `APPLY`.

`APPLY` sara ammesso solo in futuro con confirmation token hash, rollback id e
audit pre-apply valido.

## APPLY_FLAGS_VALIDATION

Regole:

- `apply_executed=true` richiede `apply_allowed=true`;
- `apply_executed=true` richiede `strong_confirmation_status=CONFIRMED`;
- `apply_executed=true` richiede `confirmation_token_hash`;
- `apply_executed=true` richiede `rollback_id`;
- in preview/dry-run entrambi devono restare `false`.

## ROLLBACK_ID_POLICY

`rollback_id` e obbligatorio per qualunque apply futuro.

Il repository deve rifiutare apply futuro senza rollback id.

## ACTOR_SOURCE_TIMESTAMP

Il repository deve rifiutare record senza:

- actor;
- source;
- timestamp UTC;
- audit event type.

## FAILURE_POLICY

Il repository futuro deve fallire in modo esplicito se:

- schema DB non disponibile;
- audit_event_id duplicato non idempotente;
- campi obbligatori mancanti;
- token in chiaro presente;
- risk/write mode non validi;
- apply flags incoerenti;
- rollback id mancante per apply;
- side effects non dichiarati;
- dati sensibili rilevati.

## IDEMPOTENCY_POLICY

`audit_event_id` e la chiave logica di idempotenza.

Retry con stesso `audit_event_id` e stesso contenuto puo restituire
`idempotent_replay=true`.

Retry con stesso `audit_event_id` e contenuto diverso deve fallire.

## IMMUTABILITY_POLICY

Repository append-only.

Vietati:

- update ordinario;
- delete ordinario;
- correzione distruttiva;
- sovrascrittura evento.

Correzioni future solo tramite evento compensativo.

## NO_UPDATE_DELETE

Il repository non deve esporre metodi runtime ordinari di update/delete.

Metodi ammessi futuri:

- `record_event`;
- `get_event`;
- `find_by_rollback_id`;
- `find_by_confirmation_token_hash`.

## PREVIEW_ENDPOINT_RELATION

Il preview endpoint non deve scrivere audit persistente finche repository runtime
non e implementato e testato.

La relazione futura sara esplicita e separata dal dry-run.

## DRY_RUN_RELATION

Ogni record persistente futuro deve riferirsi a un audit dry-run.

Repository deve rifiutare record senza dry-run reference.

## APPLY_RELATION

Apply futuro non puo chiamare repository in modo implicito o parziale.

Prima di apply futuro servono:

- audit persistente pre-apply;
- confirmation token hash;
- rollback id;
- risk policy;
- no-apply guard aggiornato.

## ERRORI_PREVISTI

Errori minimi futuri:

- `audit_schema_unavailable`;
- `audit_event_duplicate_conflict`;
- `missing_required_field`;
- `clear_confirmation_token_forbidden`;
- `invalid_risk_level`;
- `invalid_write_mode`;
- `invalid_apply_flags`;
- `rollback_id_required`;
- `sensitive_payload_forbidden`;
- `side_effects_missing`.

## TEST_MINIMI_FUTURI

Test futuri minimi:

- insert record valido sanificato;
- duplicate idempotente;
- duplicate conflict;
- blocco token in chiaro;
- blocco risk/write mode invalidi;
- blocco apply flags incoerenti;
- blocco dati sensibili;
- query per rollback id;
- nessun update/delete ordinario.

## TEST_DI_CONTRATTO

Comandi minimi attuali:

```bash
bash scripts/controlled_import_audit_repository_contract_v1_check.sh
make controlled-import-audit-repository-contract-v1
```

## NON_OBIETTIVI

Questo contratto non deve:

- implementare repository;
- connettere DB;
- eseguire migration;
- scrivere audit;
- implementare endpoint audit;
- implementare apply;
- toccare SMF;
- toccare planner;
- toccare frontend.

## PROSSIMO_PASSO

Prima di implementare repository runtime, aggiungere un guard che blocchi
repository, endpoint audit e apply non autorizzati fuori da questa sequenza.
