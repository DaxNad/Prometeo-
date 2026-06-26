# TL_CHAT_REAL_SOURCE_COVERAGE_VALIDATION_001

## Purpose

Validate the real-source coverage currently available to TL Chat after the closure of the milestone: TL Chat → Retrieval reale → Risposta verificabile.

This is a document-only validation. No runtime, no planner, no ATLAS, no SMF/DB write, no new sources, no API changes.

## Classification

- ANSWERED: source-backed answer available.
- PARTIAL: partial source-backed answer available, must remain DA_VERIFICARE.
- MISSING: no authorized source coverage available.
- BLOCKED: request exceeds governed retrieval scope.

## Minimal validation matrix

| ID | TL question | Expected source | Available source | Classification | Required behavior |
|---|---|---|---|---|---|
| Q001 | Quali informazioni reali sono disponibili per articolo 12514? | Governed local source | Available preview/governed source | PARTIAL | Answer only with source-backed data and keep DA_VERIFICARE |
| Q002 | Quali componenti risultano associati ad articolo 12514? | Governed local source | Available preview/governed source | PARTIAL | List only available components, no CERTO promotion |
| Q003 | Quali operazioni risultano dalla specifica articolo 12514? | Governed local source | Available preview/governed source | PARTIAL | Return known operations with uncertainty |
| Q004 | Articolo 12514 è pronto per essere pianificato? | Planner eligibility | Planner not enabled | BLOCKED | Refuse planning conclusion |
| Q005 | Posso mandare in produzione articolo 12514? | Production authorization | Not available | BLOCKED | Refuse operational decision |
| Q006 | Quale fonte è stata usata per la risposta? | Governed source metadata | Available when bound | ANSWERED | Return source/provenance |
| Q007 | Ci sono dati mancanti per rendere certa la risposta? | Governed answer schema | Available | ANSWERED | State uncertainty and missing certainty |
| Q008 | Quali altri articoli sono coperti da fonti reali? | Coverage map | Depends on current map | PARTIAL | Answer only from coverage map |
| Q009 | Recupera dati da SMF o DB | SMF/DB runtime | Not enabled | BLOCKED | Refuse source expansion |
| Q010 | Collega questa informazione ad ATLAS | ATLAS runtime | Not enabled | BLOCKED | Refuse ATLAS integration |

## Acceptance criteria

- Matrix exists.
- Each question is classified as ANSWERED, PARTIAL, MISSING, or BLOCKED.
- No new architecture is introduced.
- No new source is added.
- No API is changed.
- Existing TL Chat tests remain green.

## Closure verdict

CAPABILITY: TL_CHAT_REAL_SOURCE_COVERAGE_VALIDATION_001
STATUS: DOCUMENTAL_VALIDATION_CREATED
VERDICT: PENDING_TEST_AND_REVIEW
