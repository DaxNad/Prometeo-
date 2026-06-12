---
memory_id: MEMORY_DOMAIN_INVARIANTS_001
type: persistent_memory
status: active
authority: domain_summary
confidence: CERTO
allowed_for_retrieval: true
sensitive: false
last_review: 2026-06-12
title: PROMETEO domain invariants
---
# Domain Invariants

## FATTO

Invarianti consolidati:

- `ZAW1` e `ZAW2` non sono intercambiabili.
- `ZAW1_2` non e `ZAW2`.
- `ZAW2` non va inferito da doppio passaggio `ZAW`.
- `CP` finale e obbligatorio quando `cp_required=true`.
- `COLLAUDO_VERTICALE` e modalita macchina `CP`, non postazione separata.
- `HENN` non va inferito senza fonte confermata.
- Specifica reale + conferma TL prevalgono su fonti derivate.
- Planner suggerisce, TL decide.
- ATLAS Engine segnala/spiega, non muta direttamente il dominio.

## INFERENZA

Ogni capability che tocca route, stazioni, planner, TL Chat, retrieval o
conflict detection deve verificare questi invarianti prima del verdict.

## DA_VERIFICARE

Nuovi invarianti o eccezioni operative devono essere promossi solo tramite fonte
autorevole e aggiornamento coerente dei documenti primari.

## NON_USARE_COME_FONTE

Non usare questo file per dedurre route articolo, componenti, stati ordine o
priorita operative senza evidenza autorizzata.
