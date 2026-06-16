# PROMETEO - NUCLEO

Status: ACTIVE - SYNTHETIC CORE
Type: anti-entropy summary
Runtime impact: NONE

## Missione

PROMETEO trasforma conoscenza operativa dispersa in conoscenza interrogabile e verificabile per supportare il Team Leader.

PROMETEO non decide la produzione.

PROMETEO organizza, struttura e rende recuperabile la conoscenza operativa reale, affinche il Team Leader possa decidere in modo piu rapido, coerente e tracciabile.

L autorita finale resta sempre umana.

## Realta operativa

PROMETEO esiste solo se rappresenta correttamente la produzione reale.

Gli elementi fondamentali sono:

- ordini da produrre;
- articoli e disegni;
- componenti e materiali;
- stazioni operative;
- eventi di produzione;
- vincoli reali di reparto;
- conoscenza operativa del Team Leader.

Se la rappresentazione del dominio reale e errata, ogni livello superiore perde valore.

## Modello dominio

Cuore architetturale:

Order -> Route -> Station -> ProductionEvent

Principio:

- la Route definisce cio che puo accadere;
- il ProductionEvent registra cio che e accaduto;
- PROMETEO deve preservare questa separazione.

## Fonti autorevoli

Gerarchia vincolante:

1. Specifica di finitura reale.
2. Conferma Team Leader.
3. BOM reale.
4. Fonti derivate.
5. Inferenze AI.

Le fonti inferiori non possono prevalere sulle fonti superiori.

Specifica reale e conferma TL prevalgono su BOM, cache, preview e inferenza AI.

## Regole dominio fondamentali

- ZAW1 e ZAW2 non sono intercambiabili.
- ZAW1_2 non significa ZAW2.
- CP finale e obbligatorio quando richiesto.
- COLLAUDO_VERTICALE e modalita macchina CP, non postazione separata.
- Il Team Leader puo effettuare override motivato.
- Nessuna route puo essere inventata.

## Livelli di certezza

CERTO:

- confermato da fonte autorevole.

INFERITO:

- deducibile, ma non confermato.

DA_VERIFICARE:

- evidenza insufficiente, contraddittoria o incompleta.

Principio:

CERTO > INFERITO > DA_VERIFICARE.

Mai il contrario.

## Ruoli

Team Leader:

- decide.

PROMETEO Core:

- organizza il dominio.

Planner:

- suggerisce.

ATLAS Engine:

- analizza, segnala e spiega.

LLM:

- assiste.

Nessuno di questi sostituisce il Team Leader.

## Cosa non e PROMETEO

PROMETEO non e:

- ERP;
- SAP;
- MES completo;
- agente autonomo;
- planner autonomo;
- sistema che autorizza decisioni produttive.

## Asset principali

Il valore del sistema risiede in:

1. Dominio reale.
2. Specifiche reali.
3. Conoscenza Team Leader.
4. Eventi di produzione.

Non nell AI.

L AI e un modulo di supporto.

## Priorita strategiche

Ordine attuale:

1. Guardrail.
2. Densificazione dominio reale.
3. Retrieval controllato.
4. Eval.
5. Validator.
6. AI controllata.

Fine-tuning e agenti autonomi non sono priorita.

## Principio finale

PROMETEO deve conoscere piu codici di quanti ne deve pianificare.

L obiettivo non e automatizzare il Team Leader.

L obiettivo e rendere il dominio produttivo comprensibile, interrogabile e verificabile, affinche il Team Leader possa decidere meglio.

## Regola anti-entropia

Ogni nuova capability deve essere confrontata con questo nucleo.

Se una proposta non rafforza missione, dominio, fonti, tracciabilita, retrieval, eval o decisione umana verificabile, va respinta o parcheggiata.

Questo documento non sostituisce PROMETEO_MASTER.md.

PROMETEO_NUCLEO.md e una sintesi operativa anti-entropia.
