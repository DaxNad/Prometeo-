# PROMETEO_AGENT_OPERATING_MODEL

Fonte primaria: `docs/PROMETEO_MASTER.md`.

Questo documento e governance operativa per lo sviluppo PROMETEO. Non e un
orchestratore runtime, non abilita agenti autonomi e non modifica backend,
frontend, planner, SMF o dati reali.

## 1. Scopo

Definire una squadra di agenti specializzati, governati e verificabili per
sviluppo, hardening e chiusura capability PROMETEO.

Gli agenti descritti qui sono ruoli operativi assegnabili a persone, LLM o
strumenti assistivi sotto controllo umano. Ogni agente deve lavorare su una
capability alla volta, con scope dichiarato, file ammessi, file vietati, test
minimi e verdict finale.

## 2. Principio base

Gli agenti PROMETEO sono ruoli governati, non autonomi.

Un agente puo:

- leggere fonti autorizzate;
- proporre piani minimi;
- produrre patch solo se lo scope lo consente;
- produrre test, eval, report e checklist;
- segnalare rischi, conflitti e blocchi.

Un agente non puo:

- decidere al posto del TL;
- applicare modifiche operative senza preview, conferma e audit;
- usare AI come fonte autorevole;
- leggere o modificare dati reali vietati;
- creare architetture parallele;
- introdurre agenti runtime autonomi.

## 3. Ruoli agenti

### System Mapper Agent

Mantiene la mappa del sistema, lo stato capability, i confini architetturali e
la relazione tra documenti, backend, frontend, planner, ATLAS Engine, TL Chat,
eval e guardrail.

Output tipico: stato capability, gap, file ownership, impatto, proposta di
prossimo passo minimo.

### Domain Guard Agent

Verifica che ogni proposta rispetti gli invarianti dominio e la gerarchia delle
fonti.

Controlli minimi:

- `ZAW1` e `ZAW2` non sono intercambiabili;
- `ZAW1_2` non e `ZAW2`;
- `HENN` precede `ZAW` quando presente con fonte confermata;
- `CP` finale resta obbligatorio quando richiesto;
- `COLLAUDO_VERTICALE` e modalita CP, non stazione autonoma;
- nessuna route viene inferita senza evidenza.

### Retrieval Evidence Agent

Lavora sul recupero fonti autorizzate e sulla forma evidence pack.

Deve rispettare `GOVERNED_RETRIEVAL_001`: read-only, local-only, no LLM calls,
no DB writes, no SMF writes, no planner mutation, no runtime mutation, no
accesso a immagini `specs_finitura`.

### Conflict Detection Agent

Identifica conflitti tra fonti, route, stazioni, componenti condivisi,
confidence, eventi e vincoli planner.

Non risolve automaticamente il conflitto. Produce classificazione, evidenza,
rischio e domanda TL quando serve.

### Test Eval Agent

Costruisce e mantiene test contract, eval sintetici, micro-campioni sanificati e
guard di regressione.

Non introduce logica di dominio nuova. Se un test richiede una nuova regola,
deve rimandare a `PROMETEO_MASTER.md` o chiedere conferma TL.

### Backend Capability Agent

Chiude una capability backend alla volta con patch minima e test dedicati.

Ambiti ammessi solo quando esplicitamente autorizzati: API, domain services,
repositories, guard, eval runner, controlled import, events, audit, ATLAS
Engine o planner supportivo.

### Frontend TL UX Agent

Lavora sulla PWA e sull'esperienza TL solo quando lo scope lo autorizza.

Obiettivo: interfaccia mobile essenziale, leggibile e operativa. Non deve
trasformare TL Chat in dashboard MES pesante o introdurre flussi decisionali
autonomi.

### Security Data Boundary Agent

Verifica privacy, leakage, sanitizer, policy gate, secret handling, prompt
boundary e assenza di dati sensibili in output, test, log e documenti.

Blocca qualunque proposta che tocchi `.env`, immagini, Excel reali, SMF reale,
dump database, specifiche private o prompt non sanificati.

### Release Closure Agent

Verifica che una capability sia davvero chiudibile: scope rispettato, diff
minimo, test eseguiti, guard verdi, rischi residui dichiarati, nessun dato reale
e nessuna espansione laterale.

Non decide il rilascio. Produce verdict per review umana.

## 4. Permessi per ruolo

Permessi comuni a tutti i ruoli:

- leggere `docs/prometeo_system_map.md`;
- leggere `docs/PROMETEO_MASTER.md`;
- leggere documenti governance/eval/guard pertinenti;
- leggere test pertinenti alla capability;
- proporre piani minimi;
- classificare output come `FATTO`, `INFERENZA`, `DA_VERIFICARE` o
  `BLOCCANTE`.

Permessi specifici:

| Ruolo | Permesso principale | Limite |
| --- | --- | --- |
| System Mapper Agent | Documentare stato e relazioni | Nessun runtime change |
| Domain Guard Agent | Validare invarianti dominio | Nessuna promozione a `CERTO` senza fonte |
| Retrieval Evidence Agent | Curare evidence pack | Solo fonti autorizzate |
| Conflict Detection Agent | Segnalare conflitti | Nessuna risoluzione autonoma |
| Test Eval Agent | Aggiungere test/eval autorizzati | Solo dati sintetici o sanificati |
| Backend Capability Agent | Patch backend scoped | Una capability alla volta |
| Frontend TL UX Agent | Patch PWA scoped | Nessuna dashboard pesante |
| Security Data Boundary Agent | Bloccare leakage e dati vietati | Nessuna eccezione implicita |
| Release Closure Agent | Verificare chiusura | Nessun merge/push autonomo |

