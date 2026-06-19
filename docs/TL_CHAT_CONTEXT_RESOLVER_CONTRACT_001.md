# TL_CHAT_CONTEXT_RESOLVER_CONTRACT_001

## Status
- capability: TL_CHAT_CONTEXT_RESOLVER_001
- status: CONTRACT_ONLY
- runtime_impact: NONE
- created_for: PROMETEO TL Chat answer discipline
- no_runtime_binding: true
- no_frontend_change: true
- no_planner_binding: true
- no_atlas_binding: true
- no_specs_finitura_real_read: true
- no_smf_real_read: true
- no_data_mutation: true

## Scopo
Definire come TL Chat deve risolvere il contesto candidato prima di rispondere al Team Leader.

Il resolver concettuale serve a classificare la richiesta, rilevare entita minime, selezionare fonti candidate ammissibili e decidere se la risposta puo proseguire, deve restare DA_VERIFICARE, oppure deve fermarsi con stop condition.

Questo contratto non implementa il resolver e non autorizza binding runtime.

## Non-scopo
Questa capability non deve:
- modificare TL Chat;
- modificare UI o frontend;
- collegare planner;
- collegare ATLAS Engine;
- introdurre retrieval runtime;
- creare endpoint;
- leggere specs_finitura reali;
- leggere SMF reale;
- leggere database reale;
- leggere contenuto di fonti indicizzate non autorizzate;
- chiamare LLM;
- promuovere una informazione a CERTO;
- generare decisioni operative;
- modificare dati, metadata, route o memoria.

## Input
Un futuro resolver potra ricevere solo input gia ammessi da capability dedicate:
- question: testo della domanda TL;
- tl_context: contesto dichiarato dal chiamante, se presente;
- article: codice articolo dichiarato nel contesto, se presente;
- station: postazione dichiarata nel contesto, se presente;
- drawing: disegno dichiarato nel contesto, se presente;
- context_source_index_metadata: metadata read-only da indice governato, senza lettura contenuto fonti;
- allowed_source_types: lista chiusa di tipologie fonte ammesse;
- caller: chiamante dichiarato;
- dry_run: true obbligatorio in fase preview;
- evidence_policy: policy di classificazione FATTO, INFERENZA, DA_VERIFICARE.

Input vietati:
- path arbitrari;
- contenuto grezzo da specs_finitura reale;
- SMF reale;
- database reale;
- immagini/PDF/Excel reali;
- prompt libero non classificato;
- dati produttivi reali;
- richieste di apply, write, update o route override.

## Output
Il resolver deve produrre solo un risultato descrittivo:
- ok: bool;
- blocked: bool;
- block_reason: string | null;
- intent_class: enum;
- detected_entities: oggetto con entita minime rilevate;
- candidate_sources: lista di fonti candidate ammesse;
- candidate_source_type: enum;
- confidence: enum;
- stop_condition: string | null;
- answer_mode: enum;
- resolution_reason: string;

L'output non deve contenere:
- decisioni operative finali;
- priorita produttive;
- route generate;
- aggiornamenti metadata;
- comandi planner;
- output LLM libero;
- autorizzazioni a scrivere SMF, database o memory.

## Intent class minime
Il resolver deve distinguere almeno:
- SYSTEM_CAPABILITY: domanda sulle capacita del sistema o sui limiti di PROMETEO;
- ARTICLE_OPERATIONAL: domanda operativa legata a un articolo, codice o contesto produttivo;
- EXPLICIT_CANDIDATE_LIST: richiesta esplicita di elenco candidati, anomalie o codici da verificare;
- TURN_WITHOUT_CONTEXT: richiesta di priorita/azione senza contesto sufficiente;
- FAMILY_OR_COMPONENT: domanda su famiglia, componente o classe tecnica dichiarata;
- UNKNOWN_OR_UNSUPPORTED: richiesta non classificabile o non supportata.

