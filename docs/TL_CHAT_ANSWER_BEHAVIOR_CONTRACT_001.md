# TL_CHAT_ANSWER_BEHAVIOR_CONTRACT_001

## Status
- status: CONTRACT_ONLY
- runtime_impact: NONE
- ui_change: false
- frontend_change: false
- planner_binding: false
- atlas_engine_binding: false
- retrieval_runtime_change: false
- endpoint_change: false
- llm_free_mode: false

## Purpose
Definire il comportamento risposta della TL Chat dopo la chiusura della capability TL INTERFACE ONLY.

La TL Chat deve rispondere in modo utile, disciplinato e verificabile, senza fingere capacità non presenti e senza trasformare domande generali in output operativi non richiesti.

## Scope
Questo contratto riguarda solo il comportamento risposta della TL Chat.

Ammesso:
- classificare i tipi di domanda TL;
- definire cosa la TL Chat può rispondere;
- definire cosa la TL Chat non deve rispondere;
- definire fonti ammesse e gerarchia;
- definire stop condition;
- definire test minimi futuri.

Non ammesso:
- modificare UI o frontend;
- collegare planner;
- collegare ATLAS Engine;
- introdurre retrieval runtime nuovo;
- creare endpoint;
- fare runtime patch;
- fare refactor backend;
- introdurre LLM libero;
- usare PROMETEOWIKI come fonte runtime.

## Context
TL INTERFACE ONLY e chiusa.

Fatti noti:
- UI prompt-like: chiusa;
- copy sorgente: corretto;
- branch fix UI: rimosso;
- repo pulito al momento di apertura capability;
- problema residuo: comportamento risposta TL Chat, non interfaccia.

## Current Behavior Summary
La TL Chat attuale non e una chat LLM conversazionale libera.

E un router deterministico contract-v1 che:
- riceve domanda e context;
- cerca un codice articolo nella domanda o nel context;
- usa fonti locali read-only se disponibili;
- gestisce alcune domande speciali senza articolo;
- aggiunge un evidence pack governato read-only;
- restituisce TLChatResponse.

Rischio osservato: una domanda di capacita del sistema puo essere interpretata come richiesta di candidati intake o densificazione.

## Answer Classification
Ogni domanda TL deve essere classificata prima della risposta.

Classi minime:
- SYSTEM_CAPABILITY: domanda su cosa PROMETEO o TL Chat puo fare;
- ARTICLE_OPERATIONAL: domanda operativa con codice articolo;
- EXPLICIT_CANDIDATE_LIST: richiesta esplicita di lista codici/candidati/staging/densificazione;
- TURN_WITHOUT_CONTEXT: domanda turno senza articolo, ordine, lotto, stato board o evento;
- FAMILY_OR_COMPONENT: domanda su famiglia tecnica o componente;
- UNKNOWN_OR_UNSUPPORTED: domanda non classificabile con fonti disponibili.

## Priority Rules
Le domande SYSTEM_CAPABILITY devono avere priorita sui trigger di lista candidati.

Una risposta di lista candidati e ammessa solo quando la domanda richiede esplicitamente una lista o elenco di codici.

Esempi validi per lista candidati:
- quali codici sono candidati alla densificazione;
- elenca i codici da review TL;
- quali codici staging posso portare avanti.

Esempi non validi per lista candidati:
- hai capacita di implementare nuovi codici;
- puoi usare screenshot o foto della specifica;
- come gestisci una nuova specifica di finitura;
- puoi creare un nuovo codice partendo dalla descrizione TL.

## Allowed Answers
La TL Chat puo:
- rispondere da specifica o metadata articolo quando presenti;
- usare lifecycle registry read-only;
- usare article summary read-only;
- usare preview profile read-only;
- elencare candidati solo se la richiesta e esplicita;
- dichiarare DA_VERIFICARE quando manca fonte autorevole;
- chiedere codice articolo, ordine, lotto, stato board o evento quando il contesto e insufficiente;
- spiegare limiti e capacita del sistema senza promettere automazioni;
- richiedere conferma TL quando una risposta puo influenzare decisioni operative.

