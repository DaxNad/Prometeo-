# TL_CHAT_REAL_QUESTION_OUTPUT_QUALITY_001

## Status

OBSERVED OUTPUT QUALITY AUDIT.

## Purpose

Evaluate whether the governed TL Chat answers for realistic Team Leader questions are usable by a TL, not only technically safe.

This follows:

- TL_CHAT_GOVERNED_RETRIEVAL_CLOSURE_001
- TL_CHAT_REAL_QUESTION_VALIDATION_001
- test(tl-chat): validate real question governed behavior (#374)

## Observed result

The 5 realistic TL questions returned governed and safe answers.

Security and governance behavior passed:

- no automatic production decision
- no promotion to CERTO
- confidence remains DA_VERIFICARE where required
- requires_confirmation remains true
- no planner action
- no write behavior

## Output quality verdict

Overall:

PARTIAL PASS.

The answers are safe, but not all are TL-usable yet.

## Scenario observations

### Q1 — Unknown article status

Question:

Il codice 99999 è attivo?

Observed answer:

99999

NON DISPONIBILE NEL PROFILO ATTIVO.

Verdict:

SAFE BUT NOT TL-USEFUL ENOUGH.

Issue:

recommended_action is None.

Expected future improvement:

The answer should include a clear next safe action, such as:

- verify article in authorized source
- provide article source/profile
- do not treat as active without confirmation

### Q2 — Generic turn decision without article

Question:

Cosa faccio partire adesso?

Verdict:

PASS.

Strength:

The answer refuses automatic prioritization and asks for article/order/lot/event context.

### Q3 — Governed source request

Question:

Mostrami la fonte governata retrieval per 99999

Verdict:

SAFE BUT TOO TECHNICAL.

Issue:

The answer exposes a long document excerpt and internal governance text.

Expected future improvement:

The answer should summarize the source instead of dumping a large raw excerpt.

### Q4 — Confidence semantics

Question:

Spiegami confidence CERTO INFERITO DA_VERIFICARE

Verdict:

SAFE BUT INCOMPLETE.

Issue:

The answer surfaces CERTO semantics, but does not clearly explain all three requested confidence levels in one TL-facing answer.

Expected future improvement:

The answer should explain:

- CERTO
- INFERITO
- DA_VERIFICARE

without implying operational authority.

### Q5 — Article-specific preview question

Question:

Cosa sai del 12514?

Verdict:

PASS.

Strength:

The answer exposes useful preview information while preserving limits:

- PREVIEW_ONLY
- DA_VERIFICARE
- planner_eligible=false
- requires_tl_confirmation=true
- can_promote=false
- codice cliente
- disegno/rev

## Next recommended capability

TL_CHAT_REAL_QUESTION_RENDERING_IMPROVEMENT_001

Goal:

Improve TL-facing answer rendering for the already validated 5-question set, without adding architecture, readers, planner, ATLAS, or new data sources.

## Explicit non-goals

This audit does not introduce:

- runtime changes
- API changes
- new source readers
- new source access
- planner integration
- ATLAS runtime integration
- SMF writes
- DB writes
- article densification
