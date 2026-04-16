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
