# PROMETEO_PRODUCT_COMPLETE_ROADMAP_V1

## Scopo

Questo documento definisce la roadmap vincolante per portare PROMETEO a prodotto completo, funzionante, dimostrabile e potenzialmente monetizzabile.

PROMETEO non viene considerato completo quando esiste solo documentazione di readiness.
PROMETEO viene considerato completo quando il sistema è utilizzabile operativamente da un responsabile di reparto ad alta variabilità per interrogare codici, leggere situazioni, valutare priorità, registrare eventi e ricevere supporto decisionale tracciabile.

## Definizione di GOAL

PROMETEO è a GOAL quando soddisfa tutte le condizioni minime seguenti:

1. Backend FastAPI stabile e testato.
2. PWA/interfaccia minimale utilizzabile da smartphone.
3. TL Chat operativa con risposte brevi, vincolate e contestuali.
4. Dominio articoli interrogabile.
5. Route articolo gestite come dati controllati.
6. Eventi produttivi registrabili.
7. Planner assistivo capace di proporre sequenze motivate.
8. ATLAS Engine capace di rilevare rischi, incoerenze e vincoli.
9. Override umano tracciato.
10. Audit log disponibile.
11. Nessuna esposizione di dati sensibili.
12. Demo interna sanificabile.
13. Architettura predisposta a futura modalità SaaS o MES leggero.

## Non-obiettivi immediati

Questa roadmap non autorizza:

- riscrittura generale del sistema;
- dashboard enterprise pesante;
- automatismi decisionali senza conferma umana;
- push diretto su main;
- uso di dati reali sensibili in demo esterne;
- ampliamento laterale senza chiusura capability.

## FASE 1 - Product Core Closure

Obiettivo: chiudere il cuore operativo minimo.

Componenti richiesti:

- Order
- Article
- Route
- Station
- ProductionEvent
- Stato avanzamento
- Blocco operativo
- Priorità per scadenza
- Risposta TL Chat su codice/articolo

Criterio di chiusura:

Una domanda del tipo "Situazione 12066?" deve produrre una risposta operativa con:

- stato articolo;
- route nota o stato di verifica;
- prossima azione;
- rischio;
- eventuale conferma richiesta.

## FASE 2 - Densificazione dominio reale

Obiettivo: rendere PROMETEO utile con dati reali controllati.

Priorità densificazione:

1. articoli standard ricorrenti;
2. complessivi semplici;
3. complessivi complessi;
4. articoli con plastiche;
5. articoli con PIDMILL;
6. articoli con doppio passaggio ZAW1;
7. articoli con conflitti storici.

Regola:

PROMETEO deve conoscere più codici di quanti ne pianifica.
La conoscenza articolo non implica planner_eligible automatico.

## FASE 3 - Interfaccia operativa minimale

Obiettivo: rendere PROMETEO usabile da smartphone.

Interfaccia primaria:

- input comando/domanda;
- risposta breve;
- stato codice;
- prossima azione;
- rischio;
- conferma richiesta;
- ultimi eventi rilevanti.

Non deve diventare una dashboard MES pesante.

## FASE 4 - Planner assistivo

Obiettivo: proporre sequenze produttive motivate.

Il planner deve usare:

- scadenze;
- route;
- postazioni;
- eventi aperti;
- blocchi;
- disponibilità informativa;
- classe operativa articolo;
- conferma umana quando necessaria.

Il planner non deve:

- produrre priorità autonome senza ordine o richiesta;
- ignorare operational_class;
- pianificare reference-only come standard;
- trasformare ogni evento aperto in criticità automatica.

## FASE 5 - Audit e Human Override

Obiettivo: ogni modifica importante deve essere tracciata.

Pipeline obbligatoria:

comando umano -> estrazione -> classificazione rischio -> preview/diff -> conferma -> applicazione -> audit log

Per modifiche ad alto impatto serve conferma forte.

Esempio:

CONFERMO MODIFICA 12066

## FASE 6 - Demo interna

Obiettivo: PROMETEO deve essere dimostrabile in ambiente controllato.

Scenario demo minimo:

1. consultazione articolo;
2. visualizzazione route;
3. visualizzazione rischio;
4. registrazione evento;
5. proposta priorità;
6. override umano;
7. audit visibile;
8. dati sanificati.

## FASE 7 - Productization SaaS/MES leggero

Obiettivo: preparare monetizzazione solo dopo validazione interna.

Elementi futuri:

- autenticazione;
- ruoli;
- multi-tenant;
- ambiente demo;
- onboarding cliente;
- data boundary;
- backup/export;
- pricing;
- documentazione commerciale.

## Gate di avanzamento

Ogni fase può avanzare solo se:

- esiste test minimo;
- non rompe core runtime;
- non introduce dati sensibili;
- non crea biforcazioni smf_core/backend;
- non espande scope senza motivazione;
- passa da branch dedicato e PR.

## Ordine operativo permanente

1. Chiudere Product Core.
2. Densificare dominio reale.
3. Rendere PWA usabile.
4. Attivare planner assistivo.
5. Rafforzare audit.
6. Preparare demo.
7. Solo dopo valutare SaaS/MES.

## Stato iniziale

PROMETEO possiede già:

- backend FastAPI;
- modello dominio di base;
- TL Chat;
- test semantici;
- regole ZAW/HENN/PIDMILL/CP;
- guardrail privacy;
- CI;
- workflow branch/PR;
- ATLAS Engine in evoluzione;
- knowledge spine documentale.

Il lavoro da fare non è ripartire.
Il lavoro da fare è chiudere le capability mancanti una alla volta.

## Prossima capability obbligatoria

PROMETEO_PRODUCT_CORE_CLOSURE_V1

Questa sarà la checklist tecnica verificabile per trasformare la roadmap in chiusura reale di backend, PWA, TL Chat, planner ed eventi.