## Forbidden Answers
La TL Chat non deve:
- inventare route, componenti, postazioni o stati;
- dichiarare CERTO senza fonte autorevole;
- trasformare una domanda di capacita in lista candidati;
- promettere implementazione automatica di nuovi codici;
- dichiarare di poter leggere screenshot o foto se non esiste pipeline autorizzata;
- usare evidence pack come autorizzazione operativa;
- decidere priorita produttive senza contesto minimo;
- collegare planner, ATLAS Engine o runtime non autorizzati;
- usare un LLM libero come fonte;
- scrivere SMF, database, planner o file operativi.

## Source Policy
Gerarchia fonti:
1. specifica reale confermata e conferma TL;
2. metadata articolo normalizzato;
3. article summary;
4. lifecycle registry;
5. preview profile;
6. registri locali read-only;
7. evidence pack governato solo come preview read-only;
8. inferenza modello solo come DA_VERIFICARE e mai come fonte autorevole.

Fonti vietate in questa capability:
- planner runtime;
- ATLAS Engine binding;
- retrieval runtime nuovo;
- endpoint nuovi;
- DB write;
- SMF write;
- OCR runtime nuovo;
- LLM libero;
- screenshot o foto come fonte diretta senza pipeline autorizzata.

## Expected System Capability Answer
Per domande tipo capacita nuovi codici, screenshot o foto, la risposta deve dire:
- PROMETEO puo supportare intake e classificazione solo con fonte leggibile e autorizzata;
- puo aiutare a strutturare dati e distinguere CERTO, INFERITO, DA_VERIFICARE;
- non puo creare route certa senza specifica e conferma TL;
- non deve scrivere dati reali senza conferma;
- screenshot o foto richiedono pipeline dedicata o testo estratto;
- se il dato non e verificabile, resta DA_VERIFICARE.

## Stop Conditions
La TL Chat deve fermarsi o chiedere chiarimento quando:
- manca codice articolo per una risposta articolo-specifica;
- manca ordine, lotto, stato board o evento per una priorita turno;
- la domanda richiede capacita non ancora implementata;
- la fonte non e autorevole;
- la risposta comporterebbe scrittura o decisione automatica;
- servirebbe planner, ATLAS Engine, retrieval nuovo o runtime non autorizzato.

## Output Format
Formato minimo consigliato:
- RISPOSTA: frase operativa breve;
- STATO: FATTO, INFERENZA, DA_VERIFICARE, BLOCCANTE o RICHIESTA_CONFERMA_TL;
- MOTIVO: perche la risposta e limitata o affidabile;
- AZIONE TL: prossimo dato richiesto o controllo consigliato.

Il formato puo essere compresso quando la risposta e semplice, ma non deve nascondere incertezza o limiti.

## Minimal Future Tests
Test 1 - system capability does not list candidates:
Domanda: hai capacita di implementazione nuovi codici descritti dal TL oppure attraverso screenshot o foto della specifica di finitura?
Atteso: non elenca candidati intake; spiega capacita e limiti; richiede fonte leggibile o pipeline autorizzata; non promette scrittura automatica.

Test 2 - candidate list explicit request preserved:
Domanda: quali codici sono candidati alla densificazione?
Atteso: mantiene risposta lista candidati da staging preview, se fonte disponibile.

Test 3 - turn question without context remains guarded:
Domanda: cosa devo fare ora?
Atteso: non genera priorita; chiede articolo, ordine, lotto, stato board o evento.

Test 4 - unknown article remains DA_VERIFICARE:
Domanda: che criticita ha il 99999?
Atteso: non inventa; risponde DA_VERIFICARE o non disponibile nel profilo attivo.

Test 5 - screenshot capability remains bounded:
Domanda: puoi leggere una foto della specifica e creare il codice?
Atteso: spiega che serve pipeline autorizzata o input testuale estratto; non crea profilo operativo certo.

## Relation With PROMETEOWIKI
PROMETEOWIKI puo essere valutata in capability separata.

In questo contratto:
- PROMETEOWIKI non e fonte runtime;
- nessun file wiki viene creato;
- nessun binding TL Chat viene introdotto.

## Final Verdict
CONTINUE come contratto minimo.

La capability resta CONTRACT_ONLY e non autorizza runtime patch.
