# INTAKE_DESTINATION_CLASSIFIER_CONTRACT_001

## Scopo

Il classificatore di destinazione intake riceve dati gia estratti da documenti,
immagini, input umano, import strutturati o conferme operative e restituisce una
decisione deterministica sulla sezione PROMETEO di destinazione.

La capability si ferma al risultato strutturato. Non persiste dati, non modifica
fonti e non decide pianificazione, quantita, turno o sequenziamento.

## Non Obiettivi

Il classificatore non:

- usa LLM;
- dipende dal renderer TL Chat;
- dipende dalla formulazione della domanda utente;
- scrive Article, Route, Components, Tools, QualityControls, Constraints o
  HumanConfirmations;
- fonde fonti;
- promuove dati a `CERTO`;
- inventa categorie mancanti;
- crea tabelle o repository.

## Modello Input

L'input scalare e tipizzato conserva almeno:

- `field_name`;
- `value`;
- `source_id`;
- `source_type`;
- `source_status`;
- `semantic_status`;
- `authority_role`;
- `document_section`;
- `document_label`;
- `context`;
- `metadata`.

Il classificatore non muta l'input, `context` o `metadata`.

## Modello Output

Il risultato contiene almeno:

- `ok`;
- `destination`;
- `classification_code`;
- `matched_rules`;
- `candidate_destinations`;
- `original_value`;
- `normalized_value`;
- `normalization_rules_applied`;
- `requires_review`;
- `review_reason`;
- `source_id`;
- `confidence`;
- `normalized_field_name`;
- `error_code`.

`confidence` usa stati deterministici, non probabilita:

- `DETERMINISTIC_MATCH`;
- `AMBIGUOUS_MATCH`;
- `UNCLASSIFIED`;
- `INVALID_INPUT`;
- `CONFLICTING_RULES`.

## Destinazioni Ammesse

Le destinazioni sono enum governati:

- `ARTICLE`;
- `ROUTE`;
- `COMPONENTS`;
- `TOOLS`;
- `QUALITY_CONTROLS`;
- `CONSTRAINTS`;
- `HUMAN_CONFIRMATIONS`.

Non esiste una destinazione generica `OTHER`. Un dato non classificabile produce
`destination=null`, `requires_review=true` e `classification_code=UNCLASSIFIED`.

## Priorita Delle Regole

| Priorita | Famiglia regola | Esempi |
| --- | --- | --- |
| 1 | input invalido | item non scalare, source mancante, ruolo non ammesso |
| 20 | conferma umana strutturata completa | autorita, soggetto, campo, valore, origine, audit |
| 25 | vincolo operativo forte | `VINCOLO`, `NON ESEGUIRE`, `RICHIEDE` |
| 30 | tipo entita dichiarato | `tooling`, `component`, `quality_control` |
| 35 | operazione di controllo qualita governata | collaudo, controllo dimensionale, prova tenuta |
| 40 | alias governato del campo | `operation`, `component_code`, `machine` |
| 50 | sezione o label documentale | OPERAZIONI, COMPONENTI, ATTREZZATURE |
| 60 | match lessicale forte | route nota, codice componente dichiarato |
| 70 | pattern lessicale debole | vincolo o tool da testo |
| 90 | ambiguita | operation/tool senza contesto sufficiente |
| 100 | non classificato | nessuna regola applicabile |

L'ordine e esplicito e non dipende dall'ordine casuale di dizionari.

## Regole Forti E Deboli

Le regole forti derivano da evidenza strutturata o vocabolari governati:
conferme umane, sezioni documentali, field alias, tipo dichiarato, match esatti.

Le regole deboli derivano da segnali lessicali. Una regola forte prevale su una
debole. Se due regole forti di pari priorita producono destinazioni diverse, il
classificatore non sceglie arbitrariamente e richiede review.

La qualita governata puo prevalere sul contesto `OPERAZIONI` per evitare di
classificare i collaudi come route ordinaria, ma non prevale su:

- `field_name=tool` o `type=tooling`;
- `field_name=component` o `type=component`;
- marker forti di vincolo operativo.

## Conferme Umane Strutturate

`HUMAN_CONFIRMATIONS` richiede una struttura minima completa:

- `authority_role` ammesso dal dominio condiviso;
- soggetto o articolo nel contesto;
- campo confermato;
- valore confermato;
- `confirmation_origin=HUMAN_EXPLICIT_CONFIRMATION`;
- `audit_note` o evidenza equivalente.