Regola di priorita:
- SYSTEM_CAPABILITY prevale su trigger generici di lista candidati;
- EXPLICIT_CANDIDATE_LIST si attiva solo se la richiesta e esplicita;
- ARTICLE_OPERATIONAL richiede codice articolo o contesto equivalente dichiarato;
- TURN_WITHOUT_CONTEXT non puo produrre azione operativa.

## Entity detection minima
Il resolver puo rilevare solo entita dichiarate o estratte in modo deterministico:
- article_code: codice articolo a 5 cifre, con eventuale suffisso letterale gia presente;
- station: postazione dichiarata nel testo o nel contesto;
- drawing: disegno dichiarato nel contesto;
- family_or_component: famiglia o componente presente in fonte ammessa;
- source_id: id fonte presente in context_source_index metadata;
- requested_action: tipo di richiesta, se esplicito.

Regole:
- non inferire route senza evidenza;
- non inferire ZAW2 da ZAW1 o ZAW1_2;
- non inferire HENN senza fonte confermata;
- non usare immagini o PDF reali come base;
- se un codice articolo e assente, non inventarlo;
- se piu codici sono presenti, segnalare ambiguita.

## Candidate source type
Tipologie candidate ammesse in futuro, solo se autorizzate da capability dedicate:
- ARTICLE_METADATA: metadata articolo normalizzati e read-only;
- LIFECYCLE_REGISTRY: registro lifecycle read-only;
- ARTICLE_SUMMARY: sintesi articolo governata;
- PREVIEW_PROFILE: profilo preview non operativo;
- CONTEXT_SOURCE_INDEX_METADATA: metadata dell'indice fonti, senza lettura contenuto;
- MEMORY_POLICY_METADATA: policy memory o retrieval governata;
- GOVERNANCE_CONTRACT: documenti contract rilevanti;
- NONE: nessuna fonte candidata ammissibile.

Tipologie vietate:
- SPECS_FINITURA_REAL;
- SMF_REAL;
- DATABASE_REAL;
- IMAGE_REAL;
- PDF_REAL;
- EXCEL_REAL;
- FREE_LLM_MEMORY;
- PLANNER_RUNTIME;
- ATLAS_RUNTIME.

## Confidence
La confidence del resolver riguarda solo la qualita della risoluzione del contesto candidato, non la verita operativa finale.

Valori ammessi:
- CERTO: ammesso solo se ereditato da fonte gia autorevole e non promosso dal resolver;
- INFERENZA: candidato plausibile ma non sufficiente per decisione operativa;
- DA_VERIFICARE: fonte mancante, incompleta, ambigua o non autorevole;
- BLOCCANTE: risposta non producibile senza violare confini o senza contesto minimo.

Regole:
- il resolver non promuove mai INFERENZA o DA_VERIFICARE a CERTO;
- il resolver non trasforma evidence candidate in decisione operativa;
- se manca authority, confidence deve essere DA_VERIFICARE o BLOCCANTE;
- se la fonte e sensibile o vietata, il resolver deve bloccare;
- la conferma TL e la specifica reale prevalgono sempre su ogni candidato.

## Stop condition
Il resolver deve fermarsi se:
- manca il codice articolo per una domanda article-specific;
- manca contesto ordine/lotto/stato/evento per una richiesta di priorita turno;
- il codice e assente o ambiguo;
- viene richiesta una route non supportata da fonte;
- viene richiesta lettura di specs_finitura reale;
- viene richiesta lettura SMF reale;
- viene richiesta lettura di immagini/PDF/Excel reali;
- viene richiesta scrittura su memory, database, SMF o metadata;
- viene richiesto planner, ATLAS Engine o LLM operativo;
- la fonte candidata e fuori dai path ammessi;
- authority o confidence sono mancanti;
- la domanda richiede una capability non implementata;
- la risposta richiederebbe promozione automatica a CERTO.

## Forbidden actions
Il contratto vieta:
- runtime implementation;
- TL Chat binding;
- frontend change;
- planner binding;
- ATLAS Engine binding;
- governed_retrieval.py binding;
- endpoint creation;
- LLM generation;
- autonomous decision;
- route override;
- production priority;
- metadata update;
- memory write automation;
- DB write;
- SMF write;
- specs_finitura real read;
- SMF real read;
- image/PDF/Excel real read;
- context source content read without dedicated contract;
- promotion to CERTO.

