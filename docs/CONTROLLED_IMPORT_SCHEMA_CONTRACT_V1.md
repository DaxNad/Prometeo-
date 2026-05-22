# CONTROLLED_IMPORT_SCHEMA_CONTRACT_V1

## SCOPO

Definire il contratto stabile dello schema input/output per
`CONTROLLED_IMPORT_PREVIEW_RUNTIME_V1`.

Questo gate non importa dati reali, non aggiunge endpoint e non abilita
scritture. Serve a impedire regressioni: ogni preview controllata deve
continuare a dichiarare chiaramente input minimo, output normalizzato, rischio,
conferma umana e assenza di side effect.

## INPUT_SCHEMA

Input ammesso per preview sintetica/sanificata:

- `order_id`: stringa non vuota;
- `article_code` o alias `codice`: stringa non vuota;
- `quantity` o alias `qta`: numero positivo o stringa convertibile;
- `due_date`: data ISO opzionale;
- `priority`: stringa opzionale;
- `station` o alias `postazione`: stringa opzionale;
- `route`: lista opzionale di postazioni;
- `note`: stringa opzionale sanificata;
- `source_type`: `synthetic`, `sanitized` o `demo`.

## OUTPUT_SCHEMA

Ogni risposta deve includere:

- `ok`;
- `capability`;
- `write_mode`;
- `preview_only`;
- `required_human_confirmation`;
- `risk_level`;
- `risk_allowed_values`;
- `errors`;
- `warnings`;
- `preview`;
- `side_effects`.

## PREVIEW_SCHEMA

La sezione `preview` deve includere quando disponibile:

- `order_id`;
- `article_code`;
- `quantity`;
- `due_date`;
- `priority`;
- `route`;
- `station`;
- `note`;
- `source_type`.

Se il record e bloccato per input sensibile o payload non valido, `preview`
puo essere vuoto.

## SIDE_EFFECTS_SCHEMA

La sezione `side_effects` deve includere sempre:

- `db_write`;
- `smf_write`;
- `planner_update`;
- `file_write`;
- `external_call`;
- `ocr`;
- `ai_runtime`.

Tutti questi valori devono essere `false` in questa capability.

## REQUIRED_FIELDS

I campi minimi richiesti sono:

- `order_id`;
- `article_code`;
- `quantity`.

La mancanza di uno di questi campi deve produrre errore esplicito
`missing_required_field:<field>` e rischio `BLOCKED`.

## RISK_LEVELS

I valori ammessi per `risk_level` sono:

- `LOW`;
- `MEDIUM`;
- `HIGH`;
- `BLOCKED`.

`risk_allowed_values` deve riportare lo stesso insieme di valori.

## WRITE_MODE

`write_mode` deve essere sempre:

```text
PREVIEW_ONLY
```

Qualunque valore diverso rompe il contratto.

## HUMAN_CONFIRMATION

`required_human_confirmation` deve essere sempre `true`.

La preview non autorizza apply, import reale, scritture SMF, scritture DB o
mutazioni planner.

## NO_SIDE_EFFECTS

Il contratto vieta:

- connessioni DB;
- scritture SMF;
- scritture file dati;
- aggiornamenti planner;
- chiamate esterne;
- OCR reale;
- AI runtime.

## TEST_DI_CONTRATTO

Comandi minimi:

```bash
bash scripts/controlled_import_schema_contract_v1_check.sh
python3 -m pytest -s backend/tests/test_controlled_import_schema_contract.py -q
make controlled-import-schema-contract-v1
```

## FAILURE_MODES

Il gate fallisce se:

- manca questo documento;
- manca un marker obbligatorio;
- manca il target Makefile;
- lo schema output perde chiavi obbligatorie;
- `write_mode` non e `PREVIEW_ONLY`;
- `required_human_confirmation` non e `true`;
- `side_effects` contiene valori `true`;
- `risk_level` esce dai valori ammessi.

## PROSSIMO_PASSO

Dopo questo contratto, il prossimo micro-passo puo essere un endpoint preview
dedicato solo a payload sintetici/sanificati, da autorizzare separatamente.
