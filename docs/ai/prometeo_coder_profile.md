---

THIS DOCUMENT IS NOT A SEMANTIC SOURCE OF TRUTH.

Canonical domain semantics, planner constraints,
AI governance, TL operational rules,
station/process taxonomy and permanent policies
are defined exclusively in:

docs/PROMETEO_MASTER.md

This file exists only as:

* historical reference
* implementation support
* technical context
* archived material
* extracted summary

In case of conflict:
PROMETEO_MASTER.md prevails.

---

# PROMETEO — AI CODER PROFILE

## purpose

Define the operational coding context required for AI models working on PROMETEO.

This document acts as:

- stable system prompt reference
- domain alignment contract
- architecture guard rail
- coding constraint layer
- training dataset base

AI agents must respect this document when generating or modifying code.

---

# system identity

PROMETEO is an event-driven orchestration system for industrial production flow optimization.

Primary objective:

translate real production constraints into executable operational sequences.

PROMETEO is NOT a generic ERP.

PROMETEO is closer to:

MES-lite
event-driven workflow orchestrator
constraint-aware planner
production decision support system

---

# core domain entities

Order  
ProductionEvent  
Station  
Phase (logical)  
Rule  
Route  
SMFRow  
Component  
Family  
Packaging  

---

# domain structure

Order is the aggregate root.

Order is defined by:

order_id (stable identity)
code (internal production code)
quantity
priority
due_date
station constraint
state

Order evolves through ProductionEvents.

ProductionEvents represent real execution steps.

Each ProductionEvent is associated with:

station
event_type
status
timestamp

---

# station semantics

Stations are real physical production resources.

Examples:

GUAINE
ULTRASUONI
FORNO
WINTEC
PIDMILL
ZAW1
ZAW2
HENN
CP

Constraints:

HENN precedes ZAW
CP is final blocking phase
ZAW is bottleneck resource
shared components may block multiple Orders

---

# event driven logic

Route defines allowed sequence.

ProductionEvent defines executed sequence.

Planner proposes sequence respecting constraints:

station compatibility
shared component dependencies
priority rules
delivery deadlines
blocking phases

---

# SMF role

SMF (SuperMegaFile) is a transitional interoperability layer.

SMF is NOT source of truth.

SMF is:

input normalization layer
bridge with shopfloor tools
temporary persistence surface

SMFRow maps to Order.

Order.id = SMFRow.id

---

# operational constraints

shared components create cross-order dependencies

example:

O-ring shared between multiple codes
ZAW drivers shared across families

planner must consider:

global bottlenecks
component reuse
station saturation
multi-order interference

---

# coding rules

AI must:

avoid breaking event model
avoid bypassing Order aggregate logic
avoid introducing parallel sources of truth
avoid duplicating SMF mapping logic
avoid bypassing station constraints
avoid redefining state semantics

AI must preserve:

Order → ProductionEvent relationship
station compatibility constraints
event-driven structure
planner explainability
SMF bridge integrity

---

# repository structure

backend/
FastAPI services
domain logic
planner
event engine

frontend/
React dashboard
PWA interface

smf_core/
SMF bridge logic
excel interoperability

docs/
architecture decisions
AI context

board/
project governance

scripts/
operational utilities

---

# allowed modifications

AI may:

add diagnostic endpoints
improve planner logic
add explainability fields
refactor services preserving contracts
extend rule definitions
add compatibility tables
improve typing

AI must NOT:

change Order identity semantics
change event structure arbitrarily
remove explainability fields
introduce hidden side effects
duplicate SMF adapters
break compatibility with existing endpoints

---

# explainability requirement

planner outputs must remain explainable.

expected fields:

priority_reason
risk_level
constraint_source
dependency_source

---

# future AI integration

target models:

Qwen coder
Codex CLI
Claude architecture validator

PROMETEO requires domain-aligned coding assistance, not generic code completion.

