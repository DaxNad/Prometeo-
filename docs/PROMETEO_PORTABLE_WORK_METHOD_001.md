# PROMETEO Portable Work Method 001

## Status

- method: `PROMETEO_PORTABLE_WORK_METHOD_001`
- lifecycle: `ACTIVE`
- runtime_impact: `NONE`
- purpose: rendere il lavoro su PROMETEO indipendente da Atlas Browser, dalla memoria delle chat e da un singolo modello
- applies_to: assistenti cloud, assistenti locali, Codex, LM Studio e operatori umani autorizzati

## Principio operativo

Il modello utilizzato può cambiare.

Il browser, l'interfaccia e gli strumenti possono cambiare.

Le fonti di verità, il perimetro della capability e le prove tecniche devono invece restare verificabili e condivisibili attraverso il repository.

## 1. Stato canonico del progetto

PROMETEO deve poter essere compreso e ripreso da qualunque assistente autorizzato senza dipendere dalla memoria di una chat, da Atlas Browser o da un singolo modello.

Le fonti autorevoli del progetto sono limitate a:

1. `docs/PROMETEO_MASTER.md`

   Fonte primaria per principi, dominio, gerarchia delle autorità, stati semantici e vincoli architetturali.

2. `docs/CURRENT_STATE.md`

   Fonte primaria per lo stato operativo corrente, capability chiuse, gap ancora aperti, prove disponibili e limiti conosciuti.

3. Codice e test presenti nel repository

   Fonte di verità tecnica per simboli, file, endpoint, contratti, comportamenti runtime e copertura effettivamente esistente.

4. Una sola capability attiva

   Può essere dichiarata solo dopo verifica del repository e autorizzazione esplicita. Deve indicare almeno:

   - obiettivo verificabile;
   - scope ammesso;
   - file o moduli coinvolti;
   - comportamenti vietati;
   - test richiesti;
   - criterio di chiusura.

Nessun riepilogo di chat, memoria del modello, documento storico, roadmap superata o inferenza dell'assistente può sostituire queste fonti.

In caso di conflitto si applica il seguente ordine:

```text
specifica reale e conferma umana
→ PROMETEO_MASTER
→ CURRENT_STATE
→ codice e test
→ capability attiva autorizzata
→ inferenze del modello
```

Se `CURRENT_STATE.md` non è allineato con il codice e con i test, il documento deve essere aggiornato prima di selezionare una nuova capability.

Se non esiste una capability attiva autorizzata, il sistema resta in stato di verifica e non apre nuovo sviluppo per supposizione.


## 2. Pacchetto di sessione portabile

Ogni nuova sessione di lavoro deve iniziare da un pacchetto minimo costruito dal repository.

Il pacchetto serve a trasferire lo stato operativo tra GPT-5.6, Sol, Codex, LM Studio o altri assistenti autorizzati senza dipendere dalla memoria della conversazione precedente.

Deve contenere almeno:

1. Identità del repository

   - percorso locale;
   - remote principale;
   - branch corrente;
   - commit `HEAD`;
   - branch base autorevole.

2. Stato Git

   - working tree pulito o modificato;
   - file modificati;
   - file staged;
   - differenza rispetto alla base;
   - eventuali commit non ancora pubblicati.

3. Stato canonico

   - riferimento a `docs/PROMETEO_MASTER.md`;
   - sintesi verificata di `docs/CURRENT_STATE.md`;
   - eventuali discrepanze tra documentazione, codice e test.

4. Capability attiva

   Deve essere presente una sola capability autorizzata e deve riportare:

   - identificativo;
   - obiettivo verificabile;
   - stato: `VERIFY`, `ACTIVE`, `BLOCKED` o `CLOSED`;
   - criterio di chiusura;
   - rischi noti.

5. Perimetro operativo

   - file e moduli ammessi;
   - file e moduli vietati;
   - operazioni consentite;
   - operazioni vietate;
   - eventuale impatto runtime o dati.

6. Prove richieste

   - test mirati;
   - guard applicabili;
   - build o lint necessari;
   - verifica del diff;
   - eventuali prove post-merge.

7. Ultima chiusura verificata

   - ultima capability chiusa;
   - PR o commit di chiusura;
   - test eseguiti;
   - rischi residui;
   - stato di `main`.

8. Prossima mossa autorizzata

   Deve essere una sola azione concreta.

   Se non è possibile determinarla dalle fonti canoniche, il pacchetto deve dichiarare:

   ```text
   NEXT_MOVE: VERIFY
   ```

### Formato minimo

```text
REPOSITORY:
BRANCH:
HEAD:
BASE:
WORKTREE:
CURRENT_STATE:
ACTIVE_CAPABILITY:
CAPABILITY_STATUS:
ALLOWED_FILES:
FORBIDDEN_FILES:
ALLOWED_ACTIONS:
FORBIDDEN_ACTIONS:
REQUIRED_TESTS:
LAST_CLOSURE:
RISKS:
VERDICT:
NEXT_MOVE:
```

### Regole

- Il pacchetto descrive lo stato; non autorizza automaticamente modifiche.
- Ogni valore tecnico deve essere osservato nel repository o nei test.
- I campi mancanti devono essere dichiarati come `UNKNOWN` o `NOT_AUTHORIZED`.
- Nessun assistente può completare i campi tramite supposizione.
- Il pacchetto deve essere rigenerato quando cambiano branch, `HEAD`, working tree, capability o stato dei test.
- Un pacchetto precedente non sostituisce una nuova verifica del repository.
