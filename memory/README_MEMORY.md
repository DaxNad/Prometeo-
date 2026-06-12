---
memory_id: MEMORY_README_001
type: persistent_memory
status: active
authority: governance_summary
confidence: CERTO
allowed_for_retrieval: true
sensitive: false
last_review: 2026-06-12
title: PROMETEO memory workspace policy
---
# PROMETEO Memory

## FATTO

`memory/` contiene memoria locale sintetica per PROMETEO.

Scopo:

- ridurre dipendenza da memoria chat;
- fornire contesto stabile a ChatGPT, Codex e futuri agenti PROMETEO;
- preparare una base futura per retrieval governato e long-context controllato;
- mantenere sintesi brevi, verificabili e non sensibili.

Questa cartella puo contenere:

- stato operativo sintetico;
- invarianti dominio gia consolidati;
- stato capability;
- policy future di retrieval;
- note governate con `memory_id`, `authority`, `confidence` e flag di sicurezza.

Questa cartella non puo contenere:

- dati produttivi reali;
- specifiche private;
- SMF reale;
- immagini, PDF, Excel o dump;
- segreti, token, chiavi o credenziali;
- log lunghi;
- copie integrali di chat;
- duplicazioni estese di documenti gia presenti in `docs/`.

## INFERENZA

`memory/` deve funzionare come livello di sintesi, non come nuova fonte
semantica primaria. La fonte di autorita resta `docs/PROMETEO_MASTER.md`,
insieme a specifica reale e conferma TL quando applicabili.

## DA_VERIFICARE

Il collegamento futuro tra `memory/` e retrieval governato non e implementato in
questa capability.

## NON_USARE_COME_FONTE

Non usare `memory/` per decidere route, priorita produttive, apply operativo o
promozioni a `CERTO` senza fonte autorevole esterna alla memoria.

Non usare `memory/` come archivio libero di appunti. Ogni aggiunta deve essere
breve, governata, sanificata e utile alla chiusura capability.