## Esempi obbligatori

### Esempio 1: articolo 12514
Input:
- question: "Cosa sai del 12514?"
- context: vuoto o generico.

Risoluzione attesa:
- intent_class: ARTICLE_OPERATIONAL;
- detected_entities.article_code: "12514";
- candidate_source_type: ARTICLE_METADATA, LIFECYCLE_REGISTRY, ARTICLE_SUMMARY o NONE secondo fonti ammesse disponibili;
- confidence: DA_VERIFICARE se manca fonte autorevole;
- stop_condition: null solo se esiste fonte candidata ammessa;
- forbidden: inferire route, stazioni, ZAW2, HENN o CP senza fonte.

Risposta ammessa:
- descrivere solo cosa e supportato da fonte ammessa;
- dichiarare DA_VERIFICARE se il dato non e disponibile;
- chiedere conferma TL o fonte se serve decisione operativa.

### Esempio 2: domanda sistema
Input:
- question: "PROMETEO puo aiutarmi a classificare una nuova specifica?"

Risoluzione attesa:
- intent_class: SYSTEM_CAPABILITY;
- detected_entities.article_code: null;
- candidate_source_type: GOVERNANCE_CONTRACT o CONTEXT_SOURCE_INDEX_METADATA;
- confidence: INFERENZA o DA_VERIFICARE secondo fonte disponibile;
- stop_condition: null se la risposta resta sui limiti del sistema.

Risposta ammessa:
- spiegare capacita e limiti;
- dire che PROMETEO puo supportare classificazione governata solo con fonte leggibile e autorizzata;
- non promettere creazione automatica di route certe;
- non trasformare la domanda in lista candidati.

### Esempio 3: codice assente
Input:
- question: "Cosa devo fare adesso in reparto?"

Risoluzione attesa:
- intent_class: TURN_WITHOUT_CONTEXT;
- detected_entities.article_code: null;
- candidate_source_type: NONE;
- confidence: BLOCCANTE;
- stop_condition: missing_operational_context.

Risposta ammessa:
- chiedere articolo, ordine, lotto, stato o evento;
- non produrre priorita produttiva;
- non chiamare planner;
- non inventare contesto.

## Test minimi futuri
Una futura capability guard o test-only dovra verificare:
- il contratto esiste;
- tutte le sezioni obbligatorie sono presenti;
- 12514 viene trattato come article_code candidato senza inferenze route;
- una domanda sistema viene classificata come SYSTEM_CAPABILITY;
- una domanda senza codice operativo produce stop condition;
- SYSTEM_CAPABILITY prevale su candidate-list non esplicita;
- EXPLICIT_CANDIDATE_LIST richiede richiesta esplicita;
- candidate_source_type resta in enum chiuso;
- confidence non viene promossa a CERTO;
- fonti vietate sono elencate e bloccate;
- nessun runtime binding e autorizzato;
- nessuna modifica a TL Chat, frontend, planner o ATLAS Engine e autorizzata.

## Criteri di chiusura
La capability TL_CHAT_CONTEXT_RESOLVER_001 e chiudibile quando:
- il documento contract-only e presente;
- scopo e non-scopo sono espliciti;
- input e output concettuali sono definiti;
- intent_class minime sono definite;
- entity detection minima e definita;
- candidate_source_type e definito;
- confidence e definita senza promozione a CERTO;
- stop condition e forbidden actions sono definite;
- gli esempi 12514, domanda sistema e codice assente sono presenti;
- test minimi futuri sono elencati;
- non sono state modificate UI, TL Chat, runtime, planner, ATLAS Engine, memory o dati reali.

## Final verdict
This contract defines TL Chat context resolution as contract-only governance.
It authorizes no runtime binding, no TL Chat patch, no frontend change, no planner integration, no ATLAS Engine integration, no LLM generation, no endpoint exposure, no real source reading, no promotion to CERTO, and no data mutation.
