# TL_CHAT_REAL_SOURCE_COVERAGE_MAP_001

## Status

DRAFT.

## Purpose

Map which realistic Team Leader questions can currently be answered by TL Chat using governed sources, and which fail because source, article, order, lifecycle, or operational coverage is missing.

This follows the closed milestone:

TL Chat -> Retrieval reale -> Risposta verificabile.

## Scope

Documentation and coverage mapping only.

No runtime change.

## Question classes to map

### Article status

Example:

- Il codice 99999 è attivo?
- Cosa sai del 12514?

Coverage to verify:

- active profile
- lifecycle registry
- preview metadata
- governed source fallback
- missing article behavior

### Governed source request

Example:

- Mostrami la fonte governata retrieval per 99999

Coverage to verify:

- authorized source id
- reader status
- source summary
- confidence
- missing data
- next safe action

### Confidence semantics

Example:

- Spiegami confidence CERTO INFERITO DA_VERIFICARE

Coverage to verify:

- semantic registry availability
- TL-facing explanation
- no promotion to operational certainty

### Turn/order decision

Example:

- Cosa faccio partire adesso?
- Cosa devo fare con questo ordine?

Coverage to verify:

- article present
- order present
- lot present
- board state present
- event present
- refusal when context is missing

### Component or tooling question

Example:

- Che manicotto usa questo articolo?
- Che dima PIDMILL serve?

Coverage to verify:

- metadata components
- profile availability
- missing tool behavior
- recommended_action when unavailable

## Output format

Each mapped question should produce:

- Question
- Expected source
- Current status: ANSWERED / PARTIAL / MISSING / BLOCKED
- Confidence
- Missing data
- Current TL usefulness
- Next safe action
- Needed future capability, if any

## Initial known coverage

### Covered

- governed source request with read-only source summary
- confidence explanation
- preview-only article response for 12514
- missing article response with recommended_action
- generic turn decision refusal when context is missing

### Partial

- tooling questions where metadata/profile is incomplete
- component questions without full article coverage
- governed source answers limited to currently authorized source index

### Missing

- broad article/profile coverage
- order-aware retrieval
- board-state-aware retrieval
- source lifecycle/superseding runtime enforcement
- TL confirmation workflow

## Explicit non-goals

This document does not introduce:

- new readers
- new source access
- runtime changes
- API changes
- planner integration
- ATLAS runtime integration
- SMF writes
- DB writes
- automatic production decisions
