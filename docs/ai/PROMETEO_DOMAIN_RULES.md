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

# PROMETEO DOMAIN RULES

real stations:

GUAINE
ULTRASUONI
FORNO
WINTEC
PIDMILL
ZAW1
ZAW2
HENN
CP

known constraints:

HENN handles dedicated metal connectors.
ZAW handles O-ring crimping.
CP is final blocking phase.

shared dependencies:

plastic connectors shared across articles
O-rings shared across multiple codes
shared components can block multiple orders

key concepts:

shared driver
station bottleneck
multi-station sequence
assemblies and partials
ragno / ragnetto families

operational states:

PARZIALE
IN_ATTESA
SOSPESO
COMPLETATO
BLOCCATO

planner rule:

blocking constraints priority
then customer priority
then sequence optimization