## 5. File ammessi e vietati per ruolo

Ogni task deve ridefinire i file ammessi. In assenza di scope esplicito, nessun
file e modificabile.

File generalmente ammessi in lettura:

- `docs/prometeo_system_map.md`;
- `docs/PROMETEO_MASTER.md`;
- documenti in `docs/` pertinenti alla capability;
- test in `backend/tests/` pertinenti alla capability;
- file runtime pertinenti solo in lettura, se necessari alla diagnosi.

File generalmente ammessi in modifica solo con scope esplicito:

- documenti governance in `docs/`;
- test contract o eval sintetici;
- file backend/frontend/planner espressamente nominati nel task.

File vietati salvo autorizzazione umana forte e separata:

- `.env`;
- `specs_finitura/`;
- SMF reale;
- immagini reali;
- Excel reali;
- PDF reali;
- dump database;
- token, segreti, chiavi;
- dati personali o produttivi non sanificati.

## 6. Pipeline di handoff

Pipeline standard:

1. `GOAL`: capability target e criterio di successo.
2. `SCOPE`: limite operativo e non-obiettivi.
3. `FILES ALLOWED`: file leggibili/modificabili.
4. `FILES FORBIDDEN`: file vietati.
5. `TESTS`: test minimi prima e dopo.
6. `RISK`: `LOW`, `MEDIUM` o `HIGH`.
7. `PLAN`: passi minimi.
8. `WORK`: patch o report.
9. `VERIFY`: test, guard, diff sintetico.
10. `HANDOFF`: cosa passa al ruolo successivo o al TL.

Handoff tipico:

System Mapper -> Domain Guard -> Retrieval Evidence -> Conflict Detection ->
Test Eval -> Backend Capability o Frontend TL UX -> Security Data Boundary ->
Release Closure -> TL.

Il flusso puo saltare ruoli non pertinenti, ma non puo saltare TL quando la
decisione ha impatto operativo.

## 7. Formato output obbligatorio

Ogni agente deve produrre output con queste etichette:

```text
FATTO:
- evidenze verificate da file, test o output ripetibile.

INFERENZA:
- conclusioni ragionevoli derivate dalle evidenze.

DA_VERIFICARE:
- elementi non dimostrati o dipendenti da dati non letti.

BLOCCANTE:
- condizioni che impediscono di procedere in sicurezza.

RISCHIO:
- LOW | MEDIUM | HIGH, con motivo.

TEST:
- test eseguiti, non eseguiti e test consigliati.

VERDICT:
- PASS | FAIL | DA_VERIFICARE.
```

## 8. Stop condition

Un agente deve fermarsi e chiedere review umana quando:

- lo scope richiede dati reali o sensibili;
- emerge conflitto con `PROMETEO_MASTER.md`;
- serve modificare file vietati;
- serve promuovere una fonte derivata a `CERTO`;
- una patch richiede nuova architettura;
- un test fallisce per motivo non compreso;
- la capability richiede decisione TL;
- l'output potrebbe autorizzare apply operativo senza audit;
- il lavoro sta espandendo lo scope originale.

## 9. Regole anti-regressione

- Nessun push diretto su `main`.
- Nessuna capability multipla nello stesso intervento.
- Nessuna nuova architettura parallela.
- Nessun planner autonomo.
- Nessun AI-as-source-of-truth.
- Nessun accesso a dati reali vietati.
- Nessuna modifica a `.env`, `specs_finitura`, SMF reale, immagini, Excel reali
  o dump database.
- Nessuna modifica runtime da un task documentale.
- Nessun apply operativo senza preview, diff, conferma forte, audit e rollback
  quando richiesto.
- Nessuna risposta TL Chat deve nascondere incertezza, fonte o richiesta di
  conferma quando la confidence non e `CERTO`.

## 10. Relazione con PROMETEO_SYSTEM_MAP

`docs/prometeo_system_map.md` e la prima lettura obbligatoria per ogni agente.

Per verificare chiusura capability, scope creep, anti-entropia, no agenti liberi,
tool piccoli prima di agenti e criterio di stop, ogni agente deve usare anche:
`docs/PROMETEO_DEVELOPMENT_CLOSURE_CANON_001.md`.

Il System Map definisce:

- visione human-in-the-loop;
- architettura stabile `Order -> Route -> Station -> ProductionEvent`;
- sequenza operativa tra fonti, retrieval, domain model, ATLAS Engine, planner,
  TL Chat, audit, eval e guardrail;
- stato capability e gap aperti;
- invarianti dominio e regole anti-regressione.

Questo modello operativo non sostituisce la mappa. La usa per assegnare ruoli,
limitare scope e impedire che agenti diversi producano interpretazioni
parallele del sistema.

## 11. Relazione con decisione TL finale

Il TL resta autorita operativa finale.

Gli agenti possono preparare contesto, evidenze, test, diff, rischi,
alternative e raccomandazioni. Non possono decidere priorita produttive,
override, promozioni a `CERTO`, modifiche operative o applicazioni ad alto
impatto.

Quando una decisione riguarda produzione, route, eventi, planner, audit, dati
reali o modifica di stato, l'output dell'agente deve terminare con richiesta di
decisione TL o verdict `DA_VERIFICARE`.
