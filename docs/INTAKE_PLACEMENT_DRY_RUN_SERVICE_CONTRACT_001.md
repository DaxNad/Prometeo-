# INTAKE_PLACEMENT_DRY_RUN_SERVICE_CONTRACT_001

## Scopo

Il servizio di collocazione intake dry-run riceve un `IntakeItem` gia
classificato e il relativo `IntakeClassificationResult`, poi produce un piano
strutturato di collocazione verso il dominio PROMETEO.

Il servizio non scrive e non chiama writer.

## Non Obiettivi

Il servizio non:

- ricalcola la classificazione;
- persiste dati;
- crea tabelle o repository;
- integra upload, OCR, TL Chat, Board o API;
- promuove dati a `CERTO`;
- fonde fonti;
- deduce autorita;
- usa LLM.

## Relazione Con Il Classificatore

Il classificatore decide la destinazione. Il dry-run verifica precondizioni,
target e policy fonte. Una classificazione con `requires_review=true` non viene
collocata e produce `REVIEW_REQUIRED`.

## Modello Request

```python
@dataclass(frozen=True)
class IntakePlacementDryRunRequest:
    item: IntakeItem
    classification: IntakeClassificationResult
    requested_by_role: str | None = None
    dry_run: bool = True
```

`dry_run` deve essere `True`.

## Modello Result

Il risultato espone:

- `ok`;
- `status`;
- `destination`;
- `domain_entity`;
- `target_repository`;
- `target_service`;
- `target_section`;
- `operation`;
- `payload_preview`;
- `required_fields`;
- `missing_fields`;
- `blocking_reasons`;
- `warnings`;
- `matched_rules`;
- `source_id`;
- `source_status`;
- `semantic_status`;
- `authority_role`;
- `ready_for_persistence`;
- `requires_review`;
- `review_reason`;
- `error_code`.

Il risultato e immutabile e deterministico.

## Stati Dry-Run

- `READY`;
- `REVIEW_REQUIRED`;
- `BLOCKED`;
- `UNSUPPORTED_DESTINATION`;
- `TARGET_NOT_AVAILABLE`;
- `INVALID_PLACEMENT_REQUEST`;
- `SOURCE_NOT_AUTHORIZED`;
- `AUTHORITY_REQUIRED`;
- `MISSING_REQUIRED_FIELDS`.

## Operazioni Proposte

- `CREATE`;
- `UPDATE`;
- `APPEND`;
- `LINK`;
- `NO_OP`;
- `NOT_AVAILABLE`.

## Semantica APPEND Per Le Conferme Umane

Per `HUMAN_CONFIRMATIONS` con target service
`confirm_article_operational_status`, il dry-run usa `operation=APPEND` per
indicare la sottoposizione di una nuova conferma governata.

Il dry-run non decide se la persistenza produrra:

- creazione;
- aggiornamento;
- no-op idempotente.

Questa decisione appartiene al writer, che verifica lo stato corrente del
registry durante la transazione.

`APPEND` non autorizza una scrittura diretta, non implica duplicazione della
history e non indica che il record esista gia.

## Target Descriptor

Ogni destinazione ha un descriptor governato con:

- destinazione;
- entita dominio;
- repository logico;
- servizio target, se esiste;
- sezione target;
- campi richiesti;
- source policy;
- authority policy;
- audit policy.

I descriptor sono statici e immutabili.

## Mapping Destinazioni

| Destinazione | Entita dominio | Repository fisico | Sezione logica | Servizio |
| --- | --- | --- | --- | --- |
| `ARTICLE` | `Article` | nessuno | `article_metadata` | nessuno |
| `ROUTE` | `Route` | nessuno | `route_step` | nessuno |
| `COMPONENTS` | `ArticleComponentRelation` | nessuno | `bom_component` | nessuno |
| `TOOLS` | `ToolRequirement` | nessuno | `tooling_requirement` | nessuno |
| `QUALITY_CONTROLS` | `QualityControlRequirement` | nessuno | `quality_control` | nessuno |
| `CONSTRAINTS` | `OperationalConstraint` | nessuno | `constraint` | nessuno |
| `HUMAN_CONFIRMATIONS` | `HumanOperationalConfirmation` | `article_operational_registry` | `operational_status` | `confirm_article_operational_status` solo per stato operativo articolo |

