# PROMETEO_SMALLEST_VERIFIABLE_VERTICAL_SLICE_PROMPT_001

## Stato

- `STATUS`: `EXPORTED_AND_SANITIZED`
- `SOURCE_CAPABILITY`: `PROMETEO_ATLAS_DATA_EXPORT_AND_INVENTORY_001`
- `SOURCE_CATEGORY`: `prompt_canonici`
- `ITEM_ID`: `ATLAS_PROMPT_001`
- `CLASSIFICATION`: `EXPORTABLE_SANITIZED`
- `SANITIZATION_REQUIRED`: `true`
- `DESTINATION`: `repository`
- `VERIFICATION_STATUS`: `SANITIZED`
- `RUNTIME_AUTHORIZED`: `false`

## Scopo

Versionare un solo prompt operativo Prometeo, ricavato dalle conversazioni Atlas, utile a mantenere un metodo di sviluppo robusto e deterministico anche fuori da Atlas.

Questo artefatto non è una copia integrale di una conversazione. Contiene soltanto la regola operativa stabile, priva di dati personali, credenziali, percorsi locali, dati aziendali o riferimenti a sessioni autenticate.

## Inventario minimo dei candidati

| Candidato | Descrizione | Classificazione | Decisione |
|---|---|---|---|
| Preflight deterministico | verifica perimetro, fonte di verità e assunzioni | `EXPORTABLE_SANITIZED` | `DEFER` — già distribuito in più documenti e regole repository |
| Mappatura minima | leggere solo ciò che serve prima di autorizzare una modifica | `EXPORTABLE_SANITIZED` | `DEFER` — da consolidare in una slice successiva |
| Test-first | test mirato rosso prima della patch runtime minima | `EXPORTABLE_PUBLIC` | `DEFER` — già prescritto da `AGENTS.md` |
| Chiusura capability | evidenze, limiti, impatti e una sola prossima mossa | `EXPORTABLE_SANITIZED` | `DEFER` — richiede confronto con i documenti closure esistenti |
| Più piccola slice verticale verificabile | privilegiare una consegna concreta rispetto a ulteriore analisi non necessaria | `EXPORTABLE_SANITIZED` | `SELECTED` |

## Registrazione obbligatoria degli elementi

| `item_id` | `source_category` | `source_description` | `business_need` | `classification` | `sanitization_required` | `destination` | `verification_status` | `verified_by` | `verified_at` | `notes` |
|---|---|---|---|---|---|---|---|---|---|---|
| `ATLAS_PROMPT_CANDIDATE_001` | `prompt_canonici` | Preflight deterministico | Preservare il controllo di perimetro, fonti e assunzioni | `EXPORTABLE_SANITIZED` | `true` | `reference-only` | `REVIEWED` | `repository_operator` | `2026-07-22` | `DEFER`: già distribuito in documenti e regole repository |
| `ATLAS_PROMPT_CANDIDATE_002` | `prompt_canonici` | Mappatura minima | Preservare la lettura minima prima di autorizzare modifiche | `EXPORTABLE_SANITIZED` | `true` | `reference-only` | `REVIEWED` | `repository_operator` | `2026-07-22` | `DEFER`: consolidamento rinviato |
| `ATLAS_PROMPT_CANDIDATE_003` | `prompt_canonici` | Test-first | Preservare il ciclo test rosso e patch runtime minima | `EXPORTABLE_PUBLIC` | `false` | `reference-only` | `REVIEWED` | `repository_operator` | `2026-07-22` | `DEFER`: già prescritto da AGENTS.md |
| `ATLAS_PROMPT_CANDIDATE_004` | `prompt_canonici` | Chiusura capability | Preservare evidenze, limiti, impatti e prossima mossa | `EXPORTABLE_SANITIZED` | `true` | `reference-only` | `REVIEWED` | `repository_operator` | `2026-07-22` | `DEFER`: richiede confronto con closure esistenti |
| `ATLAS_PROMPT_001` | `prompt_canonici` | Più piccola slice verticale verificabile | Preservare il metodo operativo minimo, concreto e verificabile fuori da Atlas | `EXPORTABLE_SANITIZED` | `true` | `repository` | `SANITIZED` | `repository_operator` | `2026-07-22` | `SELECTED` ed esportato come artefatto testuale |

## Motivazione della selezione

