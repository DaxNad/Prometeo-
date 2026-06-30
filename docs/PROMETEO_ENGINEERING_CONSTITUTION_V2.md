# PROMETEO Engineering Constitution

**Versione:** 2.0
**Stato:** APPROVED DESIGN

---

# Scopo

Questa Costituzione definisce i principi permanenti con cui PROMETEO viene progettato, sviluppato, verificato ed evoluto.

I principi qui descritti hanno priorità sulle convenzioni operative temporanee e possono essere modificati esclusivamente quando il cambiamento migliora contemporaneamente:

- qualità;
- affidabilità;
- capacità di consegna del progetto.

---

# Articolo 1 — Obiettivo

PROMETEO viene sviluppato per consegnare valore operativo reale.

Ogni attività di sviluppo deve contribuire, direttamente o indirettamente, all’obiettivo finale del progetto.

La governance è uno strumento al servizio del prodotto, non il prodotto stesso.

---

# Articolo 2 — Principi permanenti

I seguenti principi costituiscono il nucleo stabile di PROMETEO.

- Una sola capability attiva.
- Una sola priorità operativa.
- Nessuno scope creep.
- Ogni modifica deve essere verificabile.
- Ogni risposta deve essere tracciabile fino alla fonte.
- Distinzione rigorosa tra **CERTO**, **INFERITO** e **DA_VERIFICARE**.
- Test proporzionati al rischio della modifica.
- Repository sempre in stato consistente.
- Nessuna riduzione dei guardrail di sicurezza.
- Nessuna riduzione della governance delle fonti.

---

# Articolo 3 — Governance proporzionale al rischio

La quantità di processo richiesta deve essere proporzionata al rischio tecnico della modifica.

L’obiettivo non è massimizzare:

- documentazione;
- review;
- procedure.

L’obiettivo è massimizzare l’affidabilità con il minimo attrito necessario.

---

# Articolo 4 — Classificazione delle modifiche

## Livello A — Strategico

Comprende:

- nuove architetture;
- nuove capability fondamentali;
- modifiche alla governance;
- modifiche ai meccanismi di retrieval;
- modifiche ai guardrail.

Richiede:

- review completa;
- test completi;
- documentazione aggiornata.

---

## Livello B — Evolutivo

Comprende:

- estensioni di capability esistenti;
- nuove integrazioni;
- nuove sorgenti;
- miglioramenti funzionali.

Richiede:

- implementazione;
- test;
- aggiornamento della documentazione solo quando necessario.

---

## Livello C — Manutenzione tecnica

Comprende:

- refactoring;
- pulizia del codice;
- ottimizzazioni;
- riduzione del debito tecnico.

Richiede esclusivamente:

- comportamento pubblico invariato;
- regressioni assenti;
- test verdi.

Non richiede nuovi contratti se il comportamento esterno non cambia.

---

## Livello D — Editoriale

Comprende:

- correzioni documentali;
- typo;
- miglioramenti descrittivi;
- aggiornamenti non funzionali.

Richiede esclusivamente revisione.

---

# Articolo 5 — Documentazione

La documentazione deve crescere per conoscenza, non per quantità.

Regole:

- aggiornare prima i documenti esistenti;
- creare nuovi documenti solo quando nasce un concetto realmente nuovo;
- evitare duplicazioni;
- evitare frammentazione documentale.

---

# Articolo 6 — Contratti

I contratti descrivono il comportamento pubblico del sistema.

Un nuovo contratto viene creato soltanto quando:

- nasce una nuova capability;
- cambia un comportamento pubblico;
- cambia un’interfaccia;
- cambia una regola di governance.

Negli altri casi si aggiorna il contratto esistente.

---

# Articolo 7 — Pull Request

Una Pull Request rappresenta un incremento funzionale coerente.

Può contenere più modifiche purché:

- appartengano alla stessa capability;
- siano verificabili come un’unica unità funzionale;
- mantengano coerenza architetturale.

La frammentazione artificiale deve essere evitata.

---

# Articolo 8 — Refactoring

Il refactoring è considerato manutenzione ordinaria.

È incoraggiato quando:

- riduce la complessità;
- migliora la leggibilità;
- elimina debito tecnico;
- non modifica il comportamento pubblico.

---

# Articolo 9 — Criterio di completamento

Una capability è completata quando:

- il requisito è soddisfatto;
- i test sono adeguati al rischio;
- la governance è rispettata;
- il valore operativo è aumentato.

La quantità di documentazione prodotta non costituisce criterio di completamento.

---

# Articolo 10 — Execution Mode

PROMETEO entra in **Execution Mode** quando:

- l’architettura principale è stabilizzata;
- la governance fondamentale è consolidata;
- la priorità diventa la consegna di valore operativo.

In Execution Mode:

- la qualità non diminuisce;
- la sicurezza non diminuisce;
- la tracciabilità non diminuisce;
- vengono eliminate le attività di processo che non producono valore proporzionato.

---

# Articolo 11 — Test di una nuova regola

Prima di introdurre una nuova regola è obbligatorio verificare:

> **La regola aumenta l’affidabilità più di quanto rallenti la capacità di consegnare valore?**

Se la risposta è negativa, la regola deve essere semplificata, accorpata oppure non introdotta.

---

# Articolo 12 — Principio finale

PROMETEO ricerca costantemente il miglior equilibrio tra:

- affidabilità;
- semplicità;
- velocità di esecuzione;
- valore operativo.

La governance è un moltiplicatore di qualità.

Non deve mai trasformarsi in un ostacolo al completamento del prodotto.
