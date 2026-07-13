# PROMETEO — INTERACTION PREFLIGHT

## Scopo

Protocollo permanente per avviare attività di analisi, sviluppo, revisione o chiusura su PROMETEO senza dipendere dalla cronologia della chat o da uno specifico modello.

## Principi vincolanti

1. Il repository e i contratti canonici prevalgono sulla conversazione.
2. Nessun file, simbolo, campo, route o stato può essere assunto senza verifica.
3. Ogni avvio distingue:
   - `OBSERVED`: verificato direttamente;
   - `INFERRED`: dedotto da prove osservate;
   - `DECIDED`: autorizzato da fonte canonica o decisione umana esplicita;
   - `UNKNOWN`: non verificato.
4. Una capability alla volta.
5. La consegna minima verificabile prevale sull'espansione architetturale.
6. I dati industriali reali, le credenziali e i file sensibili restano fuori dai modelli cloud e dal repository.
7. Nessun modello possiede autorità autonoma di dominio, runtime o merge.

## Pacchetto minimo di avvio

Prima di proporre modifiche, raccogliere soltanto:

- branch e commit osservati;
- stato del worktree;
- fonte di verità applicabile;
- capability attiva o task richiesto;
- file ammessi;
- file vietati;
- tipo di azione: lettura, test, patch, review o chiusura;
- criterio di accettazione;
- stop condition.

Non importare automaticamente l'intera conversazione o documentazione non necessaria.

## Gate di autorizzazione

### Lettura e mappatura

Consentite quando il perimetro è chiaro e non comportano mutazioni.

### Patch

Richiede:

- scope esplicito;
- file autorizzati;
- contratto letto;
- test o verifica definiti;
- assenza di blocker non risolti.

### Modifiche materiali

Richiedono decisione umana esplicita quando cambiano:

- accesso runtime;
- campi o fonti autorizzate;
- stato semantico;
- planner eligibility;
- promozione automatica;
- scritture o persistenza;
- regole di dominio;
- privacy o sicurezza.

## Metodo operativo

1. Verificare il perimetro.
2. Leggere le fonti canoniche pertinenti.
3. Bloccare le assunzioni.
4. Cercare scope creep e capability concorrenti.
5. Consegnare la slice verticale minima.
6. Eseguire test e guard applicabili.
7. Analizzare il diff completo.
8. Fermarsi su failure, divergenza, file inattesi o cambio di scope.
9. Chiudere con:
   - risultato;
   - prove;
   - limiti residui;
   - una sola `NEXT_MOVE`.

## Stop condition

Interrompere senza workaround quando si verifica almeno una condizione:

- fonte di verità assente o contraddittoria;
- necessità di modificare file vietati;
- diff inatteso;
- test o guard non verdi;
- divergenza Git;
- richiesta di dati sensibili;
- autorizzazione insufficiente;
- seconda capability necessaria.

## Formato minimo di chiusura

```text
CAPABILITY:
FILES_READ:
FILES_CHANGED:
TESTS:
GUARDS:
RUNTIME_IMPACT:
RISKS:
VERDICT:
NEXT_MOVE:
```

`NEXT_MOVE` contiene una sola azione e non apre automaticamente una nuova capability.
