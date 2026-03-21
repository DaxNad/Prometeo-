# ADR-001 — Adozione monorepo PROMETEO

## Stato
APPROVATO

## Contesto
Il progetto è distribuito su più repository separati con rischio di duplicazioni, divergenza configurazioni e complessità operativa.

## Decisione
Unificare i componenti in un monorepo unico PROMETEO.

## Conseguenze
### Positive
- Visione unica del sistema
- Riduzione duplicazioni
- Deploy e sviluppo più coerenti
- Governance centralizzata

### Negative
- Fase iniziale di migrazione e riordino
- Necessità di verificare conflitti fra file legacy
