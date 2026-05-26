# PROMETEO — INPUT INTERFACE V1

## STATUS

ACTIVE — CORE OPERATIONAL CAPABILITY

Questo documento definisce la porta di ingresso primaria di PROMETEO.

PROMETEO deve avere una interfaccia operativa semplice, rapida e simile a ChatGPT, pensata per uso reale da smartphone o browser.

---

## PRIMARY OBJECTIVE

Consentire al Team Leader di fornire a PROMETEO il programma produzione reale tramite:

- foto
- screenshot
- file Excel
- testo copiato
- input chat

PROMETEO deve leggere, interpretare e trasformare questi input in uno snapshot operativo di produzione.

---

## WHY THIS IS CORE

Questa capability non è laterale.

È direttamente subordinata a:

PROMETEO PATTERN LEARNING IMPERATIVE

Senza input reale rapido, PROMETEO non può apprendere dai pattern TL e resta arretrato rispetto alla produzione reale.

---

## CANONICAL FLOW

INPUT TL
→ foto / screenshot / Excel / testo
→ OCR o parsing
→ riconoscimento codici
→ riconoscimento quantità
→ riconoscimento date richiesta / spedizione
→ riconoscimento cliente o programma se disponibile
→ preview controllata
→ conferma TL
→ snapshot produzione
→ Pattern Learning
→ proposta delega operatori / postazioni
→ supporto target 100 pezzi pro testa

---

## HARD RULES

PROMETEO non deve scrivere automaticamente dati operativi definitivi senza preview e conferma TL.

Ogni import deve produrre prima:

- dati estratti
- campi mancanti
- ambiguità
- anomalie
- livello confidenza
- richiesta conferma se necessario

---

## EXPECTED OUTPUT

Ogni input programma produzione deve produrre uno snapshot strutturato:

- periodo: giornaliero / settimanale / mensile
- codice articolo
- quantità richiesta
- data richiesta cliente / spedizione
- priorità se disponibile
- postazioni probabili
- criticità note
- stato: CERTO / DA_VERIFICARE / INCOMPLETO

---

## RELATION TO PATTERN LEARNING

Ogni snapshot alimenta il Pattern Learning.

PROMETEO deve usare gli input reali per apprendere:

- nuovi codici progetto
- nuove famiglie
- nuovi mix turno
- nuovi colli di bottiglia
- nuove pratiche operative
- distanza dal target 100 pezzi pro testa

---

## PROJECT LAW

La Input Interface V1 è capability core.

Qualunque sviluppo futuro su OCR, Excel import, chat UI, mobile UI, planner o runtime deve rispettare questa regola:

prima acquisire bene la realtà produttiva,
poi ragionare,
poi proporre azioni.
