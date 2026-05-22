# CONTROLLED_IMPORT_AUDIT_STORAGE_DECISION_V1

## SCOPO

Decidere lo storage futuro per l'audit persistente della pipeline controlled
import, prima di qualunque implementazione runtime.

Questo documento non implementa storage, non crea migration, non scrive su DB,
non scrive su file runtime, non crea endpoint audit e non implementa apply.

```text
AUDIT_STORAGE_RUNTIME_IMPLEMENTED = FALSE
PERSISTENT_AUDIT_RUNTIME_IMPLEMENTED = FALSE
APPLY_RUNTIME_IMPLEMENTED = FALSE
```

## OPZIONI_VALUTATE

Opzioni considerate:

1. PostgreSQL audit table.
2. File JSONL locale controllato.
3. Log applicativo standard.
4. Storage esterno/cloud.
5. Nessuna persistenza.

## OPZIONE_RACCOMANDATA

Opzione raccomandata futura: PostgreSQL audit table.

Motivo:

- transazionalita;
- query verificabili;
- relazione naturale con utenti, preview, confirmation token e rollback id;
- controllo retention;
- backup coerente con runtime applicativo;
- testabilita con database di test;
- minore rischio di dispersione rispetto a file locali non governati.

Questa raccomandazione non autorizza migration o scrittura DB in questo step.

## OPZIONI_VIETATE_ORA

Vietate per ora:

- storage esterno/cloud;
- nessuna persistenza come soluzione finale;
- file JSONL runtime fuori da percorso governato;
- log applicativo standard come unica fonte audit;
- qualunque scrittura DB senza contratto schema e test dedicati.

## POSTGRESQL_AUDIT_TABLE

PostgreSQL e la destinazione raccomandata futura.

Requisiti minimi futuri:

- tabella audit dedicata;
- schema versionato;
- migration separata e testata;
- nessun payload sensibile completo;
- indici su `audit_event_id`, `rollback_id`, `confirmation_token`,
  `timestamp_utc`;
- retention definita;
- test no-write non autorizzato.

## JSONL_LOCALE

File JSONL locale puo essere ammesso solo per sviluppo o fallback controllato.

Limiti:

- rischio path sensibili;
- retention piu fragile;
- backup meno governato;
- concorrenza piu debole;
- rischio confusione con session memory o dati locali.

Non e raccomandato come storage primario.

## APPLICATION_LOG

Il log applicativo standard puo contenere solo eventi tecnici sintetici.

Non deve essere fonte primaria dell'audit controlled import perche:

- retention non e dominio-specifica;
- correlazione rollback/conferma e fragile;
- parsing e fragile;
- rischio esposizione accidentale.

## EXTERNAL_CLOUD_STORAGE

Storage esterno/cloud e vietato in questa fase.

Motivo:

- rischio dati sensibili;
- governance cliente non definita;
- segreti e token non in scope;
- compliance non definita;
- non necessario per uso interno controllato.

## NO_PERSISTENCE

Nessuna persistenza e accettabile solo nello stato attuale di dry-run.

Non e accettabile per autorizzare apply futuro.

## SECURITY_RATIONALE

La scelta PostgreSQL futura riduce:

- duplicazione fuori controllo;
- path locali sensibili;
- log non strutturati;
- dispersione dati;
- ambiguita su rollback e conferma.

L'audit deve salvare metadati e riferimenti, non dati produttivi completi.

## TESTABILITY_RATIONALE

PostgreSQL audit table futura e testabile con:

- schema test;
- insert controllati;
- query su rollback id;
- query su confirmation token;
- failure test;
- test retention;
- test assenza dati sensibili.

## ROLLBACK_RELATION

Ogni evento audit persistente futuro deve collegarsi a un `rollback_id`.

Il `rollback_id` deve essere generato prima dell'apply e deve permettere
ricostruzione sicura senza salvare payload sensibili completi.

## CONFIRMATION_RELATION

Ogni evento audit persistente futuro deve collegarsi a un
`confirmation_token`.

Il token deve dimostrare che esiste conferma forte separata da preview e dry-run.

## APPLY_RELATION

Apply futuro e vietato finche:

- lo storage audit non e implementato e testato;
- il rollback id non e registrabile;
- il confirmation token non e registrabile;
- la policy rischio non e applicata;
- il no-apply guard resta verde.

## FAILURE_POLICY

L'audit storage futuro deve fallire o bloccare se:

- storage non disponibile;
- schema audit mancante;
- rollback id mancante;
- confirmation token mancante;
- actor/source/timestamp mancanti;
- risk_level non ammesso;
- write_mode incoerente;
- payload contiene dati sensibili;
- retention non definita;
- apply richiesto senza audit registrabile.

## RETENTION_MINIMA

Retention minima prevista: conservare audit per durata sufficiente a:

- investigare modifiche operative;
- ricostruire conferme;
- associare rollback id;
- verificare responsabilita e fonte.

La durata precisa resta da definire con policy aziendale. Fino ad allora non
si implementa storage runtime.

## DATI_SENSIBILI_DA_NON_SALVARE

Non salvare:

- dati cliente completi;
- nomi operatori se non autorizzati;
- path locali sensibili;
- immagini, PDF, Excel;
- specifiche reali;
- token/segreti;
- payload produttivi completi;
- BOM o SMF reali.

## AUDIT_TECNICO_VS_DATI_PRODUTTIVI

Audit tecnico significa salvare metadati verificabili su operazione, rischio,
conferma, fonte, rollback e risultato.

Dati produttivi reali sono contenuti operativi o tecnici sensibili. Non devono
essere copiati integralmente nello storage audit.

## TEST_DI_DECISIONE

Comandi minimi:

```bash
bash scripts/controlled_import_audit_storage_decision_v1_check.sh
make controlled-import-audit-storage-decision-v1
```

## PROSSIMO_PASSO

Prima di implementare runtime, creare un contratto schema tabella audit
PostgreSQL futura e un guard che continui a bloccare storage non autorizzato.