Per target senza writer governato, il dry-run restituisce
`TARGET_NOT_AVAILABLE` quando le precondizioni sono altrimenti complete.

I nomi delle sezioni logiche non sono repository tecnici disponibili. Quando
non esiste un writer governato, `target_repository` resta `None`.

## Semantica Del Ramo ARTICLE

Il ramo `ARTICLE` del dry-run non distingue `CREATE`, `UPDATE` o `NO_OP`.

La presenza dell'article id identifica il soggetto del dato, ma non dimostra che
il record anagrafico esista gia. L'assenza dell'article id non dimostra che un
nuovo record debba essere creato.

Per dati `ARTICLE` strutturalmente completi:

- `status=TARGET_NOT_AVAILABLE`;
- `operation=NOT_AVAILABLE`;
- `ready_for_persistence=false`;
- `target_repository=None`;
- `target_service=None`;
- `target_section=article_metadata`.

Il payload preview resta disponibile per review e per un futuro writer
governato. Il dry-run non autorizza upsert impliciti e non include campi come
`create_if_missing`, `update_existing`, `upsert`, `inferred_exists` o
`inferred_missing`.

Una futura capability potra introdurre reader e writer governati per Article;
fino ad allora `article_metadata` resta una sezione logica, non un repository
fisico.

## Precondizioni

Ogni piano richiede:

- coerenza `classification.source_id == item.source_id`;
- source id presente;
- classification `ok=True`;
- destination presente;
- assenza di conflitti o ambiguita;
- campi minimi del target;
- fonte autorizzata;
- ruolo autoritativo ammesso quando richiesto.

## Policy Fonti

- `PREVIEW_ONLY`: puo produrre piano, ma richiede review e non e ready.
- `DA_VERIFICARE`: richiede review.
- `CERTO`: puo arrivare a `READY` solo se esiste writer governato.
- `SOURCE_MISSING`: `BLOCKED`.
- `SOURCE_FORBIDDEN`: `SOURCE_NOT_AUTHORIZED`.
- `SOURCE_AUTHORIZED_BUT_UNAVAILABLE`: `BLOCKED`.
- `HUMAN_EXPLICIT_CONFIRMATION`: richiede authority valida e servizio governato.

## READY Vs CERTO

`READY` non significa `CERTO`.

`READY` significa solo che il piano e strutturalmente completo e potrebbe essere
passato a un writer governato esistente. Il dry-run non promuove confidence,
semantic status o source status.

TARGET INDIVIDUATO non significa `READY`. Se un servizio target e noto ma il
payload non contiene tutti gli argomenti obbligatori della firma, il risultato
deve essere `MISSING_REQUIRED_FIELDS` o `INVALID_PLACEMENT_REQUEST`.

## Payload Preview

Il payload preview e minimo e strutturato. Deve preservare:

- valore originale;
- valore normalizzato;
- regole di normalizzazione;
- source id;
- source status;
- semantic status.

Per i target con writer governato il payload distingue:

- `writer_arguments`: solo argomenti accettati dalla firma del writer;
- `source_evidence`: metadati di fonte, regole e tracciabilita.

`source_id`, `source_status`, `semantic_status` e `matched_rules` sono evidence,
non argomenti del writer `confirm_article_operational_status`.

Esempio quality:

```json
{
  "article": "SYNTH01",
  "control_name": "COLLAUDO A PRESSIONE VERTICALE",
  "source_value": "COLLAUDO A PRESSIONE",
  "normalization_rules_applied": [
    "OPERATION_COLLAUDO_PRESSIONE_CONFIRMED_NORMALIZATION"
  ],
  "source_id": "spec_intake_preview:SYNTH01",
  "source_status": "PREVIEW_ONLY",
  "semantic_status": "DA_VERIFICARE"
}
```

