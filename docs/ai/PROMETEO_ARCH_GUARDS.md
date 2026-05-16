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

# PROMETEO ARCHITECTURE GUARDS

hard constraints:

do not introduce bifurcations between:

smf_core
backend/services
planner logic
event logic

domain model frozen:

Order
ProductionEvent
Station
Rule
SMFRow

relations to preserve:

Order aggregates ProductionEvent
ProductionEvent represents real execution
Station represents real physical workstation
Route defines possible phases but is not source of state

forbidden:

do not create:

Phase as separate entity unless strictly required
duplicate Order mapping between SMF and DB
new CQRS layers
new distributed event buses
new microservices

allowed extensions:

new Order fields
new ProductionEvent types
new planner rules
new FastAPI endpoints coherent with existing model
