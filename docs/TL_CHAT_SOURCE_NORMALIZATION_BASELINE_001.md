# TL_CHAT_SOURCE_NORMALIZATION_BASELINE_001

## Stato

- Capability: `TL_CHAT_SOURCE_NORMALIZATION_001`
- Baseline: `001`
- Modalità: `READ_ONLY_NON_BLOCKING`
- Target: `backend/app/api/tl_chat.py::_build_contract_response`
- Repository ref verificato: branch `audit/tl-chat-source-normalization-inventory`
- File target blob SHA: `d421049e39bc5f84fa7039db350cb3d18ae578e9`

## Risultato audit

| Metrica | Valore |
|---|---:|
| Return totali | 18 |
| Costruzioni dirette `TLChatResponse(...)` | 3 |
| Return delegati a helper o tramite variabile | 15 |

## Inventario dei return

| Linea | Classificazione | Target |
|---:|---|---|
| 2003 | delegato | `_response_for_densification_candidates` |
| 2007 | delegato | `_response_for_lifecycle_status_list` |
| 2010 | delegato | `_response_for_turn_fallback_without_article` |
| 2023 | variabile | `why_response` |
| 2026 | delegato | `_response_for_pidmill_dima` |
| 2032 | delegato | `_response_for_components` |
| 2043 | variabile | `operational_verification` |
| 2045 | delegato | `_response_from_local_specs_metadata` |
| 2049 | variabile | `article_summary_response` |
| 2054 | delegato | `_response_from_lifecycle` |
| 2066 | variabile | `confirmation_rendering_response` |
| 2068 | delegato | `_response_from_spec_intake_preview` |
| 2072 | variabile | `preview_response` |
| 2077 | variabile | `context_reader_response` |
| 2079 | diretto | `TLChatResponse` — articolo non disponibile nel profilo attivo |
| 2097 | delegato | `_response_from_family_registry` |
| 2103 | diretto | `TLChatResponse` — regola ZAW senza articolo |
| 2120 | diretto | `TLChatResponse` — contesto articolo mancante |

## Interpretazione

Questa baseline descrive la struttura di dispatch corrente. Non è un test di correttezza e non dimostra, da sola, difetti runtime.

In particolare:

- un `TLChatResponse(...)` diretto non equivale automaticamente a una risposta non governata;
- un return delegato non dimostra automaticamente l'uso del Context Resolver;
- l'uso del resolver dentro gli helper deve essere verificato separatamente;
- la baseline non modifica il contratto pubblico `/tl/chat`;
- la baseline non introduce nuovi criteri bloccanti nella suite.

## Limiti della capability

Incluso:

- censimento dei rami;
- classificazione progressiva delle sorgenti;
- definizione successiva di criteri comportamentali osservabili;
- migrazione incrementale, protetta da regressioni.

Fuori scope:

- nuove sorgenti;
- refactoring completo immediato;
- modifiche a UI, planner, SMF o database;
- riapertura della milestone retrieval reale già chiusa;
- uso del numero di return o della costruzione diretta come unico criterio di accettazione.

## Esito

`BASELINE_RECORDED`
