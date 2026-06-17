---
title: PROMETEO_MIMO_MINIMAX_M3_BINDING_001
date: 2026-06-17
status: DOCUMENTAL_BINDING_ONLY
scope: prometeo_mimo_model_usage
runtime_enabled: false
access_mode: read_only
contains_secrets: false
source_report: data/local_reports/mimo/MIMO_MINIMAX_M3_VALIDATION_001.md
lifecycle_status: active
review_date: 2026-09-17
retention_rule: replace_when_newer_validation_exists
---

# PROMETEO_MIMO_MINIMAX_M3_BINDING_001

## Scopo

Questo documento rende disponibile a PROMETEO, come fonte documentale versionabile e read-only, la conoscenza minima necessaria sull'uso di MiMo con MiniMax M3.

Il report completo di validazione resta locale e ignorato da git:

- data/local_reports/mimo/MIMO_MINIMAX_M3_VALIDATION_001.md

Questo binding non abilita runtime automatico, non collega TL Chat, non collega planner, non modifica backend/frontend e non autorizza scritture.

## Metodo di indicizzazione governata

Questo documento applica il metodo PROMETEO di indicizzazione governata.

Regole:

- una fonte indicizzata deve avere stato, ruolo, access_mode e runtime_enabled espliciti
- fonti nuove sullo stesso tema ma piu aggiornate devono sostituire o supersedere le fonti precedenti
- fonti validate come obsolete devono essere marcate e rimosse secondo calendario prestabilito
- l'indice non deve accumulare duplicati non governati sullo stesso tema
- ogni fonte attiva deve avere una policy di review o retention
- l'indice resta read-only per il runtime finche non esiste un adapter autorizzato

Applicazione a questo binding:

| Campo | Valore |
|---|---|
| lifecycle_status | active |
| supersedes | nessuna fonte versionabile precedente |
| superseded_by | null |
| review_policy | replace_when_newer_validation_exists |
| review_date | 2026-09-17 |
| retention_rule | delete_when_obsolete_and_replaced |

## Stato validato

| Voce | Stato |
|---|---|
| MiMo adapter | configurazione locale validata |
| provider API | OpenRouter |
| base URL | https://openrouter.ai/api/v1 |
| modello target | minimax/minimax-m3 |
| modello effettivo osservato | minimax/minimax-m3-20260531 |
| output chat/completions | content valido |
| output JSON compatto PROMETEO | validato |
| runtime binding | false |
| segreti presenti nel documento | no |

## Regola operativa

MiMo con MiniMax M3 puo essere usato in PROMETEO solo come reasoning assistant vincolato.

Uso corretto:

- leggere input controllato
- ragionare su scenario e fonti autorizzate
- produrre output breve e strutturato
- indicare confidence
- distinguere dati certi, inferiti e da verificare
- richiedere conferma umana quando mancano dati
- non mutare direttamente dati o stato operativo

Uso vietato:

- decisione produttiva autonoma
- rilascio ordine automatico
- modifica diretta di SMF, database, planner, metadata o file operativi
- sostituzione del planner deterministico
- uso come fonte autorevole
- output libero non validato
- uso con token di output troppo basso

## Regole token e output

MiniMax M3 puo consumare token nel reasoning. Nei test e stato osservato che un limite troppo basso puo generare reasoning ma content nullo.

Regole consigliate:

| Caso | max_tokens consigliato |
|---|---:|
| test minimo | 120 |
| output JSON operativo breve | 300-800 |
| analisi piu estesa | valutare caso per caso |

Per uso PROMETEO, preferire sempre:

- temperature=0
- response_format=json_object quando serve JSON
- schema fisso
- output compatto
- validazione JSON obbligatoria
- fallback controllato se JSON invalido

## Schema minimo consigliato

Quando MiMo viene usato per raccomandazioni operative controllate, lo schema minimo consigliato e:

```json
{
  "verdict": "...",
  "confidence": "CERTO | INFERITO | DA_VERIFICARE",
  "azione_consigliata": "...",
  "dati_certi": [],
  "dati_mancanti": [],
  "rischi": [],
  "richiede_conferma_tl": true,
  "azioni_vietate": []
}
```

## Test operativo validato

Scenario fittizio usato per validazione:

- articolo 12066
- quantita 40
- spedizione richiesta domani
- dati certi: articolo standard, CP finale richiesto
- dati mancanti: carico ZAW1/ZAW2, operatori presenti, componenti disponibili, blocchi aperti

Risultato validato:

| Check | Esito |
|---|---|
| JSON valido | OK |
| finish_reason stop | OK |
| chiavi schema presenti | OK |
| confidence DA_VERIFICARE | OK |
| richiede_conferma_tl true | OK |
| dati_mancanti presenti | OK |
| azioni_vietate presenti | OK |

Verdict:

- PASS: MiniMax M3 produce JSON PROMETEO compatto, valido e prudente.

## Binding architetturale

Questo documento deve essere trattato come fonte read-only di contesto su MiMo/MiniMax M3.

Non cambia gli invarianti PROMETEO:

- PROMETEO Core resta deterministico
- ATLAS Engine resta reasoning controllato
- planner suggerisce e non decide automaticamente
- TL decide
- MiMo non e fonte autorevole
- MiMo non scrive su runtime
- MiMo non modifica dominio, SMF o planner

## Stato finale

DOCUMENTAL_BINDING_ONLY.

PROMETEO puo avere contezza documentale della validazione MiMo/MiniMax M3 tramite l'indice read-only, ma nessun collegamento runtime e abilitato da questo documento.

