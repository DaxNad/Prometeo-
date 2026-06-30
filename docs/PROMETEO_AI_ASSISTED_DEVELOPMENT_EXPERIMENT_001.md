# PROMETEO_AI_ASSISTED_DEVELOPMENT_EXPERIMENT_001

## Status

EXPERIMENT.

This document defines a limited, measurable experiment for AI-assisted development review inside PROMETEO.

It is not a permanent governance layer.
It is not a runtime capability.
It does not authorize autonomous development.
It does not change PROMETEO public behavior.

## Purpose

The purpose of this experiment is to evaluate whether controlled AI-assisted review can improve PROMETEO development quality before code changes are authorized.

The experiment focuses on:

- read-only audit before patching;
- evidence review before implementation;
- detection of weak tests;
- detection of unnecessary patches;
- detection of real defects;
- safer capability closure;
- reduction of scope creep.

## Scope

The experiment applies only to PROMETEO development workflow review.

Allowed use:

- review existing files in read-only mode;
- identify missing evidence;
- identify weak or excessive tests;
- identify likely bugs;
- suggest whether a patch is justified;
- suggest limited files that may be changed, subject to human authorization;
- review diffs before commit;
- review PR scope before merge.

Not allowed:

- autonomous patching;
- autonomous merging;
- autonomous capability definition;
- autonomous runtime design;
- planner changes;
- SMF changes;
- database changes;
- frontend changes;
- ATLAS Engine changes;
- production behavior changes;
- permanent governance expansion.

## Operating Model

The experiment follows this sequence:

1. Human and ChatGPT define the active capability, constraints, risk, and next move.
2. Codex starts in review-only mode.
3. Human and ChatGPT decide whether to authorize, reduce, or block the proposed change.
4. Codex may patch only after scope and target files are explicitly declared.
5. Terminal executes tests, status checks, diff checks, commit, and PR creation.
6. ChatGPT closes the capability and declares one next move.

Codex is a reviewer or controlled patcher.
Codex is not a decision-maker.

## Required Evidence Before Patch

A patch may be authorized only when at least one of the following exists:

- a failing or missing test is identified;
- a real inconsistency is found in code, docs, or tests;
- an existing guard is too weak or too broad;
- an implementation gap is confirmed against an already accepted capability;
- a PR review identifies a concrete defect.

A patch should be blocked when:

- the finding is speculative;
- the proposed change expands scope;
- the proposed change creates new architecture without authorization;
- the same result can be achieved by documentation or test clarification;
- the change attempts to make an experiment permanent.

## Measurable Output

Each experiment cycle should produce a short result record in the working discussion or PR notes.

Minimum fields:

- capability reviewed;
- files inspected;
- finding type;
- patch authorized: yes/no;
- reason;
- tests executed;
- outcome;
- noise level: low/medium/high;
- next move.

Finding types:

- no issue found;
- weak test;
- unnecessary patch avoided;
- real bug found;
- scope creep blocked;
- documentation clarification;
- implementation gap confirmed.

## Exit Clause

This experiment must be stopped or reduced if it produces excessive noise.

Exit conditions include:

- repeated low-value comments;
- pressure to add permanent governance without behavioral need;
- repeated expansion beyond the active capability;
- more process than defect prevention;
- unclear ownership of decisions;
- patches proposed without evidence.

If the experiment is stopped, PROMETEO returns to the existing Capability Execution Workflow without adding a permanent AI-assisted governance layer.

## Success Criteria

The experiment is considered useful only if it measurably helps at least one of the following:

- prevents unnecessary patches;
- improves test quality;
- finds real defects before merge;
- reduces scope creep;
- improves PR closure confidence;
- keeps capability execution smaller and safer.

## Non-Goals

This experiment does not define:

- a new runtime capability;
- a new planner behavior;
- a new retrieval behavior;
- a new TL Chat answer behavior;
- a new ATLAS behavior;
- a new permanent governance constitution;
- a new autonomous agent workflow.

## Governance Boundary

This experiment remains subordinate to:

- Engineering Constitution v2;
- TL Chat real retrieval verifiable answer guard;
- Capability Execution Workflow;
- one active capability rule;
- one next move rule;
- proportional governance rule;
- proportional testing rule.

If this document conflicts with existing governance, existing governance wins.

## Closure Rule

This experiment can be closed only by a dedicated PR.

Closure must state one of:

- continue experiment unchanged;
- continue experiment with reduced scope;
- stop experiment;
- promote a specific proven rule into existing governance through a separate explicit proposal.

Promotion is not automatic.
Promotion requires evidence from the experiment.
