# TL_CHAT_12514_CONFIRMATION_RUNTIME_BOUNDARY_001

## Purpose

Define the runtime boundary for future TL Chat confirmation behavior for article 12514 before any implementation.

This is a document-only boundary. It does not implement runtime confirmation, persist TL answers, mutate preview JSON, or promote any field to CERTO.

## Source documents

- docs/TL_CHAT_12514_CONFIRMATION_PROMPT_CONTRACT_001.md
- backend/tests/test_tl_chat_12514_confirmation_prompt_contract_doc.py
- docs/TL_CHAT_12514_SOURCE_CONFIRMATION_REVIEW_001.md

## Boundary principle

TL Chat may ask bounded confirmation questions and may display non-persisted candidate confirmation outcomes.

TL Chat must not persist TL answers, mutate source data, promote certainty, or enable operational execution in this boundary.

## Allowed runtime surface

Future runtime may display:

- article 12514 preview fields
- PREVIEW_ONLY status
- DA_VERIFICARE confidence
- requires_tl_confirmation=true
- planner_eligible=false
- Q1-Q7 confirmation questions from the prompt contract
- allowed answer states
- blocked operational conclusions
- non-persisted confirmation result summary

Future runtime may ask:

- one bounded confirmation group at a time
- Q1 article identity confirmation
- Q2 packaging and quantities confirmation
- Q3 normalized route confirmation
- Q4 ZAW station resolution clarification
- Q5 components confirmation
- Q6 tooling confirmation
- Q7 PIDMILL and CP visibility clarification

Future runtime may receive:

- YES
- NO
- UNKNOWN
- CORRECTED_VALUE
- NOT_VISIBLE
- ABSENT

## Allowed non-persisted output states

| Output state | Meaning | Persistence allowed in this boundary |
|---|---|---|
| CANDIDATE_CONFIRMATION | TL answer appears to confirm proposed value | No |
| CANDIDATE_CORRECTION | TL provides corrected value | No |
| DA_VERIFICARE | Value remains uncertain | No |
| MISSING | Required value is unavailable or not visible | No |
| BLOCKED | Request exceeds governed confirmation scope | No |

## Forbidden runtime effects

The following effects are explicitly forbidden:

- persist TL answers
- mutate data/local_reports/spec_intake_preview/12514_metadata_preview.json
- write confirmation state to SMF
- write confirmation state to database
- promote any field to CERTO
- set planner_eligible=true
- mark article 12514 ready for planning
- mark article 12514 ready for production
- infer ZAW2 from repeated ZAW operations
- invoke planner
- invoke ATLAS runtime
- change TL Chat API contract
- add new source ingestion

## Ask-only boundary

Within this boundary, TL Chat behavior is ask-only and summarize-only.

Allowed:

- ask the next governed confirmation question
- show current preview values
- show allowed answer states
- explain that the response is not a CERTO promotion
- summarize the TL response as non-persisted candidate confirmation

Forbidden:

- saving the answer
- treating the answer as source of truth
- updating preview metadata
- changing route_status
- changing zaw_station_resolution
- enabling planner

## Required response framing

Every future runtime confirmation prompt must include this framing:

La tua risposta serve solo come input di conferma governata. Non viene salvata da questa funzione, non promuove automaticamente il dato a CERTO e non abilita planner o produzione.

## Stop conditions

TL Chat must stop or refuse when the user asks to:

- confirm production readiness
- confirm planning readiness
- save the confirmation
- update source JSON
- write to SMF or database
- promote to CERTO
- infer route or ZAW station without explicit governed rule
- use ATLAS or planner for this confirmation

## Future implementation preconditions

Before any runtime implementation, a separate capability must define:

- exact non-persistent response model
- test cases for allowed Q1-Q7 prompts
- test cases for forbidden persistence
- test cases for anti-CERTO behavior
- test cases for anti-planner and anti-ATLAS behavior
- explicit statement that preview JSON remains immutable

## Recommended next capability

TL_CHAT_12514_CONFIRMATION_RUNTIME_BOUNDARY_TEST_001

Purpose:

- guard this runtime boundary document with a document-level test
- require ask-only and no-persist language
- require forbidden runtime effects
- require stop conditions
- require anti-CERTO, anti-planner, anti-ATLAS, and no JSON mutation boundaries

## Explicit non-goals

- no runtime implementation
- no TL answer persistence
- no preview JSON mutation
- no automatic promotion to CERTO
- no planner
- no ATLAS runtime
- no SMF/DB write
- no new source ingestion
- no TL Chat API change
- no production decision automation

## Closure verdict

CAPABILITY: TL_CHAT_12514_CONFIRMATION_RUNTIME_BOUNDARY_001
STATUS: DOCUMENT_CREATED
VERDICT: PENDING_TEST_AND_PR
NEXT SAFE ACTION: add, commit, push, and open PR for this runtime boundary document
