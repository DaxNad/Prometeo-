# PROMETEO — PATTERN LEARNING RUNTIME V1

## STATUS

ACTIVE — OPERATIONAL LEARNING RUNTIME

Questo documento definisce il runtime reale di apprendimento di PROMETEO.

È subordinato a:

- PROMETEO_PATTERN_LEARNING_IMPERATIVE.md
- PROMETEO_INPUT_INTERFACE_V1.md

---

## PRIMARY OBJECTIVE

PROMETEO deve apprendere continuamente dai pattern TL
per ridurre il delta rispetto alla produzione reale.

---

## CANONICAL LEARNING FLOW

TL INPUT
→ chat
→ foto
→ screenshot
→ Excel
→ testo operativo

PROMETEO EXTRACTION
→ OCR
→ parsing
→ riconoscimento codici
→ quantità
→ date
→ priorità
→ possibili segnali operativi

PATTERN ENGINE
→ candidate pattern creation
→ confidence assignment
→ classification

RUNTIME MEMORY
→ pattern registry
→ reinforcement history
→ source tracking

RUNTIME USAGE
→ programma giorno
→ programma settimana
→ programma mese
→ delega operatori
→ supporto 100 pezzi pro testa
→ gestione nuovi codici progetto

---

## PATTERN ENGINE

Ogni nuovo input può generare:

PATTERN_CANDIDATE

Il Pattern Engine assegna:

- source
- confidence
- affected codes
- affected families
- operational impact
- timestamp

---

## PATTERN CLASSIFICATION

CERTO
- confermato da TL o dato reale affidabile

PATTERN_CANDIDATE
- pattern osservato ma non consolidato

ACTIVE_PATTERN
- pattern utilizzabile nel runtime operativo

EXCEPTION
- comportamento reale che rompe pattern esistente

---

## RUNTIME MEMORY

PROMETEO deve mantenere memoria operativa di:

- pattern attivi
- pattern candidati
- reinforcement history
- override TL
- eccezioni
- drift rispetto alla realtà

---

## OPERATIONAL OUTPUTS

PROMETEO deve usare i pattern appresi per produrre:

1. fotografia programma produzione
2. proposta delega operatori/postazioni
3. supporto target 100 pezzi pro testa
4. riconoscimento nuovi codici progetto
5. adattamento a nuovi mix produttivi

---

## PROJECT LAW

Il runtime di apprendimento non è opzionale.

PROMETEO deve imparare più velocemente possibile dal Team Leader e dalla produzione reale.

Ridurre il delta uomo → sistema è legge primaria del runtime.