Il solo `source_type=human_operational_confirmation` non basta. Una conferma
umana incompleta produce review con
`classification_code=INCOMPLETE_HUMAN_CONFIRMATION`.

## Ambiguita

Esempio: `MACCHINA CRIMP RING ZAW`.

- se arriva da `OPERAZIONI`, destinazione primaria `ROUTE`;
- se `field_name=machine` o `type=tooling`, destinazione `TOOLS`;
- senza contesto sufficiente, `destination=null`,
  `classification_code=AMBIGUOUS_OPERATION_OR_TOOL`,
  `candidate_destinations=[ROUTE, TOOLS]`.

`COLLAUDO A PRESSIONE VERTICALE` come operazione viene destinato a
`QUALITY_CONTROLS`; eventuali relazioni future con `ROUTE` non implicano doppia
persistenza automatica.

## Conflitti

Se due regole forti con pari priorita confliggono:

- `destination=null`;
- `classification_code=CONFLICTING_RULES`;
- `requires_review=true`;
- `matched_rules` contiene entrambe;
- `candidate_destinations` conserva le destinazioni candidate.

## Normalizzazione

La normalizzazione e minima e separata dalla classificazione:

- trim;
- collasso spazi;
- casefold e underscore per `field_name`;
- alias governati;
- normalizzazioni operative confermate.

Il valore originale resta in `original_value`.

Regola operativa confermata:

`COLLAUDO A PRESSIONE`
->
`COLLAUDO A PRESSIONE VERTICALE`

Questa regola si applica solo al valore normalizzato per la decisione. Non muta
la fonte.

La regola vive nel modulo dominio condiviso
`backend/app/domain/operation_normalization.py`, riusato da classificatore e
rendering TL Chat.

I ruoli autoritativi vivono nel modulo dominio condiviso
`backend/app/domain/authority_roles.py`.

## Fonti Distinte

FONTI DISTINTE E NON FUSE.

Il classificatore conserva `source_id` in ogni risultato. Due item identici con
fonti diverse producono due risultati distinti. Il classificatore non deduplica,
non fonde e non sostituisce evidenze.

## Comportamento Batch

`classify_intake_items`:

- preserva l'ordine;
- restituisce un risultato per item;
- non si interrompe al primo errore;
- non deduplica;
- non fonde fonti.

Le liste non sono classificate come singolo elemento dalla funzione scalare:
producono `INVALID_SCALAR_INPUT`.

## Errori

Codici governati:

- `INVALID_INPUT`;
- `INVALID_SCALAR_INPUT`;
- `MISSING_SOURCE_ID`;
- `UNSUPPORTED_VALUE_TYPE`;
- `UNCLASSIFIED`;
- `AMBIGUOUS_MATCH`;
- `CONFLICTING_RULES`;
- `UNAUTHORIZED_AUTHORITY_ROLE`.
- `INCOMPLETE_HUMAN_CONFIRMATION`.

I casi operativi ordinari non usano eccezioni.

## Criteri Di Review

`requires_review=true` quando:

- input non valido;
- dato non classificabile;
- destinazione ambigua;
- regole forti confliggono;
- ruolo autoritativo non ammesso.

## Esempi

```json
{
  "field_name": "operation",
  "value": "COLLAUDO A PRESSIONE",
  "source_id": "spec_intake_preview:SYNTH01",
  "source_type": "spec_intake_preview",
  "source_status": "PREVIEW_ONLY",
  "semantic_status": "DA_VERIFICARE",
  "document_section": "OPERAZIONI"
}
```

Produce:

```json
{
  "destination": "QUALITY_CONTROLS",
  "classification_code": "OPERATION_QUALITY_CONTROL",
  "normalized_value": "COLLAUDO A PRESSIONE VERTICALE",
  "normalization_rules_applied": [
    "OPERATION_COLLAUDO_PRESSIONE_CONFIRMED_NORMALIZATION"
  ],
  "requires_review": false
}
```

```json
{
  "field_name": "note",
  "value": "MACCHINA CRIMP RING ZAW",
  "source_id": "doc:SYNTH02"
}
```

Produce una review ambigua tra `ROUTE` e `TOOLS`.

## Rapporto Con Il Futuro Servizio Di Collocazione

Un servizio successivo potra usare il risultato per decidere dove collocare o
persistere il dato. Questo contratto non autorizza la scrittura e non definisce
repository di destinazione.

## Divieto Di Uso LLM

Il classificatore e puro, locale e deterministico:

- nessuna rete;
- nessun database;
- nessun accesso disco per classificazione singola;
- nessun timestamp;
- nessun random;
- nessun LLM.
