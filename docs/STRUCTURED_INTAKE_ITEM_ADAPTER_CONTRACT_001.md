# STRUCTURED_INTAKE_ITEM_ADAPTER_CONTRACT_001

## Scopo

Trasformare un singolo payload strutturato in un `IntakeItem` valido, senza classificare, pianificare o persistere.

## Ingresso

Un solo mapping con i campi ammessi:

- `field_name`
- `value`
- `source_id`
- `source_type`
- `source_status`
- `semantic_status`
- `authority_role`
- `document_section`
- `document_label`
- `context`
- `metadata`

Campi top-level sconosciuti devono essere rifiutati.

## Validazioni minime

- payload di tipo mapping;
- `field_name` non vuoto;
- `source_id` non vuoto;
- `context` mapping oppure `None`;
- `metadata` mapping oppure `None`.

Il campo `value` può legittimamente contenere:

- stringa vuota;
- `False`;
- `0`;
- mapping;
- altri valori supportati dal classificatore.

## Risultato

Il risultato tipizzato deve contenere:

- `ok`;
- stato `BUILT` oppure `REJECTED`;
- `IntakeItem` costruito oppure `None`;
- `error_code`.

## Regole di sicurezza

- nessuna classificazione;
- nessun dry-run;
- nessuna esecuzione;
- nessun writer;
- nessun orchestratore;
- nessun batch;
- nessun accesso a file;
- nessuna rete;
- nessuna API;
- nessun hardcode articolo;
- nessuna mutazione del payload originale;
- copia separata di `value`, `context` e `metadata`.

## Errori

- `INVALID_PAYLOAD`
- `MISSING_FIELD_NAME`
- `MISSING_SOURCE_ID`

## Collegamento autorizzato futuro

L’adapter può fornire un `IntakeItem` a:

`orchestrate_intake_item(item)`

ma questa capability non effettua il collegamento automaticamente.