## Fonti Distinte

FONTI DISTINTE E NON FUSE.

Il batch restituisce un risultato per richiesta, preserva ordine e source id, non
deduplica e non aggrega route, componenti o evidenze.

## Review E Blocking

Review obbligatoria per:

- classificazione gia in review;
- preview o dati `DA_VERIFICARE`;
- constraint senza subject;
- conferme umane incomplete.

Blocking per:

- fonte mancante;
- fonte autorizzata ma non disponibile;
- fonte vietata;
- richiesta non dry-run.

## Batch

`plan_intake_placements`:

- preserva ordine;
- non si interrompe al primo errore;
- non deduplica;
- non fonde fonti;
- non costruisce route aggregate.

## Error Codes

- `INVALID_PLACEMENT_REQUEST`;
- `DRY_RUN_REQUIRED`;
- `CLASSIFICATION_SOURCE_MISMATCH`;
- `CLASSIFICATION_VALUE_MISMATCH`;
- `CLASSIFICATION_NOT_READY`;
- `DESTINATION_MISSING`;
- `UNSUPPORTED_DESTINATION`;
- `TARGET_NOT_AVAILABLE`;
- `MISSING_REQUIRED_FIELDS`;
- `SOURCE_NOT_AUTHORIZED`;
- `AUTHORITY_REQUIRED`;
- `INVALID_PAYLOAD_PREVIEW`.

## Assenza Assoluta Di Scritture

Il servizio non deve:

- aprire file in scrittura;
- chiamare `write_text`;
- chiamare `json.dump`;
- chiamare `replace`;
- chiamare servizi writer;
- invalidare cache;
- generare timestamp;
- creare directory;
- modificare environment.

## Rapporto Con Futuri Writer

Un futuro writer potra consumare il piano dry-run solo dopo review del contratto
del target. Questa capability non abilita la persistenza.

## Esempi Completi

### Quality Preview

Input classificato: `QUALITY_CONTROLS`, source `PREVIEW_ONLY`.

Output: payload preview disponibile, `status=REVIEW_REQUIRED`,
`ready_for_persistence=false`.

### Operational Human Confirmation

Input classificato: `HUMAN_CONFIRMATIONS`, campo `operational_class`, ruolo
`RESPONSABILE_PRODUZIONE`, origine `HUMAN_EXPLICIT_CONFIRMATION`.

Output: target service `confirm_article_operational_status`, `status=READY` se
fonte, semantica e payload sono compatibili.

Operazione proposta: `APPEND`. Il writer determinera atomicamente se la
conferma produce creazione, aggiornamento o no-op idempotente.

Campi obbligatori per `confirm_article_operational_status`:

- `article`;
- `operational_class`;
- `planner_eligible`;
- `tl_confirmation_required`;
- `authority_role`;
- `audit_note`;
- `confirmation_origin`.

`planner_eligible` e `tl_confirmation_required` devono essere booleani reali.
Non vengono derivati da `operational_class` e non accettano stringhe come
`"true"` o `"false"`.

Esempio:

```json
{
  "writer_arguments": {
    "article": "SYNTH01",
    "operational_class": "STANDARD",
    "planner_eligible": true,
    "tl_confirmation_required": false,
    "authority_role": "RESPONSABILE_PRODUZIONE",
    "audit_note": "Conferma operativa esplicita.",
    "confirmation_origin": "HUMAN_EXPLICIT_CONFIRMATION",
    "confirmed_at": null,
    "material": null,
    "drawing": null,
    "description": null
  },
  "source_evidence": {
    "source_id": "human:SYNTH",
    "source_status": "SOURCE_FOUND",
    "semantic_status": "CERTO"
  }
}
```