Il prompt selezionato:

- è ricorrente e stabile nelle conversazioni Prometeo;
- non contiene dati sensibili;
- è applicabile a documentazione, test e runtime;
- limita esplicitamente l'espansione dello scope;
- produce un criterio di completamento verificabile;
- è comprensibile e utilizzabile senza accesso ad Atlas.

## Prompt canonico sanitizzato

```text
Lavora con metodo robusto e deterministico.

1. Esegui un preflight minimo:
   - identifica la capability;
   - definisci uno scopo verificabile;
   - dichiara file, moduli e azioni ammessi;
   - dichiara limiti e stop conditions;
   - verifica la fonte di verità prima di assumere nomi, percorsi o contratti.

2. Esegui solo la mappatura necessaria a individuare il percorso minimo reale.

3. Dopo preflight e mappatura minima, privilegia sempre la più piccola slice verticale concreta e verificabile.

4. Non estendere analisi, cataloghi o architettura quando esiste già un percorso minimo per consegnare valore operativo.

5. Ogni task deve produrre:
   - una slice verticale concreta;
   - un criterio di accettazione verificabile;
   - un limite di scope esplicito;
   - una sola prossima mossa.

6. Per modifiche runtime:
   - aggiungi prima un test mirato rosso;
   - applica la patch minima;
   - esegui regressioni e guard obbligatori;
   - fermati su diff inatteso, failure reale o cambio di scope.

7. Non dichiarare completata o chiusa una capability senza evidenze osservabili.
```

## Pipeline canonica

```text
PRECHECK
→ MAPPATURA MINIMA
→ SCELTA DELLA PIÙ PICCOLA VERTICAL SLICE
→ TEST MIRATO QUANDO RUNTIME
→ IMPLEMENTAZIONE MINIMA
→ VERIFICA DI ACCETTAZIONE
→ LIMITI ED EVIDENZE
→ UNA SOLA PROSSIMA MOSSA
```

## Regole d'uso

Il prompt deve essere adattato alla capability concreta specificando sempre:

- obiettivo;
- baseline;
- fonte primaria;
- allowlist;
- denylist;
- modalità autorizzata: lettura, test, patch o closure;
- criterio di accettazione;
- stop conditions.

Il prompt non sostituisce:

- `AGENTS.md`;
- il Manifesto architetturale;
- i contratti della capability;
- i guard privacy e data leak;
- la verifica del repository reale.

In caso di conflitto prevalgono le fonti repository più autorevoli.

## Sanitizzazione applicata

Sono stati rimossi o generalizzati:

- nomi personali;
- riferimenti aziendali;
- articoli, ordini e dati di produzione;
- percorsi locali reali;
- token, password, cookie e credenziali;
- riferimenti a sessioni o account;
- dettagli contingenti di singole capability.

Non sono presenti file binari, screenshot, dump di chat o cronologia completa.

## Criterio di accettazione della slice

La prima slice è soddisfatta quando:

1. una sola categoria Atlas è stata mappata;
2. i candidati sono stati inventariati e classificati;
3. un solo prompt non sensibile è stato selezionato;
4. il prompt è stato sanitizzato e versionato;
5. l'artefatto è comprensibile senza Atlas;
6. `Privacy Guard` e `Data Leak Guard` risultano verdi prima del merge;
7. nessun runtime è stato modificato.

## Limiti

Questa slice non autorizza:

- esportazione massiva di prompt o conversazioni;
- archiviazione completa delle chat;
- scraping autenticato;
- modifica di backend, frontend, planner, registry o TL Chat;
- modifica dei guard;
- chiusura dell'intera capability `PROMETEO_ATLAS_DATA_EXPORT_AND_INVENTORY_001`.

## Impatto architetturale

- Modello `Order -> ProductionEvent -> Station/Phase`: invariato.
- Planner: nessun impatto.
- Registry semantico: nessun impatto.
- Backend dominio: nessun impatto.
- Review architetturale: non necessaria.

## Esito

`FIRST_CANONICAL_PROMPT_EXPORT_READY_FOR_GUARDS`

## Prossima mossa

Eseguire nel checkout locale:

```bash
./tools/py scripts/privacy_guard_specs.py
./tools/py scripts/data_leak_guard.py
git status --short
git diff --cached --stat
```

La PR deve restare draft fino all'esito verde dei guard.