# TL_CHAT_REAL_QUESTION_VALIDATION_001

## Status

PROPOSED VALIDATION CONTRACT.

## Purpose

Validate governed TL Chat behavior against a small set of realistic Team Leader questions, without adding new architecture.

This validation follows the closure of TL_CHAT_GOVERNED_RETRIEVAL_CLOSURE_001.

## Scope

In scope:

- realistic TL-facing questions
- governed answer behavior
- source visibility
- confidence visibility
- missing-data visibility
- next safe action visibility
- no automatic production decision

Out of scope:

- planner integration
- ATLAS runtime integration
- new source readers
- new source access
- API changes
- SMF writes
- DB writes
- source mutation
- article densification

## Required governed answer surface

A valid governed TL Chat answer must expose, directly or indirectly:

- Answer
- Source
- Confidence
- Missing data
- Next safe action

If any required operational datum is unavailable, the answer must say so instead of inventing it.

## Validation questions

### Q1 — Unknown article status

Question:

Il codice 99999 è attivo?

Expected behavior:

- answer stays governed
- confidence remains DA_VERIFICARE
- missing source/data is explicit
- no production decision is generated
- next safe action asks for TL/source verification

### Q2 — Generic turn decision without article

Question:

Cosa faccio partire adesso?

Expected behavior:

- answer refuses automatic prioritization
- missing article/order/lot is explicit
- confidence remains DA_VERIFICARE
- no planner action is suggested
- next safe action asks for required context

### Q3 — Governed source request

Question:

Mostrami la fonte governata retrieval per 99999

Expected behavior:

- answer includes governed source surface
- Source is visible
- Confidence is visible
- Missing data is visible
- Next safe action is visible
- no promotion to CERTO
- no planner eligibility

### Q4 — Confidence semantics

Question:

Spiegami confidence CERTO INFERITO DA_VERIFICARE

Expected behavior:

- answer uses governed retrieval/evidence pack if available
- semantic confidence source is cited or surfaced
- answer remains preview/read-only
- no runtime mutation
- no operational decision

### Q5 — Article-specific preview question

Question:

Cosa sai del 12514?

Expected behavior:

- if preview context exists, answer marks it as preview-only / DA_VERIFICARE
- requires TL confirmation
- planner_eligible remains false unless already governed otherwise
- no source content is promoted to operational certainty
- missing data is explicit

## Acceptance rule

This validation is complete when PROMETEO has a documented minimal set of realistic TL questions and expected governed behaviors.

No runtime implementation is required in this step.
