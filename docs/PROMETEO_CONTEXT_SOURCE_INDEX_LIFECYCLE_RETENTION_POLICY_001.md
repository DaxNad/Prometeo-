# PROMETEO_CONTEXT_SOURCE_INDEX_LIFECYCLE_RETENTION_POLICY_001


## Scopo

Questo documento definisce la policy documentale per lifecycle, retention, superseding, obsolescenza e sostituzione controllata delle fonti indicizzate nel Context Source Index di PROMETEO.

Questa capability \u00de esclusivamente documentale e test-only.

Non abilita:

- runtime binding;
- TL Chat binding;
- ATLAS Engine binding;
- planner binding;
- endpoint FastAPI;
- retrieval runtime;
- lettura contenuto integrale delle fonti;
- scrittura automatica su fonti, SMF, database orepository.

## Stato capability


```text
CAPABILITY: CONTEXT_SOURCE_INDEX_LIFECYCLE_RETENTION_POLICY_001
TYPE: DOCUMENTAL_TEST_ONLY
RUNTIME_BINDING: FORBIDDEN
FULL_CONTENT_READING: FORBIDDEN
INDEX_MUTATION_RUNTIME: FORBIDDEN
TL_CHAT_BINDING: FORBIDDEN
ATLAS_ENGINE_BINDING: FORBIDDEN
PLANNER_BINDING: FORBIDDEN
```

## Stati ammessi per le fonti indicizzate


```text
ACTIVE
SUPERSEDED
DEPRECATED
- REJECTED
ARCHIVED
DRAFT
```

## Regole lifecycle

### ACTIVE

Una fonte ACTIVE rappresenta il riferimento corrente per una certa area di governance o architettura.

Richiede:

- path relativo ammesso;
- categoria chiara;
- motivo di inclusione;
- access_mode=read_only;
- runtime_enabled=false;
- nessun payload con text, content o bytes.

### SUPERSEDED

Una fonte SUPERSEDED \u00de stata sostituita da una fonte successiva.

Richiede:

- riferimento alla fonte sostitutiva;
- motivo della sostituzione;
- divieto di uso come riferimento corrente.

### DEPRECATED

Una fonte DEPRECATED \u00de ancora presente ma il suo uso futuro \u00e8 sconsigliato.

Richiede:

- motivo della deprecazione;
- rischio associato;
- eventuale azione consigliata.

### REJECTED

Una fonte REJECTED non deve entrare nel perimetro governato o deve essere esclusa.

Motivi massimi:

- path vietato;
- dato reale sensibile;
- file runtime;
- file generato;
- contenuto non governato;
- duplicazione pericolosa;
- scope creep.

### ARCHIVED

Una fonte ARCHIVED non \u00e8 pi\u00f9 operativa ma rimane utile come storico.

Non deve essere usata come riferimento corrente.

### DRAFT

Una fonte DRAFT non \u00e8 ancora approvata.

Non deve influenzare decisioni operative, planner, TL Chat o ATLAS Engine.


## Retention

Le fonti non devono essere cancellate automaticamente.

```text
DELETE_AUTOMATICALLY: FALSE
PREFER_SUPERSEDE_OVER_DELETE: TRUE
PREFER_ARCHIVE_OVER_DELETE: TRUE
```

La cancellazione \u00e8 ammessa solo se:

1. la fonte \u00e8 duplicata;
2. la fonte \u00e8 errata;
3. la fonte viola policy;
4. la fonte contiene dati non ammessi;
5. esiste una decisione esplicita e tracciata.

## Superseding

La sostituzione tra fonti deve essere esplicita.

```text
old_source.status = SUPERSEDED
old_source.superseded_by = new_source.id
new_source.replaces = old_source.id
reason = ...
```

La sostituzione non deve cancellare la storia decisionale.

## Obsolescenza

Una fonte deve essere candidata a obsolescenza quando:

- contraddice una fonte pi\u00f9 recente;
- contraddice una conferma TL;
- contraddice una specifica reale confermata;
- mantiene regole architetturali superate;
- induce interpretazioni incompatibili con la governance corrente.

L'obsolescenza non implica cancellazione. Implica revisione e possibile cambio stato.

## Gerarchia fonti preservata

1. specifica reale + conferma TL;
2. metadata normalizzato;
3. SMF;
4. registry locali;
5. BOM/cache/export/preview;
6. inferenza modello.

Una fonte inferiore non pu\u00f2 sostituire automaticamente una fonte superiore.

## Divieti

Divieti assoluti:

- runtime binding;
- endpoint FastAPI;
- retrieval runtime;
- lettura contenuto integrale;
- mutazione automatica dell'indice da runtime;
- collegamento TL Chat;
- collegamento ATLAS Engine;
- collegamento planner;
- agenti liberi;
- acceso a dati reali privati;
- path locali assoluti.

## Regola anti-scope-creep

Questa capability pu\u00f2 solo definire policy.

Non pu\u00f2 modificare il comportamento del sistema.

Non pu\u00f2 trasformare il Context Source Index in una fonte runtime.

Non pu\u00f2 autorizzare il passaggio da metadata-only a content-reading.

## Test futuri ammessi

Una capability successiva potr\u00d0 aggiungere test documentali per verificare che:

- ogni fonte abbia stato ammesso;
- ogni fonte abbia runtime_enabled=false;
- ogni fonte abbia access_mode=read_only;
- ogni relazione superseded_by punti a una fonte esistente;
- nessuna fonte REJECTED venga trattata come ACTIVE;
- nessuna fonte contenga payload text, content obytes;
- nessun path vietato venga indicizzato.

## Test futuri vietati in questa fase

Sono vietati test che:

- aprono contenuto integrale delle fonti;
- collegano il reader adapter a runtime;
- invocano TL Chat;
- invocano ATLAS Engine;
- invocano planner;
- creano endpoint;
- modificano SME, database o fonti reali.

## Verdetto

```text
VERDETTO: POLICY_DEFINED_DOCUMENTAL_ONLY
NEXT_ALLOWED_MOVE: ADD_DOCUMENTAL_POLICY_TEST
RUNTIME_BINDING_ALLOWED: FALSE
FULL_CONTENT_READING_ALLOWED: FALSE
```
