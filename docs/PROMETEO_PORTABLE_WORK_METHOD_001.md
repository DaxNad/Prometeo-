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
