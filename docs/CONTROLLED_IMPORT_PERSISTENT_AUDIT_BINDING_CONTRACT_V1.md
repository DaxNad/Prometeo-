# CONTROLLED_IMPORT_PERSISTENT_AUDIT_BINDING_CONTRACT_V1

## SCOPO

Definire il contratto del futuro binding runtime tra endpoint preview
controlled import e `ControlledImportPersistentAuditService`.

Questo documento non modifica endpoint, non collega il servizio alla preview,
non connette il DB, non esegue migration e non implementa apply.

```text
PERSISTENT_AUDIT_BINDING_RUNTIME_IMPLEMENTED = FALSE
PERSISTENT_AUDIT_RUNTIME_IMPLEMENTED = FALSE
APPLY_RUNTIME_IMPLEMENTED = FALSE
```

## BINDING_AMMESSO

Il binding futuro sara ammesso solo quando:

- il chiamante richiede audit persistente con flag esplicito;
- sono presenti `actor` e `source`;
- e presente `confirmation_token_hash`;
- non e presente `confirmation_token` in chiaro;
- il preview result e gia stato generato;
- audit dry-run e gia stato generato;
- il risk level non e `BLOCKED` in modalita ordinaria;
- il repository audit persistente e disponibile e testato;
- la risposta API resta `PREVIEW_ONLY`.

## BINDING_VIETATO

Il binding e vietato quando:

- il flag esplicito non e presente;
- manca `confirmation_token_hash`;
- compare `confirmation_token` in chiaro;
- mancano `actor` o `source`;
- il risk level e `BLOCKED`;
- repository o DB non sono disponibili e non esiste fallback sicuro;
- la richiesta tenta `APPLY`;
- la richiesta richiede scritture SMF o planner;
- la richiesta contiene dati reali non sanificati.

## FLAG_ESPLICITO

Il default deve restare:

- audit dry-run;
- nessuna persistenza;
- nessuna connessione DB;
- nessun apply.

Per attivare il binding futuro servira un flag esplicito, ad esempio:

- `persistent_audit_requested=true`.

In assenza del flag, l'endpoint preview deve continuare a restituire solo
preview e audit dry-run.

## DEFAULT_DRY_RUN_NO_PERSISTENCE

Comportamento default obbligatorio:

- `write_mode="PREVIEW_ONLY"`;
- `required_human_confirmation=true`;
- `apply_allowed=false`;
- `audit_persistence="NONE"`;
- nessuna chiamata a repository persistente.

## CONFIRMATION_TOKEN_POLICY

Il binding futuro accetta solo `confirmation_token_hash`.

Sono vietati:

- `confirmation_token` in chiaro;
- log del token;
- token dentro preview;
- token dentro audit dry-run;
- token dentro risposta API.

## ACTOR_SOURCE_POLICY

`actor` e `source` sono obbligatori per qualunque persistenza futura.

Il binding deve rifiutare richieste senza:

- actor identificabile;
- source del canale runtime;
- timestamp audit coerente.

## BLOCKED_RISK_POLICY

`risk_level="BLOCKED"` non e persistibile in modalita ordinaria dal binding
preview.

Per casi `BLOCKED` il sistema deve restare in dry-run/no persistence, salvo
contratto separato esplicito.

## FALLBACK_REPOSITORY_DB

Se repository o DB non sono disponibili:

- la preview non deve essere persa;
- il dry-run resta disponibile;
- la risposta deve indicare persistenza non eseguita;
- non deve esserci retry implicito mutativo;
- non deve esserci fallback su file locale non contrattualizzato;
- non deve esserci apply.

## RISPOSTA_API_ATTESA

Risposta futura attesa quando il binding e autorizzato:

- `preview`;
- `audit_dry_run`;
- `persistent_audit`;
- `audit_event_id`;
- `rollback_id`;
- `write_mode="PREVIEW_ONLY"`;
- `required_human_confirmation=true`;
- `apply_allowed=false`;
- `apply_executed=false`;
- `audit_persistence="RECORDED"` oppure failure esplicito.

## NO_PREVIEW_MUTATION

Il binding non deve modificare:

- payload preview originale;
- preview result;
- audit dry-run;
- route;
- rischio calcolato;
- messaggi operativi gia prodotti.

Il servizio audit persistente deve ricevere copie o dati derivati.

## NO_APPLY

Questo contratto non autorizza apply.

Il binding futuro deve mantenere:

- `write_mode="PREVIEW_ONLY"`;
- `apply_allowed=false`;
- `apply_executed=false`.

## NO_SMF_PLANNER_WRITE

Il binding futuro non deve scrivere:

- SMF;
- planner;
- DB produttivo non audit;
- file runtime;
- dati reali.

Unica scrittura futura ammessa dal binding: repository audit persistente
contrattualizzato.

## FAILURE_POLICY

Il binding deve fallire in modo esplicito se:

- flag richiesto incoerente;
- token hash mancante;
- token in chiaro presente;
- actor/source mancanti;
- risk level `BLOCKED`;
- repository non disponibile;
- DB audit non disponibile;
- servizio audit persistente restituisce errore;
- risposta repository non conferma `PREVIEW_ONLY`.

In failure, l'endpoint deve mantenere preview/dry-run e nessun apply.

## TEST_MINIMI_FUTURI

Test futuri minimi:

- default endpoint resta dry-run/no persistence;
- flag esplicito chiama servizio audit persistente;
- assenza flag non chiama repository;
- `confirmation_token` in chiaro viene rifiutato;
- `confirmation_token_hash` e obbligatorio;
- `actor/source` sono obbligatori;
- `BLOCKED` non viene persistito;
- preview non viene mutata;
- repository failure non produce apply;
- SMF/planner/frontend non vengono toccati.

## TEST_DI_CONTRATTO

Questo contratto e verificato da:

```bash
bash scripts/controlled_import_persistent_audit_binding_contract_v1_check.sh
make controlled-import-persistent-audit-binding-contract-v1
```

## NON_OBIETTIVI

Non obiettivi di questo micro-passo:

- modificare endpoint preview;
- collegare preview endpoint al servizio;
- connettere DB;
- eseguire migration;
- implementare endpoint audit;
- implementare apply;
- scrivere SMF/planner/frontend;
- usare dati reali.

## PROSSIMO_PASSO

Solo dopo questo contratto, il prossimo passo possibile sara implementare un
binding runtime esplicito e testato, mantenendo il default dry-run/no
persistence.
