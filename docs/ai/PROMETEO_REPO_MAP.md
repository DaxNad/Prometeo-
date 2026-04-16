# PROMETEO REPOSITORY MAP

## Purpose

Help AI coding agents understand where core logic resides.

## Repository structure overview

- `backend/`  
  Main application logic.

- `backend/app/main.py`  
  FastAPI entrypoint.

- `backend/app/services/`  
  Business logic layer.

- `backend/app/routers/`  
  API endpoints.

- `backend/app/smf/`  
  SMF bridge between Excel and domain.

- `backend/app/agent_runtime/`  
  Runtime logic for agent orchestration.

- `backend/app/planner/`  
  Sequence and planning logic.

- `backend/app/models/`  
  Domain entities.

- `backend/app/schemas/`  
  API schemas.

- `docs/ai/`  
  AI operational rules.

- `evals/`  
  AI evaluation test cases.

## SMF role

- `SMFRow` represents Excel-originated planning data.
- SMF is an interoperability layer, not the primary source of truth.

## Domain core

- `Order` aggregates `ProductionEvent`.
- `ProductionEvent` represents real execution state.
- `Station` represents physical workstation constraints.

## Planner role

The planner generates production sequence proposals.

The planner must respect:

- Station constraints
- Shared components
- Blocking phases
- Customer priority
- Delivery dates

## Critical constraint

Do not duplicate domain logic outside backend services.

## Preferred modification areas

- `backend/app/services/`
- `backend/app/planner/`
- `backend/app/smf/`

## Avoid

Creating parallel domain structures outside backend.

## Goal

Reduce navigation cost for AI coding agents.
