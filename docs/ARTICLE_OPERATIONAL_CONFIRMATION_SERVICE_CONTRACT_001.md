# ARTICLE_OPERATIONAL_CONFIRMATION_SERVICE_CONTRACT_001

## Scopo

Persistenza governata di una conferma operativa umana sullo stato corrente di
un articolo nel registry esistente:

`data/local_smf/finiture/article_operational_registry.json`

La conferma operativa resta distinta da fonti documentali, preview e
`spec_intake_confirmation`.

## Autorità Ammessa

Autorità interna ammessa:

`RESPONSABILE_PRODUZIONE`

Il testo user-facing "responsabile di produzione" resta separato dal valore
interno governato.

## Input Minimo

```json
{
  "article": "12514",
  "operational_class": "STANDARD",
  "planner_eligible": true,
  "tl_confirmation_required": false,
  "authority_role": "RESPONSABILE_PRODUZIONE",
  "confirmation_origin": "HUMAN_EXPLICIT_CONFIRMATION",
  "confirmed_at": "...",
  "material": "...",
  "drawing": "...",
  "description": "...",
  "audit_note": "..."
}
```

`material`, `drawing`, `description` e `confirmed_at` sono opzionali.

## Output Minimo

Il servizio restituisce un risultato strutturato con:

- `ok`;
- `article`;
- `created`;
- `updated`;
- `previous_record`;
- `current_record`;
- `registry_path`;
- `confirmed_at`;
- `error_code`.

Il servizio non espone dettagli tecnici nella TL Chat: è una capability di
dominio/infrastruttura.

## Regole Di Validazione

- `article` obbligatorio e non vuoto;
- `operational_class` deve appartenere alle classi ammesse dal dominio;
- `planner_eligible` deve essere booleano;
- `tl_confirmation_required` deve essere booleano esplicito;
- `authority_role` deve essere `RESPONSABILE_PRODUZIONE`;
- `confirmation_origin` deve essere `HUMAN_EXPLICIT_CONFIRMATION`;
- `confirmed_at`, se presente, deve essere ISO-8601;
- `audit_note` è obbligatoria per cambi di stato significativi;
- nessuna promozione implicita da preview;
- nessuna derivazione automatica di `STANDARD`;
- il servizio non accetta campi arbitrari in input;
- i campi già presenti nel record esistente vengono preservati per evitare
  perdita di dati;
- i campi preservati non diventano automaticamente governati dal nuovo
  contratto;
- nessuna cancellazione delle evidenze precedenti.

## Semantica Di `planner_eligible`

`planner_eligible=true` significa che l'articolo può essere considerato dal
planner quando esistono tutti gli altri ingressi validi.

Non significa:

- ordine autorizzato;
- quantità autorizzata;
- turno autorizzato;
- sequenziamento autorizzato;
- avvio automatico della produzione.

## Aggiornamento Di Un Record Esistente

## Idempotenza Sostanziale

L'idempotenza è calcolata sui campi sostanziali della conferma:

- articolo;
- `operational_class`;
- `planner_eligible`;
- `tl_confirmation_required`;
- `authority_role`;
- `confirmation_origin`;
- campi opzionali effettivamente forniti: `material`, `drawing`,
  `description`.

`confirmed_at` generato dal servizio e `audit_note` non rendono da soli una
conferma una nuova variazione operativa.

Se tutti i campi sostanziali sono invariati:

- `ok=true`;
- `created=false`;
- `updated=false`;
- `persisted=false`;
- il file non viene riscritto;
- `updated_at` resta invariato;
- `confirmed_at` corrente resta invariato;
- `audit_note` corrente resta invariata;
- non viene aggiunta history;
- la cache non viene invalidata.

Per ora una `audit_note` differente, a parità di stato operativo, viene trattata
come no-op. Una futura capability potrà introdurre una conferma audit-only
esplicita.

## Confirmation History

Stesso valore e stessa autorità:

- operazione idempotente;
- nessuna duplicazione;
- risultato `updated=false`.

Valore differente:

- `previous_record` viene restituito nel risultato;
- il record corrente viene aggiornato;
- `audit_note` è obbligatoria;
- timestamp e autorità vengono registrati;
- nessuna sovrascrittura silenziosa.

Quando un aggiornamento modifica significativamente un record esistente, il
servizio conserva lo stato precedente in `confirmation_history`.

Ogni voce storica conserva, quando presenti:

- `operational_class`;
- `planner_eligible`;
- `tl_confirmation_required`;
- `source`;
- `source_authority`;
- `authority_role`;
- `confirmation_origin`;
- `confirmed_at`;
- `audit_note`;
- `material`;
- `drawing`;
- `description`;
- `superseded_at`;
- `superseded_by_authority`.

La history:

- è ordinata cronologicamente per append;
- non viene annidata dentro le singole voci;
- non viene aggiornata per no-op;
- non viene aggiornata per nuove creazioni;
- non è fonte operativa corrente;
- serve solo ad audit e ricostruzione.

Autorità non ammessa:

- rifiuto esplicito;
- nessuna scrittura.

## `tl_confirmation_required` Esplicito

Il writer non deriva `tl_confirmation_required` da `operational_class`.

Il chiamante deve passare un booleano esplicito. Il valore viene incluso nel
confronto sostanziale e nella history.

## Persistenza

La scrittura deve essere atomica:

- file temporaneo nella stessa directory;
- flush;
- sostituzione atomica;
- nessun file parzialmente scritto.

Dopo scrittura riuscita:

- la cache del registry operativo viene invalidata;
- il record viene riletto tramite il loader dominio esistente;
- il dato diventa disponibile al resolver TL Chat tramite
  `build_article_tl_summary`.

## Scrittura Riuscita Con Readback Fallito

Se la scrittura atomica riesce ma il readback dominio fallisce:

- il file può essere già stato aggiornato;
- il servizio restituisce `ok=false`;
- `error_code=WRITE_SUCCEEDED_READBACK_FAILED`;
- `persisted=true`;
- `current_record` contiene il record previsto;
- non viene tentata una seconda scrittura automatica;
- non viene cancellato il nuovo contenuto;
- è richiesta verifica manuale del readback.

`persisted` ha questa semantica:

- errore validazione: `false`;
- errore scrittura: `false`;
- scrittura riuscita e readback riuscito: `true`;
- scrittura riuscita e readback fallito: `true`.

## Retrocompatibilità Record Legacy

Per record esistenti:

- history assente equivale a lista vuota;
- campi legacy come `source_authority` vengono preservati nella history;
- `authority_role` governato viene scritto solo quando arriva una nuova
  conferma;
- non avviene alcuna migrazione globale al solo caricamento.

## Fonti Distinte

Il servizio non modifica:

- preview;
- `spec_intake_confirmation`;
- lifecycle registry;
- frontend;
- endpoint TL Chat;
- renderer;
- CORS.
