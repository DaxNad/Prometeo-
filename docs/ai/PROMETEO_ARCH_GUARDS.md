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
