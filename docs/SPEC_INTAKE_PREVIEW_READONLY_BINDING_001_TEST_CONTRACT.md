# SPEC_INTAKE_PREVIEW_READONLY_BINDING_001_TEST_CONTRACT

## Status

TEST_CONTRACT_ONLY

## Capability sotto test

SPEC_INTAKE_PREVIEW_READONLY_BINDING_001

## Obiettivo

Garantire che una preview locale SPEC_INTAKE possa essere riconosciuta solo come DA_VERIFICARE e non venga mai promossa a dato operativo certo.

## Test obbligatori futuri

### 1. Preview presente

Dato un metadata preview locale esistente con:

- status = PREVIEW_ONLY
- confidence = DA_VERIFICARE
- planner_eligible = false
- requires_tl_confirmation = true

TL Chat può rispondere solo:

Articolo presente come preview locale DA_VERIFICARE.

Non è un profilo operativo attivo.
Non è planner-eligible.
Serve conferma TL prima di renderlo operativo.

### 2. Planner bloccato

La capability non deve mai restituire:

planner_eligible: true

### 3. CERTO bloccato

La capability non deve mai restituire come certezza operativa:

- CERTO
- CONFERMATO
- OPERATIVO
- PROFILO ATTIVO
- ROUTE DEFINITIVA
- COMPONENTI CONFERMATI
- PLANNER ATTIVO

se la fonte è solo preview.

### 4. DB write bloccato

La capability non deve scrivere database.

### 5. SMF write bloccato

La capability non deve scrivere SMF.

### 6. Route definitiva bloccata

La capability non deve normalizzare route definitiva.

### 7. Preview assente

Se la preview locale non esiste, TL Chat deve continuare a rispondere:

NON DISPONIBILE NEL PROFILO ATTIVO

oppure equivalente controllato.

## Mutazioni vietate

- Nessuna scrittura file dati
- Nessuna scrittura DB
- Nessuna scrittura SMF
- Nessuna promozione runtime
- Nessuna attivazione planner
- Nessuna modifica profilo articolo

## Runtime

runtime_enabled: false

## Planner

planner_enabled: false

## Database

db_write: false

## SMF

smf_write: false

## Verdict atteso

PASS solo se la capability rimane read-only, test-only e non operativa.
