# PROMETEO MASTER
Documento semantico primario del progetto PROMETEO.
Scopo: verita operativa, governance architetturale, contratto AI, anti-frammentazione.

## SOURCE OF TRUTH POLICY
PROMETEO adotta una gerarchia di precedenza vincolante.

1. SPECIFICA REALE
2. CONFERMA TL
3. PROMETEO_MASTER
4. STRUTTURA DOMINIO
5. AI INFERENCE
6. CACHE/PREVIEW/EXPORT

Regole vincolanti:
- Nessuna duplicazione semantica stabile fuori da questo MASTER.
- I documenti esterni sono implementativi, tecnici o temporanei.
- In conflitto prevalgono SPECIFICA REALE + CONFERMA TL + PROMETEO_MASTER.
- TL resta autorita operativa finale.
- AI non puo sovrascrivere verita dominio confermate.

## SEMANTIC AUTHORITY REFERENCES
- Governance authority: sezioni 02, 11, 20
- Domain authority: sezioni 03, 04, 12, 14, 16
- Planner authority: sezione 06
- Event authority: sezione 07
- AI/Executor authority: sezioni 09, 10
- TL operational authority: sezioni 05, 17, 18
- World model authority: sezioni 25, 26, 27, 28, 29, 30, 31

## SEMANTIC NORMALIZATION BASELINE
Stati canonici obbligatori:
- CERTO
- INFERITO
- DA_VERIFICARE
- BLOCCATO
- STANDARD
- REFERENCE_ONLY

Stazioni/processi canonici obbligatori:
- ZAW1
- ZAW2
- PIDMILL
- HENN
- CP
- FORNO
- ULTRASUONI
- WINTEC

Termini planner canonici obbligatori:
- planner_eligible
- route_status
- operational_class
- confidence
- shared_component
- blocking_constraint

## SEMANTIC INDEX LAYER
### RULE INDEX
- ARCH-BOUNDARY-001 -> 02
- GOV-SCOPE-001 -> 02
- DOMAIN-CHAIN-001 -> 03
- STATION-TAXONOMY-001 -> 04
- TL-AUTHORITY-001 -> 05
- PLANNER-BOUNDARY-001 -> 06
- PLANNER-BLOCKING-001 -> 06
- EVENT-TAXONOMY-001 -> 07
- ATLAS-GOVERNANCE-001 -> 08
- AI-GOVERNANCE-001 -> 09
- EXECUTOR-GATE-001 -> 10
- GUARD-OBSERVABILITY-001 -> 11
- SHARED-COMPONENT-001 -> 15
- TL-CONTRACT-001 -> 17
- TL-OVERRIDE-001 -> 18
- SECURITY-PRIVACY-001 -> 19
- MASTER-ANTIFRAG-001 -> 20
- STATION-CAUSALITY-001 -> 25
- EVENT-CAUSALITY-001 -> 26
- COMPONENT-GRAPH-001 -> 27
- TL-COGNITION-001 -> 28
- CONFIDENCE-SEMANTICS-001 -> 29
- PLANNER-EXPLAINABILITY-001 -> 30
- OPGRAPH-SEMANTICS-001 -> 32
- CONSTRAINT-PROPAGATION-001 -> 33
- MULTIORDER-INTERACTION-001 -> 34
- TEMPORAL-OPERATIONS-001 -> 35
- REASONING-BOUNDARY-001 -> 36
- COGNITION-MODEL-001 -> 39
- SIMULATION-SEMANTICS-001 -> 40
- OPERATIONAL-RISK-001 -> 41
- RECOVERY-STABILIZATION-001 -> 42
- OPERATIONAL-MEMORY-001 -> 43
- HITL-COGNITION-001 -> 44
- SIMULATION-EXPLAINABILITY-001 -> 45
- COGNITIVE-STABILIZATION-001 -> 47
- STRATEGIC-SEQUENCING-001 -> 48
- RESILIENCE-SEMANTICS-001 -> 49
- EQUILIBRIUM-MODEL-001 -> 50
- STRATEGIC-PLANNER-001 -> 51
- UNCERTAINTY-TRUST-001 -> 52
- META-REASONING-001 -> 53
- STRATEGIC-HITL-001 -> 54
- STRATEGIC-EXPLAINABILITY-001 -> 55
- STRATEGIC-STABILIZATION-001 -> 57
- AUTONOMIC-GOVERNANCE-001 -> 58
- COGNITIVE-INTEGRITY-001 -> 59
- AUTONOMIC-SUPERVISION-001 -> 60
- STRATEGIC-CONTAINMENT-001 -> 61
- GOVERNANCE-MEMORY-001 -> 62
- AUTONOMIC-TRUST-SAFETY-001 -> 63
- AUTONOMIC-EXPLAINABILITY-001 -> 64
- AUTONOMIC-STABILIZATION-001 -> 66
- INSTITUTIONAL-REASONING-001 -> 67
- ORGANIZATIONAL-INTELLIGENCE-001 -> 68
- LONGHORIZON-OPERATIONS-001 -> 69
- INSTITUTIONAL-TRUST-001 -> 70
- CROSSCONTEXT-COGNITION-001 -> 71
- INSTITUTIONAL-MEMORY-001 -> 72
- INSTITUTIONAL-HITL-001 -> 73
- INSTITUTIONAL-EXPLAINABILITY-001 -> 74
- INSTITUTIONAL-STABILIZATION-001 -> 76
- ECOSYSTEM-OPERATIONS-001 -> 77
- FEDERATED-COGNITION-001 -> 78
- ECOSYSTEM-RESILIENCE-001 -> 79
- CIVSCALE-MEMORY-001 -> 80
- CROSSINSTITUTIONAL-TRUST-001 -> 81
- ECOSYSTEM-HITL-001 -> 82
- ECOSYSTEM-EXPLAINABILITY-001 -> 83
- ECOSYSTEM-STABILIZATION-001 -> 85

### DOMAIN INDEX
- Order -> Route -> Station -> ProductionEvent -> sezione 03
- confidence -> sezioni 14, 23, 29
- operational_class -> sezioni 14, 23, 29
- planner_eligible -> sezioni 06, 23, 29

### STATION INDEX
- ZAW1 -> 04, 25
- ZAW2 -> 04, 25
- PIDMILL -> 04, 25
- HENN -> 04, 25
- CP -> 04, 25
- FORNO -> 04, 25
- ULTRASUONI -> 04, 25
- WINTEC -> 04, 25

### EVENT INDEX
- OPEN/BLOCKING semantics -> 07, 26
- blocking_constraint linkage -> 06, 07, 26
- TL confirmation events -> 17, 18, 26

### ARTICLE INDEX
- articoli confermati -> 13
- shared_component -> 15, 27
- specifiche finitura -> 16

### POLICY INDEX
- AI policy -> 09
- Executor policy -> 10
- Guard rails -> 11
- TL chat contract -> 17
- Override umano -> 18
- Security & privacy -> 19

## WORLD MODEL INDEX LAYER
### CAUSAL INDEX
- station causality core -> 25
- event propagation core -> 26
- shared component fanout -> 27

### STATION RELATION INDEX
- ZAW1 saturation propagation -> 25
- ZAW2 route-specific dependency -> 25
- PIDMILL coupling chains -> 25
- CP final validation blocking -> 25

### EVENT PROPAGATION INDEX
- BLOCKING and CP_BLOCK escalation -> 26
- SATURATION and SHARED_COMPONENT_CONFLICT spread -> 26
- TL_OVERRIDE precedence event -> 26, 28

### COMPONENT IMPACT INDEX
- shared_component amplification -> 27
- bottleneck multiplication -> 27
- dependency fanout -> 27

### TL DECISION INDEX
- prioritization logic -> 28
- override scope/precedence -> 28
- auditability/persistence -> 28

### PLANNER EXPLAINABILITY INDEX
- minimum explanation contract -> 30
- transparency constraints -> 30
- AI validation boundaries -> 30

## OPERATIONAL GRAPH INDEX LAYER
### OPERATIONAL ENTITY INDEX
- Article, Route, Station, Component -> 32
- Event, PlannerDecision, TLOverride -> 32
- Saturation, Constraint, ProductionSequence, DependencyChain -> 32

### RELATIONSHIP INDEX
- depends_on, blocks, amplifies -> 32
- saturates, propagates_to, coupled_with -> 32
- validated_by, constrained_by, escalated_by, overridden_by -> 32

### PROPAGATION INDEX
- station saturation propagation -> 33
- component shortage propagation -> 33
- CP blocking propagation -> 33
- route mismatch propagation -> 33
- PIDMILL dependency propagation -> 33
- shared component propagation -> 33
- planner conflict propagation -> 33

### CONSTRAINT INDEX
- hard blocking constraints -> 33
- soft warning constraints -> 33
- TL escalation constraints -> 33

### REASONING INDEX
- AI MAY / AI MAY NOT boundaries -> 36
- explainable reasoning chain contract -> 30, 37
- TL final authority boundary -> 05, 18, 36

### TEMPORAL SEMANTICS INDEX
- backlog accumulation -> 35
- saturation persistence -> 35
- unresolved OPEN persistence -> 26, 35
- recovery/stabilization conditions -> 35

## OPERATIONAL COGNITION INDEX LAYER
### OPERATIONAL COGNITION INDEX
- bottleneck anticipation, dynamic prioritization -> 39
- adaptive sequencing, station balancing -> 39
- instability containment, anti-fragile adaptation -> 39

### SIMULATION SEMANTICS INDEX
- propagation forecasting -> 40
- saturation/backlog evolution -> 40
- cascading instability, route destabilization -> 40
- planner stress, sequence degradation, station collapse risk -> 40

### RISK SEMANTICS INDEX
- local/systemic instability -> 41
- cascading saturation, planner degradation -> 41
- CP overload, OPEN accumulation risk -> 41
- dependency amplification, shared-component explosion risk -> 41

### RECOVERY INDEX
- de-saturation pathways -> 42
- stabilization windows -> 42
- bottleneck relief, planner recovery mode -> 42
- partial and cascading recovery -> 42

### OPERATIONAL MEMORY INDEX
- unresolved issue persistence -> 43
- repeated instability patterns -> 43
- saturation memory and recurring bottlenecks -> 43
- TL experiential precedent influence -> 43

### HUMAN-IN-THE-LOOP INDEX
- AI bounded cognition support -> 44
- TL contextual authority and final decision -> 44
- operational trust boundaries -> 44

## STRATEGIC INTELLIGENCE INDEX LAYER
### STRATEGIC SEQUENCING INDEX
- anticipatory and saturation-aware sequencing -> 48
- bottleneck containment and backlog shaping -> 48
- recovery-oriented and throughput-preserving sequencing -> 48

### RESILIENCE INDEX
- graceful degradation and controlled instability -> 49
- anti-collapse behavior and overload absorption -> 49
- adaptive stabilization and strategic buffering -> 49

### EQUILIBRIUM INDEX
- operational and saturation equilibrium -> 50
- oscillatory states and persistent instability -> 50
- equilibrium recovery and hidden instability accumulation -> 50

### UNCERTAINTY INDEX
- uncertainty propagation and confidence degradation -> 52
- trust-aware escalation and unstable inference detection -> 52
- confidence-about-confidence semantics -> 52

### META-REASONING INDEX
- reasoning reliability assessment -> 53
- explainability sufficiency and escalation necessity -> 53
- semantic inconsistency awareness -> 53

### STRATEGIC HITL INDEX
- TL strategic stabilizer authority -> 54
- AI bounded strategic support -> 54
- contextual intelligence superiority -> 54

## AUTONOMIC GOVERNANCE INDEX LAYER
### AUTONOMIC GOVERNANCE INDEX
- governance self-monitoring and stabilization -> 58
- adaptive governance containment and escalation governance -> 58
- bounded adaptive supervision and controlled adaptation -> 58

### COGNITIVE INTEGRITY INDEX
- semantic drift detection -> 59
- governance coherence and contradiction awareness -> 59
- unstable reasoning and integrity degradation awareness -> 59

### SUPERVISION INDEX
- self-monitoring and self-evaluation -> 60
- confidence self-assessment and reliability checks -> 60
- reasoning chain verification and escalation necessity awareness -> 60

### CONTAINMENT INDEX
- instability and uncertainty containment -> 61
- planner degradation and semantic conflict containment -> 61
- cascading failure prevention and stabilization buffering -> 61

### GOVERNANCE MEMORY INDEX
- governance precedent memory -> 62
- recurring governance failures and escalation patterns -> 62
- institutional operational memory and conflict recurrence -> 62

### AUTONOMIC SAFETY INDEX
- bounded adaptive autonomy and safety boundaries -> 63
- governance trust thresholds and escalation trust gates -> 63
- TL override supremacy and governance rollback semantics -> 63

## INSTITUTIONAL INTELLIGENCE INDEX LAYER
### INSTITUTIONAL REASONING INDEX
- operational continuity and persistent identity -> 67
- long-horizon stabilization and governance continuity -> 67
- institutional escalation memory -> 67

### ORGANIZATIONAL MEMORY INDEX
- distributed operational knowledge -> 68
- inter-shift learning and collective stabilization -> 68
- persistent operational context -> 68

### LONG-HORIZON INDEX
- backlog accumulation and resilience erosion -> 69
- chronic bottlenecks and delayed systemic effects -> 69
- accumulated operational debt and stabilization fatigue -> 69

### INSTITUTIONAL TRUST INDEX
- governance reliability and escalation credibility -> 70
- precedent reliability and trust degradation accumulation -> 70
- historical trust evolution semantics -> 70

### CROSS-CONTEXT INDEX
- pattern transfer and contextual analogy -> 71
- controlled semantic reuse and similarity recognition -> 71
- bounded contextual inference and TL-verifiable transfer -> 71

### INSTITUTIONAL HITL INDEX
- TL continuity supremacy and final validation -> 73
- AI bounded institutional support and continuity analysis -> 73
- human contextual continuity superiority -> 73

## ECOSYSTEM SEMANTIC INDEX LAYER
### ECOSYSTEM OPERATIONS INDEX
- ecosystem continuity and cross-domain dependencies -> 77
- distributed operational equilibrium -> 77
- ecosystem bottleneck propagation and bounded coordination -> 77

### FEDERATED COGNITION INDEX
- federated reasoning and distributed contextual cognition -> 78
- contextual synchronization and interoperability -> 78
- bounded semantic federation and governance alignment -> 78

### ECOSYSTEM RESILIENCE INDEX
- ecosystem degradation and cross-context instability -> 79
- distributed buffering and containment cooperation -> 79
- multi-context recovery coordination -> 79

### DISTRIBUTED MEMORY INDEX
- ecosystem memory and cross-context institutional memory -> 80
- distributed precedents and escalation memory -> 80
- long-range continuity and historical propagation -> 80

### CROSS-INSTITUTIONAL TRUST INDEX
- federated trust boundaries and reliability semantics -> 81
- bounded trust propagation and transfer gates -> 81
- ecosystem reliability awareness and coherence trust -> 81

### ECOSYSTEM HITL INDEX
- contextual human authority preservation -> 82
- bounded AI ecosystem support -> 82
- TL/HITL final escalation boundaries -> 82

## 01. VISIONE SISTEMA
PROMETEO trasforma eventi di produzione in decisioni operative TL spiegabili e controllate.
PROMETEO non sostituisce il TL: fornisce contesto, vincoli, rischi e priorita.

## 02. PRINCIPI ARCHITETTURALI
RULE_ID: ARCH-BOUNDARY-001
CATEGORY: ARCHITECTURE
STATUS: ACTIVE
SOURCE: MASTER
DESCRIPTION: Architettura modulare con confini stabili tra dominio, planner, atlas, executor e API.
CONSTRAINTS: No biforcazioni logiche parallele.
NOTES: Cambi strutturali solo con PR dedicata.

RULE_ID: GOV-SCOPE-001
CATEGORY: GOVERNANCE
STATUS: ACTIVE
SOURCE: MASTER
DESCRIPTION: Ogni patch deve dichiarare scope, impatto dominio e test minimi.
CONSTRAINTS: Modifiche fuori scope bloccate.
NOTES: Anti-regressione progettuale.

## 03. MODELLO DOMINIO
Catena dominio canonica:
Order -> Route -> Station -> ProductionEvent

RULE_ID: DOMAIN-CHAIN-001
CATEGORY: DOMAIN
STATUS: ACTIVE
SOURCE: MASTER
DESCRIPTION: ProductionEvent e traccia operativa canonica.
CONSTRAINTS: Nessun layer puo reinterpretare eventi rompendo la catena dominio.
NOTES: Route definisce possibilita; evento definisce realta.

## 04. STAZIONI E PROCESSI
Stazioni/processi canonici: ZAW1, ZAW2, PIDMILL, HENN, CP, FORNO, ULTRASUONI, WINTEC.

RULE_ID: STATION-TAXONOMY-001
CATEGORY: TAXONOMY
STATUS: ACTIVE
SOURCE: MASTER
DESCRIPTION: La tassonomia stazioni/processi deve usare solo naming canonico.
CONSTRAINTS: Vietati alias non mappati o capitalizzazione incoerente.
NOTES: Normalizzazione obbligatoria in payload, policy e contratti.

## 05. REGOLE TL
RULE_ID: TL-AUTHORITY-001
CATEGORY: TL_POLICY
STATUS: ACTIVE
SOURCE: TL + MASTER
DESCRIPTION: Il TL e autorita finale sulla decisione operativa.
CONSTRAINTS: Nessun apply automatico ad alto impatto senza conferma forte.
NOTES: Conferma forte definita in sezione 18.

## 06. PLANNER RULES
RULE_ID: PLANNER-BOUNDARY-001
CATEGORY: PLANNER_POLICY
STATUS: ACTIVE
SOURCE: MASTER
DESCRIPTION: Il planner produce sequenze e segnali; non muta il dominio.
CONSTRAINTS: No enforcement occulto fuori dalle policy dichiarate.
NOTES: Decision layer separato e spiegabile.

RULE_ID: PLANNER-BLOCKING-001
CATEGORY: PLANNER_POLICY
STATUS: ACTIVE
SOURCE: MASTER
DESCRIPTION: Il planner non puo bypassare blocking_constraint attivi e verificati.
CONSTRAINTS: blocking_constraint prevale su inferenze non confermate.
NOTES: Allineato a route_status, planner_eligible e operational_class.

## 07. EVENT MODEL
RULE_ID: EVENT-TAXONOMY-001
CATEGORY: EVENT_MODEL
STATUS: ACTIVE
SOURCE: MASTER
DESCRIPTION: Eventi OPEN guidano criticita operative; eventi CLOSED non sono anomalie attive.
CONSTRAINTS: Modello eventi coerente tra API, servizi e explainability.
NOTES: Evitare falsi BLOCCATO station-level senza legame ordine-evento.

## 08. ATLAS ENGINE
RULE_ID: ATLAS-GOVERNANCE-001
CATEGORY: AI_ENGINE_POLICY
STATUS: ACTIVE
SOURCE: MASTER
DESCRIPTION: ATLAS e livello decisionale/diagnostico, non writer dominio.
CONSTRAINTS: Nessuna mutazione diretta su DB, SMF o planner state.
NOTES: Produce explainability e merge vincoli.

## 09. AI POLICY
RULE_ID: AI-GOVERNANCE-001
CATEGORY: AI_POLICY
STATUS: ACTIVE
SOURCE: MASTER
DESCRIPTION: AI adapters e tool operano in read-only o strict-gated.
CONSTRAINTS: AI non puo override di verita dominio confermate da SPECIFICA REALE + TL.
NOTES: Nessuna promozione automatica a CERTO da fonti derivate.

## 10. EXECUTOR POLICY
RULE_ID: EXECUTOR-GATE-001
CATEGORY: EXECUTOR_POLICY
STATUS: ACTIVE
SOURCE: MASTER
DESCRIPTION: Executor ammesso solo con decision context esplicito.
CONSTRAINTS: No decision context -> deny admission; no mutazione autonoma domain truth.
NOTES: Tool scope minimo e read-only per default.

## 11. GUARD RAILS
RULE_ID: GUARD-OBSERVABILITY-001
CATEGORY: SAFETY_POLICY
STATUS: ACTIVE
SOURCE: MASTER
DESCRIPTION: No API bypass, no silent failure, no data leak.
CONSTRAINTS: Errori critici devono produrre segnale osservabile o errore esplicito.
NOTES: Copertura con test contrattuali sintetici.

## 12. DOMAIN KNOWLEDGE
Conoscenza dominio valida se derivata da:
- specifica reale
- conferma TL
- mapping operativo verificabile

## 13. ARTICOLI CONFERMATI
Gli articoli confermati appartengono a base autorevole validata.
Preview e inferenze non aggiornano automaticamente stato confermato.

## 14. CLASSIFICAZIONE ROUTE
Vocabolario canonico:
- confidence: CERTO | INFERITO | DA_VERIFICARE
- operational_class: STANDARD | REFERENCE_ONLY | BLOCCATO
- route_status: CERTO | INFERITO | DA_VERIFICARE | BLOCCATO
- planner_eligible: true | false

Regola: promozione a CERTO solo con evidenza autorevole esplicita.

## 15. SHARED COMPONENTS
RULE_ID: SHARED-COMPONENT-001
CATEGORY: CONSTRAINTS_POLICY
STATUS: ACTIVE
SOURCE: MASTER
DESCRIPTION: shared_component e vincolo strategico multi-articolo.
CONSTRAINTS: Nessun hardcoding per singolo componente.
NOTES: Modellazione tramite cluster/graph derivato da BOM, subordinato a fonte autorevole.

## 16. SPECIFICHE FINITURA
SPECIFICA DI FINITURA e fonte primaria tecnica articolo.
Assenza in supporto non equivale ad assenza operativa.

## 17. TL CHAT CONTRACT
RULE_ID: TL-CONTRACT-001
CATEGORY: TL_CHAT_POLICY
STATUS: ACTIVE
SOURCE: MASTER
DESCRIPTION: Pipeline minima obbligatoria per modifiche operative via chat.
CONSTRAINTS: estrazione comando -> rischio -> preview/diff -> conferma esplicita -> apply guarded -> audit log -> rollback_id.
NOTES: Nessun apply diretto senza preview/diff.

## 18. OVERRIDE UMANO
RULE_ID: TL-OVERRIDE-001
CATEGORY: OVERRIDE_POLICY
STATUS: ACTIVE
SOURCE: TL + MASTER
DESCRIPTION: Override HIGH richiede challenge contestuale esplicita.
CONSTRAINTS: "ok", "si", "vai" non sono conferme valide; TL resta autorita finale.
NOTES: Maker-checker/4-eyes ammesso per casi critici.

## 19. SECURITY & PRIVACY
RULE_ID: SECURITY-PRIVACY-001
CATEGORY: SECURITY_POLICY
STATUS: ACTIVE
SOURCE: MASTER
DESCRIPTION: Nessun dato reale sensibile in Git.
CONSTRAINTS: No versionamento di immagini/PDF/spec private; test e guard solo sintetici.
NOTES: Policy valida per AI, planner, exporter e tooling.

## 20. GIT/GITHUB WORKFLOW
RULE_ID: MASTER-ANTIFRAG-001
CATEGORY: GOVERNANCE_POLICY
STATUS: ACTIVE
SOURCE: MASTER
DESCRIPTION: Nessuna PR puo introdurre semantica dominio stabile fuori dal MASTER.
CONSTRAINTS: Vietato definire fuori MASTER nuove policy planner/AI, tassonomie station/process/event, regole permanenti di governance.
NOTES: I documenti esterni restano supporto implementativo o archivio.

## 21. DEPLOYMENT MODEL
Stack target: FastAPI + PostgreSQL su Railway.
Compatibilita locale con fallback SQLite solo per test/dev controllato.

## 22. FUTURE ROADMAP
Evoluzione prevista:
- stati decisionali BLOCCATO/DEFER/ALLOW/BOOST
- integrazione severita evento nel decision layer
- vincoli shared_component espliciti e spiegabili

## 23. GLOSSARIO
- CERTO: informazione confermata da fonte autorevole.
- INFERITO: deduzione plausibile non ancora confermata.
- DA_VERIFICARE: informazione incompleta, ambigua o conflittuale.
- BLOCCATO: stato operativo non ammissibile senza risoluzione vincolo.
- STANDARD: classe operativa ordinaria.
- REFERENCE_ONLY: classe non idonea a uso planner operativo.
- ASK_TL: richiesta mirata al Team Leader.

## 24. APPENDICI TECNICHE MINIME
Appendici ammesse solo per riferimenti tecnici stabili e non semantici.
Vietato inserire:
- log CI/pytest
- runtime traces
- cronologia PR
- note debug temporanee
- dump dati/cache

## 25. STATION CAUSALITY MODEL
RULE_ID: STATION-CAUSALITY-001
CATEGORY: WORLD_MODEL_STATIONS
STATUS: ACTIVE
SOURCE: MASTER + TL
DESCRIPTION: Le stazioni sono nodi causali con dipendenze di sequenza, saturazione e blocco.
CONSTRAINTS:
- CP e validazione finale bloccante: senza CP valido il flusso resta BLOCCATO.
- Saturazione ZAW1/ZAW2 propaga effetti downstream su PIDMILL, CP e uscita turno.
- PIDMILL introduce catene di dipendenza quando riceve semi-lavorati da ZAW/HENN.
- HENN puo creare accodamenti upstream su componenti metallici dedicati.
- FORNO, ULTRASUONI, WINTEC agiscono come vincoli di percorso dove previsti dalla route.
- ZAW1 e ZAW2 non sono intercambiabili senza conferma esplicita di route.
NOTES:
- Impatti upstream: saturazione a valle retroagisce su rilascio ordini a monte.
- Impatti downstream: un collo di bottiglia anticipato altera priorita di sequenza.

## 26. EVENT CAUSALITY MODEL
RULE_ID: EVENT-CAUSALITY-001
CATEGORY: WORLD_MODEL_EVENTS
STATUS: ACTIVE
SOURCE: MASTER + TL
DESCRIPTION: Gli eventi operativi definiscono propagazione causale su ordini, stazioni e decisione planner.
CONSTRAINTS:
- Categorie canoniche: OPEN, BLOCKING, SATURATION, QUALITY, COMPONENT_SHORTAGE, ROUTE_MISMATCH, TL_OVERRIDE, PLANNER_EXCEPTION, CP_BLOCK, SHARED_COMPONENT_CONFLICT.
- Eventi con effetto blocco planning: BLOCKING, CP_BLOCK, SHARED_COMPONENT_CONFLICT grave, ROUTE_MISMATCH confermato.
- Eventi warning-only: SATURATION non critica, QUALITY non bloccante, PLANNER_EXCEPTION diagnostica.
- Eventi che richiedono conferma TL: TL_OVERRIDE, ROUTE_MISMATCH ambiguo, conflitti multi-order non risolti.
- Severita e impatto devono esplicitare station impact e multi-order impact.
- Persistenza semantica: OPEN resta attivo finche non risolto; CLOSED rimuove blocco attivo ma conserva audit causale.
NOTES:
- Propagazione inter-ordine: shortage condivisi e conflitti route estendono impatto oltre singolo ordine.

## 27. SHARED COMPONENT GRAPH
RULE_ID: COMPONENT-GRAPH-001
CATEGORY: WORLD_MODEL_COMPONENTS
STATUS: ACTIVE
SOURCE: MASTER + TL
DESCRIPTION: shared_component genera un grafo causale componente -> articoli -> route -> stazioni -> saturazione -> impatto planner.
CONSTRAINTS:
- Un componente critico condiviso amplifica rischio di saturazione su stazioni comuni.
- Effetto fanout: un singolo shortage puo vincolare piu articoli e finestre turno.
- Effetto moltiplicativo ZAW: conflitti O-ring/crimp-ring condivisi aumentano probabilita di BLOCCATO.
- Catene PIDMILL: dipendenze sequenziali accumulano ritardi se input condivisi non disponibili.
- Nessuna promozione automatica a CERTO senza evidenza da fonte autorevole.
NOTES:
- Il modello resta TL-centrico: priorita e azione finale dipendono dalla decisione TL.

## 28. TL DECISION SEMANTICS
RULE_ID: TL-COGNITION-001
CATEGORY: WORLD_MODEL_TL
STATUS: ACTIVE
SOURCE: TL + MASTER
DESCRIPTION: Il layer cognitivo TL bilancia scadenze, colli di bottiglia, saturazione e continuita turno.
CONSTRAINTS:
- Prioritizzazione: bilanciamento route/station prima di ottimizzazioni locali.
- Mitigazione bottleneck: prevenire accumuli su ZAW/PIDMILL/CP con sequenze stazione-aware.
- Adattamento anti-fragile: riallineamento dinamico su nuovi eventi OPEN critici.
- Override authority: TL resta autorita finale su deviazioni operative ad alto impatto.
- Override scope: puo ridefinire priorita, ma non annulla tracciabilita evento.
- Override persistence: deve essere persistito semanticamente con contesto causale.
- Override auditability: ogni override richiede motivazione, conferma e rollback_id.
NOTES:
- Intuizione operativa TL e parte del world model, non rumore eccezionale.

## 29. CONFIDENCE MODEL
RULE_ID: CONFIDENCE-SEMANTICS-001
CATEGORY: WORLD_MODEL_CONFIDENCE
STATUS: ACTIVE
SOURCE: MASTER
DESCRIPTION: Gli stati di confidence definiscono limiti decisionali, automazione ammessa ed escalation.
CONSTRAINTS:
- CERTO: utilizzabile per decisione operativa; AI non puo degradare senza evidenza nuova.
- INFERITO: utilizzabile con cautela; richiede verifiche su vincoli critici.
- DA_VERIFICARE: non idoneo a decisione automatica irreversibile; escalation TL consigliata.
- BLOCCATO: sospende avanzamento operativo finche vincolo non risolto o override TL confermato.
- STANDARD: classe operativa normale, planner_eligible compatibile salvo eventi bloccanti.
- REFERENCE_ONLY: escluso da automazione planner operativa diretta.
NOTES:
- Boundaries automazione: nessun passaggio a CERTO da sola inferenza AI.

## 30. PLANNER EXPLAINABILITY FOUNDATION
RULE_ID: PLANNER-EXPLAINABILITY-001
CATEGORY: WORLD_MODEL_EXPLAINABILITY
STATUS: ACTIVE
SOURCE: MASTER
DESCRIPTION: Ogni decisione planner deve essere spiegabile tramite catena causale esplicita.
CONSTRAINTS:
- Contratto minimo spiegazione: causal rules, blocking_constraint, event propagation, station saturation, shared_component impact, eventuale override TL.
- Trasparenza: motivazioni sintetiche ma verificabili per ordine/stazione/evento.
- AI validation boundary: AI puo validare coerenza, non creare autorita semantica alternativa.
- Nessuna decisione opaca non tracciabile a regole e stati canonici.
NOTES:
- Explainability e requisito operativo, non output opzionale.

## 31. ATLAS WORLD MODEL SUBSTRATE
RULE_ID: ATLAS-WORLDMODEL-001
CATEGORY: WORLD_MODEL_ATLAS
STATUS: ACTIVE
SOURCE: MASTER
DESCRIPTION: Questo MASTER costituisce il substrato semantico del futuro operational world model ATLAS.
CONSTRAINTS:
- ATLAS deve consumare causalita e policy da MASTER, non da fonti frammentate.
- Ogni estensione semantica permanente passa da convergenza nel MASTER.
- Vietata divergenza tra explainability planner e modello causale ufficiale.
NOTES:
- Sezione fondativa; implementazioni runtime restano fuori da questo documento.

## 32. OPERATIONAL GRAPH SEMANTICS
RULE_ID: OPGRAPH-SEMANTICS-001
CATEGORY: WORLD_MODEL_GRAPH
STATUS: ACTIVE
SOURCE: MASTER + TL
DESCRIPTION: Il modello operativo e rappresentato come grafo semantico-causale, non implementativo.
CONSTRAINTS:
- Entita canoniche: Article, Route, Station, Component, Event, PlannerDecision, TLOverride, Saturation, Constraint, ProductionSequence, DependencyChain.
- Relazioni canoniche: depends_on, blocks, amplifies, saturates, propagates_to, coupled_with, validated_by, constrained_by, escalated_by, overridden_by.
- Le relazioni descrivono causalita operativa e precedenza decisionale, non schema tecnico.
NOTES:
- Il grafo semantico e base di explainability e allineamento TL.

## 33. CONSTRAINT PROPAGATION MODEL
RULE_ID: CONSTRAINT-PROPAGATION-001
CATEGORY: WORLD_MODEL_PROPAGATION
STATUS: ACTIVE
SOURCE: MASTER + TL
DESCRIPTION: I vincoli operativi propagano impatto locale, upstream, downstream e multi-order.
CONSTRAINTS:
- Categorie propagazione: station saturation, component shortage, CP blocking, route mismatch, PIDMILL dependency, shared component, planner conflict.
- Hard blocking constraints: impediscono avanzamento sequenza finche non risolti o overridden_by TL valido.
- Soft warning constraints: mantengono pianificazione attiva ma con rischio operativo esplicito.
- TL escalation constraints: richiedono conferma TL prima di continuare in presenza di ambiguita critica.
- Propagation severity e persistence devono essere esplicite nel ragionamento planner.
NOTES:
- La propagazione non e solo ordine-locale: deve modellare effetti inter-ordine.

## 34. MULTI-ORDER INTERACTION MODEL
RULE_ID: MULTIORDER-INTERACTION-001
CATEGORY: WORLD_MODEL_MULTIORDER
STATUS: ACTIVE
SOURCE: MASTER + TL
DESCRIPTION: Un ordine puo alterare la fattibilita operativa di altri ordini attraverso risorse condivise.
CONSTRAINTS:
- Cross-order coupling: condivisione stazioni/componenti collega la decisione di sequenza tra ordini.
- Shared bottlenecks: ZAW1, ZAW2, PIDMILL, CP possono trasferire backlog tra ordini.
- Backlog amplification: ritardi su un ordine aumentano saturazione e rischio su ordini dipendenti.
- Sequence destabilization: conflitti simultanei possono invalidare la priorita locale ottima.
- Cascading planner impact: una scelta iniziale puo propagare conflitti in finestre turno successive.
NOTES:
- Il modello e TL-centrico: decisione finale resta umana e contestuale.

## 35. TEMPORAL OPERATIONAL SEMANTICS
RULE_ID: TEMPORAL-OPERATIONS-001
CATEGORY: WORLD_MODEL_TEMPORAL
STATUS: ACTIVE
SOURCE: MASTER + TL
DESCRIPTION: La causalita operativa include persistenza, accumulo e recupero nel tempo turno.
CONSTRAINTS:
- Backlog accumulation: code non risolte aumentano pressione causale su stazioni critiche.
- Saturation persistence: saturazione prolungata degrada throughput e stabilita sequenza.
- Delayed propagation: alcuni vincoli emergono a valle con ritardo operativo.
- OPEN persistence: eventi OPEN irrisolti mantengono attivo il vincolo causale.
- Temporal blocking chains: blocchi concatenati possono estendersi su piu fasi/ordini.
- Recovery semantics: il ripristino richiede riduzione vincoli, non solo chiusura formale evento.
- Stabilization conditions: il sistema torna stabile quando vincoli critici cessano propagazione.
NOTES:
- Distinzione obbligatoria tra condizioni transitorie e persistenti.

## 36. REASONING BOUNDARIES
RULE_ID: REASONING-BOUNDARY-001
CATEGORY: WORLD_MODEL_REASONING_GUARD
STATUS: ACTIVE
SOURCE: MASTER
DESCRIPTION: I confini di ragionamento delimitano cosa l'AI puo fare e cosa deve rimettere al TL.
CONSTRAINTS:
- AI MAY: validare coerenza, rilevare propagazioni, spiegare vincoli, evidenziare rischi saturazione, segnalare conflitti, suggerire investigazioni.
- AI MAY NOT: inventare route confermate, override della verita TL, inferire semantica stazione mancante senza supporto, bypassare blocking_constraint, creare autorita produttiva autonoma.
- TL authority remains final per decisioni operative ad alto impatto.
NOTES:
- Questi limiti sono vincoli di governance, non opzioni configurabili locali.

## 37. EXPLAINABLE REASONING CONTRACT
RULE_ID: EXPLAINABLE-REASONING-001
CATEGORY: WORLD_MODEL_EXPLAINABILITY_CONTRACT
STATUS: ACTIVE
SOURCE: MASTER
DESCRIPTION: Ogni catena decisionale planner deve essere trasparente, verificabile e causalmente tracciabile.
CONSTRAINTS:
- La spiegazione deve includere: causal dependency, propagation chain, blocking constraints, station saturation, shared component impact, event escalation, TL override impact.
- Ogni conclusione deve mappare a regole canoniche e stati semantici del MASTER.
- Nessuna conclusione operativa puo essere presentata senza razionale causale minimo.
- I conflitti non risolti devono emergere come DA_VERIFICARE o BLOCCATO, mai mascherati.
NOTES:
- Contratto minimo valido per explain planner, ATLAS reasoning e verifica umana.

## 38. WORLD MODEL STABILIZATION
RULE_ID: WORLDMODEL-STABILIZATION-001
CATEGORY: GOVERNANCE_WORLD_MODEL
STATUS: ACTIVE
SOURCE: MASTER
DESCRIPTION: Il MASTER e autorita semantica operativa per graph reasoning, causal governance e planner explainability.
CONSTRAINTS:
- Vietato introdurre semantica operativa permanente fuori da questo documento.
- Ogni nuova regola causale stabile deve essere prima converta nel MASTER.
- Documenti esterni possono solo referenziare o riassumere, non sostituire l'autorita semantica.
NOTES:
- Stabilizzazione anti-frammentazione per il futuro sistema cognitivo ATLAS.

## 39. OPERATIONAL COGNITION MODEL
RULE_ID: COGNITION-MODEL-001
CATEGORY: WORLD_MODEL_COGNITION
STATUS: ACTIVE
SOURCE: TL + MASTER
DESCRIPTION: La cognizione operativa TL e un processo adattivo contestuale, non esecuzione statica di regole.
CONSTRAINTS:
- Bottleneck anticipation: anticipare accumuli su ZAW1, ZAW2, PIDMILL, CP prima della saturazione manifesta.
- Dynamic prioritization: riallocare priorita in base a eventi OPEN, backlog e vincoli emergenti.
- Adaptive sequencing: riorganizzare sequenza per contenere propagazioni critiche.
- Saturation mitigation: distribuire carico tra finestre turno per evitare collasso locale.
- Station balancing: bilanciare continuita di flusso e rischio vincoli stazione-specifici.
- Strategic backlog redistribution: spostare backlog per ridurre picchi di instabilita.
- Instability containment: limitare fanout dei vincoli prima che diventino sistemici.
- Anti-fragile adaptation: migliorare resilienza operativa dopo eventi avversi ricorrenti.
NOTES:
- Cognizione TL e route-aware, station-aware, saturation-aware e constraint-aware.

## 40. SIMULATION SEMANTICS
RULE_ID: SIMULATION-SEMANTICS-001
CATEGORY: WORLD_MODEL_SIMULATION
STATUS: ACTIVE
SOURCE: MASTER + TL
DESCRIPTION: La simulazione e semantica-causale: stima evoluzioni operative senza imporre predizione numerica runtime.
CONSTRAINTS:
- Propagation forecasting: stimare come i vincoli si diffondono nel grafo operativo.
- Saturation evolution: stimare crescita/attenuazione saturazioni in base a dipendenze attive.
- Backlog evolution: stimare accumulo o drenaggio code sotto vincoli persistenti.
- Cascading instability: identificare sequenze che amplificano instabilita cross-order.
- Route destabilization: evidenziare quando la route pianificata perde robustezza operativa.
- Recovery simulation: valutare percorsi di rientro a stabilita causale.
- Planner stress conditions: segnalare condizioni che degradano qualita decisionale.
- Sequence degradation: tracciare perdita progressiva di fattibilita sequenza.
- Station collapse risk: segnalare rischio di saturazione critica prolungata su stazioni chiave.
NOTES:
- Simulazione semantica supporta TL; non sostituisce decisione finale.

## 41. OPERATIONAL RISK SEMANTICS
RULE_ID: OPERATIONAL-RISK-001
CATEGORY: WORLD_MODEL_RISK
STATUS: ACTIVE
SOURCE: MASTER + TL
DESCRIPTION: Il rischio operativo e classificato per ampiezza, persistenza e difficolta di stabilizzazione.
CONSTRAINTS:
- Categorie: local instability, systemic instability, cascading saturation, planner degradation, CP overload, unresolved OPEN accumulation, route fragility, dependency amplification, shared-component explosion risk.
- Escalation thresholds: superamento soglie causali richiede incremento severita e possibile BLOCCATO.
- Operational severity: severita dipende da impatto stazione, cross-order coupling e persistenza.
- Persistence risk: rischio cresce se vincoli critici restano OPEN su piu cicli decisionali.
- Stabilization difficulty: dipende da profondita catena causale e disponibilita percorsi alternativi.
NOTES:
- La classificazione rischio e input di explainability, non verdetto automatico.

## 42. RECOVERY & STABILIZATION MODEL
RULE_ID: RECOVERY-STABILIZATION-001
CATEGORY: WORLD_MODEL_RECOVERY
STATUS: ACTIVE
SOURCE: MASTER + TL
DESCRIPTION: Il recupero operativo e riduzione causale dei vincoli, non semplice chiusura evento.
CONSTRAINTS:
- De-saturation: ridurre carico su nodi critici con riequilibrio sequenza e priorita.
- Recovery pathways: percorsi alternativi validi devono preservare vincoli di sicurezza/qualita.
- Stabilization windows: finestre temporali in cui e possibile contenere propagazione.
- Bottleneck relief: interventi che riducono pressione su ZAW/PIDMILL/CP.
- Planner recovery mode: stato operativo prudente quando la sequenza e degradata.
- Temporary containment: isolamento locale per evitare propagazione sistemica.
- Partial recovery: recupero incompleto mantiene warning e monitoraggio rinforzato.
- Cascading recovery: risoluzione progressiva di vincoli concatenati multi-order.
NOTES:
- Evento CLOSED e necessario ma non sufficiente a dichiarare stabilizzazione completa.

## 43. OPERATIONAL MEMORY SEMANTICS
RULE_ID: OPERATIONAL-MEMORY-001
CATEGORY: WORLD_MODEL_MEMORY
STATUS: ACTIVE
SOURCE: TL + MASTER
DESCRIPTION: La memoria operativa conserva pattern storici che influenzano ragionamento futuro.
CONSTRAINTS:
- Unresolved issue persistence: issue irrisolte mantengono peso causale nelle decisioni successive.
- Repeated instability patterns: pattern ricorrenti aumentano priorita di prevenzione.
- Historical saturation memory: saturazioni storiche orientano mitigazioni preventive.
- Recurring bottleneck behavior: colli ricorrenti guidano scelte conservative di sequenza.
- TL experiential pattern recognition: esperienza TL integra segnali non completamente codificati.
- Operational precedent influence: precedenti confermati influenzano valutazione rischio corrente.
NOTES:
- Memoria operativa e parte della cognizione industriale, non archivio passivo.

## 44. HUMAN-IN-THE-LOOP COGNITION
RULE_ID: HITL-COGNITION-001
CATEGORY: WORLD_MODEL_HITL
STATUS: ACTIVE
SOURCE: TL + MASTER
DESCRIPTION: Il modello cognitivo operativo resta human-in-the-loop con AI come supporto bounded.
CONSTRAINTS:
- AI supporta visibility, propagation detection, instability analysis, explainability, simulation assistance.
- TL resta contextual authority, adaptive strategist, operational stabilizer, final decision authority.
- Human override superiority: l'override TL prevale su inferenze AI non confermate.
- Human contextual superiority: contesto reparto puo correggere semantica inferita.
- AI bounded cognition: AI non acquisisce autorita operativa autonoma.
- Operational trust boundaries: fiducia AI condizionata da trasparenza e tracciabilita causale.
NOTES:
- Il sistema privilegia robustezza operativa rispetto ad automazione cieca.

## 45. SIMULATION EXPLAINABILITY CONTRACT
RULE_ID: SIMULATION-EXPLAINABILITY-001
CATEGORY: WORLD_MODEL_SIMULATION_EXPLAINABILITY
STATUS: ACTIVE
SOURCE: MASTER
DESCRIPTION: Ogni catena simulativa deve essere spiegabile, causale, TL-readable e audit-friendly.
CONSTRAINTS:
- La simulazione deve spiegare: perche l'instabilita propaga, quali dipendenze agiscono, quali stazioni amplificano rischio, quali componenti aumentano coupling, perche backlog evolve, perche saturazione persiste, perche recovery e facile/difficile.
- Ogni scenario deve esporre assumptions operative e vincoli attivi.
- Nessun output simulativo puo essere presentato come certezza senza stato confidence coerente.
- Le incertezze devono emergere come INFERITO o DA_VERIFICARE con richiesta TL quando necessario.
NOTES:
- Contratto valido per simulazione diagnostica e forecasting semantico spiegabile.

## 46. OPERATIONAL COGNITION STABILIZATION INDEX
RULE_ID: COGNITION-INDEX-STABILITY-001
CATEGORY: GOVERNANCE_COGNITION_INDEX
STATUS: ACTIVE
SOURCE: MASTER
DESCRIPTION: Gli indici cognitivi e simulativi sono layer stabile di query semantica AI.
CONSTRAINTS:
- Gli indici devono restare lightweight, semantici, stabili, cross-referenceable.
- Nuove tassonomie cognitive permanenti devono essere introdotte via MASTER.
- Vietato usare indici esterni come autorita semantica alternativa.
NOTES:
- Garantisce discoverability coerente per ATLAS operational intelligence.

## 47. WORLD MODEL COGNITIVE STABILIZATION
RULE_ID: COGNITIVE-STABILIZATION-001
CATEGORY: GOVERNANCE_COGNITIVE_WORLD_MODEL
STATUS: ACTIVE
SOURCE: MASTER
DESCRIPTION: Il MASTER e fondazione cognitiva e simulativa del futuro ATLAS operational intelligence system.
CONSTRAINTS:
- Il layer cognitivo/simulativo resta semantico, causale e TL-centrico.
- Vietata sostituzione della cognizione TL con autonomia AI.
- Ogni estensione permanente di reasoning adattivo richiede convergenza nel MASTER.
- Anti-fragmentazione rafforzata: nessuna authority cognitiva fuori MASTER.
NOTES:
- Stabilizzazione finale del substrato di operational cognition e simulation semantics.

## 48. STRATEGIC SEQUENCING SEMANTICS
RULE_ID: STRATEGIC-SEQUENCING-001
CATEGORY: STRATEGIC_OPERATIONS
STATUS: ACTIVE
SOURCE: TL + MASTER
DESCRIPTION: Il sequencing strategico e dinamico, contestuale e orientato alla stabilizzazione operativa.
CONSTRAINTS:
- Anticipatory sequencing: anticipa propagazioni prima dell'insorgenza di BLOCCATO.
- Saturation-aware sequencing: ordina lavoro in funzione di pressione stazione e margine operativo.
- Bottleneck containment sequencing: limita fanout dei colli su ZAW/PIDMILL/CP.
- Stabilization-oriented sequencing: privilegia traiettorie che riducono instabilita persistente.
- Adaptive route balancing: bilancia route concorrenti senza forzare equivalenze non confermate.
- Throughput-preserving sequencing: conserva continuita flusso sotto vincoli.
- Recovery-oriented sequencing: prepara vie di recupero mentre gestisce backlog.
- Strategic backlog shaping: distribuisce backlog per evitare picchi destabilizzanti.
NOTES:
- Sequencing non e ottimizzazione statica; e ragionamento adattivo vincolato.

## 49. OPERATIONAL RESILIENCE SEMANTICS
RULE_ID: RESILIENCE-SEMANTICS-001
CATEGORY: STRATEGIC_RESILIENCE
STATUS: ACTIVE
SOURCE: TL + MASTER
DESCRIPTION: La resilienza operativa descrive come il sistema degrada e si stabilizza senza collasso immediato.
CONSTRAINTS:
- Graceful degradation: degradazione progressiva con mantenimento controllo causale.
- Controlled instability: instabilita ammessa entro soglie gestibili.
- Operational containment: isolamento rapido dei vincoli ad alta propagazione.
- Anti-collapse behavior: priorita a prevenire collasso stazioni critiche.
- Adaptive stabilization: ricalibrazione continua rispetto a eventi OPEN e backlog.
- Resilience thresholds: superamento soglie richiede escalation TL.
- Strategic buffering: uso di buffer operativi per assorbire overload.
- Overload absorption: riduzione impatto picchi senza perdere tracciabilita.
NOTES:
- Resilienza e comportamento sistemico, non singolo fix locale.

## 50. OPERATIONAL EQUILIBRIUM MODEL
RULE_ID: EQUILIBRIUM-MODEL-001
CATEGORY: STRATEGIC_EQUILIBRIUM
STATUS: ACTIVE
SOURCE: MASTER + TL
DESCRIPTION: L'equilibrio operativo e dinamico e puo includere oscillazioni controllate.
CONSTRAINTS:
- Operational equilibrium: stato in cui vincoli restano governabili.
- Saturation equilibrium: saturazione stabile entro limiti non collassanti.
- Planner destabilization: perdita progressiva di robustezza decisionale.
- Equilibrium recovery: ritorno a governabilita tramite riduzione propagazioni.
- Oscillatory operational states: alternanza stress/rilascio senza collasso pieno.
- Persistent instability: instabilita che permane oltre cicli decisionali.
- Temporary equilibrium: stabilita locale transitoria non definitiva.
- Hidden instability accumulation: rischio latente non ancora espresso in BLOCCATO.
NOTES:
- Equilibrio non implica assenza di rischio, ma controllo adattivo del rischio.

## 51. STRATEGIC PLANNER COGNITION
RULE_ID: STRATEGIC-PLANNER-001
CATEGORY: STRATEGIC_PLANNER_INTELLIGENCE
STATUS: ACTIVE
SOURCE: MASTER
DESCRIPTION: Il planner strategico resta bounded, adattivo e spiegabile.
CONSTRAINTS:
- Planner confidence adaptation: adegua confidenza a propagazione e qualita evidenze.
- Strategic escalation behavior: incrementa escalation quando resilienza degrada.
- Adaptive planner stabilization: sceglie alternative che riducono fragilita sistemica.
- Planner stress states: riconosce stati di stress decisionale elevato.
- Strategic conflict handling: esplicita trade-off tra obiettivi concorrenti.
- Stabilization prioritization: privilegia riduzione instabilita su ottimi locali fragili.
- Operational compromise reasoning: accetta compromessi tracciabili quando necessario.
NOTES:
- L'intelligenza planner non puo bypassare confini di governance e TL authority.

## 52. UNCERTAINTY & TRUST SEMANTICS
RULE_ID: UNCERTAINTY-TRUST-001
CATEGORY: STRATEGIC_UNCERTAINTY
STATUS: ACTIVE
SOURCE: MASTER
DESCRIPTION: Il ragionamento operativo deve trattare incertezza e fiducia come dimensioni causali esplicite.
CONSTRAINTS:
- Uncertainty propagation: incertezza si propaga lungo dipendenze e conflitti.
- Confidence degradation: la confidenza cala con ambiguita persistente.
- Semantic trust layers: fonti hanno priorita e affidabilita differenziate.
- Reasoning reliability: ogni inferenza deve dichiarare livello di affidabilita.
- Trust-aware escalation: escalation aumenta con calo fiducia operativa.
- Confidence about confidence: valutare la robustezza del giudizio di confidenza.
- Uncertainty amplification: coupling multi-order puo amplificare incertezza.
- Unstable inference detection: inferenze fragili devono emergere come DA_VERIFICARE.
NOTES:
- Non tutta conoscenza operativa ha lo stesso peso semantico.

## 53. META-REASONING SEMANTICS
RULE_ID: META-REASONING-001
CATEGORY: STRATEGIC_META_REASONING
STATUS: ACTIVE
SOURCE: MASTER
DESCRIPTION: Il sistema valuta i limiti del proprio ragionamento prima di proporre azioni operative.
CONSTRAINTS:
- Reasoning reliability assessment: verifica coerenza e robustezza della catena causale.
- Propagation confidence evaluation: misura fiducia nella propagazione dedotta.
- Simulation trustworthiness: qualifica affidabilita degli scenari simulativi.
- Explainability sufficiency: segnala quando spiegazione non e sufficiente.
- Escalation necessity detection: identifica quando serve intervento TL.
- Operational ambiguity detection: rileva ambiguita critiche non risolte.
- Semantic inconsistency awareness: evidenzia conflitti tra regole, stati o fonti.
NOTES:
- Meta-reasoning e guardrail cognitivo, non livello autonomo decisionale.

## 54. STRATEGIC HUMAN-IN-THE-LOOP INTELLIGENCE
RULE_ID: STRATEGIC-HITL-001
CATEGORY: STRATEGIC_HITL
STATUS: ACTIVE
SOURCE: TL + MASTER
DESCRIPTION: La strategia operativa resta human-led con AI come supporto bounded e spiegabile.
CONSTRAINTS:
- TL resta strategic stabilizer, contextual intelligence authority, equilibrium manager, uncertainty resolver e final escalation authority.
- AI resta bounded support per analisi propagazione, visibilita instabilita e explainability.
- Human contextual intelligence superiority: il contesto reale TL prevale su inferenze non confermate.
- Nessuna autonomia AI puo sostituire decisione strategica TL ad alto impatto.
NOTES:
- HITL strategico e requisito permanente di governance industriale.

## 55. STRATEGIC EXPLAINABILITY CONTRACT
RULE_ID: STRATEGIC-EXPLAINABILITY-001
CATEGORY: STRATEGIC_EXPLAINABILITY
STATUS: ACTIVE
SOURCE: MASTER
DESCRIPTION: Ogni catena strategica deve spiegare causalmente evoluzione rischio, equilibrio e fiducia.
CONSTRAINTS:
- Deve spiegare: perche instabilita evolve, perche equilibrio tiene/fallisce, perche cambia confidenza planner, perche escalation incertezza aumenta, perche buffering funziona/fallisce, perche resilienza degrada, perche escalation TL diventa necessaria.
- Deve restare explainable, causal, TL-readable, governance-compatible e audit-friendly.
- Conclusioni con affidabilita insufficiente devono emergere come INFERITO/DA_VERIFICARE.
NOTES:
- Contratto strategico estende explainability operativa senza sostituirla.

## 56. STRATEGIC COGNITION INDEX STABILITY
RULE_ID: STRATEGIC-INDEX-STABILITY-001
CATEGORY: GOVERNANCE_STRATEGIC_INDEX
STATUS: ACTIVE
SOURCE: MASTER
DESCRIPTION: Gli indici strategici devono restare stabili, leggeri e interrogabili da AI senza ambiguita.
CONSTRAINTS:
- Le tassonomie strategiche permanenti si introducono solo via MASTER.
- Indici esterni possono referenziare ma non ridefinire semantica strategica.
- Cross-reference obbligatorio tra sezioni rischio, resilienza, incertezza e HITL.
NOTES:
- Stabilizza recupero semantico per ATLAS strategic cognition.

## 57. STRATEGIC STABILIZATION
RULE_ID: STRATEGIC-STABILIZATION-001
CATEGORY: GOVERNANCE_STRATEGIC_WORLD_MODEL
STATUS: ACTIVE
SOURCE: MASTER
DESCRIPTION: Il MASTER e substrato ufficiale di strategic operational intelligence per ATLAS futuro.
CONSTRAINTS:
- La semantica strategica resta non-implementativa, causale e TL-centrica.
- Vietato introdurre authority strategica permanente fuori MASTER.
- Nessuna estensione strategica puo ridurre TL authority o introdurre autonomia AI non supportata.
- Anti-fragmentazione rafforzata su resilience, equilibrium, uncertainty e meta-reasoning.
NOTES:
- Consolidamento finale del layer strategico di operational intelligence.

## 58. AUTONOMIC GOVERNANCE SEMANTICS
RULE_ID: AUTONOMIC-GOVERNANCE-001
CATEGORY: AUTONOMIC_GOVERNANCE
STATUS: ACTIVE
SOURCE: MASTER + TL
DESCRIPTION: La governance autonomica e bounded: supervisione adattiva senza autorita operativa autonoma.
CONSTRAINTS:
- Governance self-monitoring: osservazione continua di coerenza regole/stati/decisioni.
- Governance stabilization: priorita a mantenere integrita semantica sotto stress operativo.
- Adaptive governance containment: contenimento adattivo di deviazioni prima di propagazione sistemica.
- Escalation governance: escalation guidata da soglie di rischio/coerenza.
- Governance degradation awareness: riconoscere perdita progressiva di controllo semantico.
- Operational integrity preservation: preservare catena causale e authority boundaries.
- Bounded adaptive supervision: adattamento consentito solo entro confini TL + MASTER.
- Controlled governance adaptation: ogni adattamento resta reversibile e tracciabile.
NOTES:
- Adattamento governance sempre subordinato a verita confermata e autorita TL.

## 59. COGNITIVE INTEGRITY SEMANTICS
RULE_ID: COGNITIVE-INTEGRITY-001
CATEGORY: AUTONOMIC_COGNITIVE_INTEGRITY
STATUS: ACTIVE
SOURCE: MASTER
DESCRIPTION: Integrita cognitiva = coerenza semantica verificabile tra regole, inferenze e spiegazioni.
CONSTRAINTS:
- Semantic drift detection: individuare divergenze progressive dal modello canonico.
- Planner integrity preservation: impedire degradazione silente della logica spiegabile.
- Explainability sufficiency validation: segnalare spiegazioni incomplete o non verificabili.
- Governance coherence validation: verificare allineamento tra policy e ragionamento.
- Contradiction awareness: evidenziare conflitti logici tra stati/regole/fonti.
- Unstable reasoning detection: identificare catene causali fragili o auto-contraddittorie.
- Semantic conflict escalation: conflitti critici devono triggerare escalation TL.
- Integrity degradation awareness: riconoscere calo di affidabilita cognitiva nel tempo.
NOTES:
- Integrita cognitiva e prerequisito per fiducia operativa.

## 60. AUTONOMIC SUPERVISION MODEL
RULE_ID: AUTONOMIC-SUPERVISION-001
CATEGORY: AUTONOMIC_SUPERVISION
STATUS: ACTIVE
SOURCE: MASTER
DESCRIPTION: La self-supervision e osservazionale/diagnostica, non autorizzazione autonoma all'azione.
CONSTRAINTS:
- Self-monitoring: monitorare coerenza interna del ragionamento operativo.
- Self-evaluation: valutare robustezza delle conclusioni prima dell'escalation.
- Bounded self-correction awareness: rilevare necessità di correzione senza auto-applicare mutazioni dominio.
- Operational self-observation: osservare pattern di degrado decisionale.
- Confidence self-assessment: autovalutare affidabilita della confidence assegnata.
- Propagation reliability checks: verificare robustezza delle propagazioni inferite.
- Reasoning chain verification: validare completezza minima della catena causale.
- Escalation necessity awareness: riconoscere quando serve intervento TL.
NOTES:
- Supervisione autonoma resta governance-oriented e non esecutiva.

## 61. STRATEGIC CONTAINMENT SEMANTICS
RULE_ID: STRATEGIC-CONTAINMENT-001
CATEGORY: AUTONOMIC_CONTAINMENT
STATUS: ACTIVE
SOURCE: MASTER + TL
DESCRIPTION: Il contenimento strategico privilegia stabilita sistemica rispetto a ottimi locali fragili.
CONSTRAINTS:
- Instability containment: limitare espansione di instabilita locale.
- Uncertainty containment: isolare zone ad alta ambiguita prima di decisioni irreversibili.
- Planner degradation containment: impedire propagazione di degradazione planner.
- Semantic conflict containment: confinare conflitti semantici con escalation guidata.
- Escalation isolation: separare escalation critiche da carico non critico.
- Cascading failure prevention: prevenire collassi concatenati multi-stazione/multi-order.
- Governance stabilization buffering: mantenere margini operativi sotto stress.
- Operational collapse prevention: prevenire perdita di governabilita complessiva.
NOTES:
- Stabilita globale puo prevalere su performance locale di breve periodo.

## 62. GOVERNANCE MEMORY SEMANTICS
RULE_ID: GOVERNANCE-MEMORY-001
CATEGORY: AUTONOMIC_GOVERNANCE_MEMORY
STATUS: ACTIVE
SOURCE: TL + MASTER
DESCRIPTION: La memoria di governance conserva precedenti utili a stabilizzazione futura.
CONSTRAINTS:
- Governance precedent memory: ricordare decisioni di stabilizzazione efficaci/inefficaci.
- Historical stabilization patterns: tracciare pattern storici di recupero operativo.
- Recurring governance failures: riconoscere failure ricorrenti di policy/applicazione.
- Long-term operational learning semantics: apprendimento semantico nel tempo senza autonomia esecutiva.
- Historical escalation patterns: identificare quando escalation anticipata evita degrado sistemico.
- Semantic conflict recurrence awareness: rilevare ricorrenza conflitti non risolti.
- Institutional operational memory: preservare continuita cognitiva oltre il singolo turno.
NOTES:
- La memoria guida prevenzione, non sostituisce conferma TL su casi critici.

## 63. AUTONOMIC TRUST & SAFETY BOUNDARIES
RULE_ID: AUTONOMIC-TRUST-SAFETY-001
CATEGORY: AUTONOMIC_SAFETY
STATUS: ACTIVE
SOURCE: MASTER
DESCRIPTION: Fiducia autonomica sempre bounded, subordinata, reversibile ed esplicabile.
CONSTRAINTS:
- Bounded adaptive autonomy: nessuna autonomia oltre perimetro semantico consentito.
- Governance trust thresholds: soglie fiducia definiscono quando fermarsi/escalare.
- Semantic safety boundaries: limiti semantici invalicabili su route, blocking e authority.
- Escalation trust gates: escalation obbligatoria sotto soglie di affidabilita.
- Confidence safety limits: confidence bassa impedisce assertivita operativa.
- AI bounded authority: AI non acquisisce autorita operativa primaria.
- TL override supremacy: override TL prevale su inferenze AI non confermate.
- Governance rollback semantics: ogni adattamento deve essere reversibile e auditabile.
NOTES:
- Safety boundaries sono parte del modello causale di governance.

## 64. AUTONOMIC EXPLAINABILITY CONTRACT
RULE_ID: AUTONOMIC-EXPLAINABILITY-001
CATEGORY: AUTONOMIC_EXPLAINABILITY
STATUS: ACTIVE
SOURCE: MASTER
DESCRIPTION: Ogni catena autonomica di governance deve essere causale, leggibile e verificabile dal TL.
CONSTRAINTS:
- Deve spiegare: perche integrita degrada, perche escalation si attiva, perche containment parte, perche incertezza amplifica, perche avviene adattamento governance, perche rollback/escalation diventa necessario, perche si prioritizza stabilita.
- Deve restare explainable, causal, TL-readable, governance-compatible e audit-friendly.
- Ogni passaggio deve riferire regole canoniche e stati di confidence coerenti.
- In presenza di ambiguita elevata, output minimo = DA_VERIFICARE + escalation TL.
NOTES:
- Contratto di explainability autonomica estende i contratti operativi/strategici.

## 65. AUTONOMIC GOVERNANCE INDEX STABILITY
RULE_ID: AUTONOMIC-INDEX-STABILITY-001
CATEGORY: GOVERNANCE_AUTONOMIC_INDEX
STATUS: ACTIVE
SOURCE: MASTER
DESCRIPTION: Gli indici autonomici devono restare stabili, leggeri e senza ambiguita semantica.
CONSTRAINTS:
- Nuove tassonomie autonomiche permanenti passano solo da MASTER.
- Indici esterni possono referenziare ma non ridefinire confini di governance autonomica.
- Cross-reference obbligatorio tra integrita, supervisione, containment e safety.
NOTES:
- Garantisce recupero semantico consistente per ATLAS bounded governance.

## 66. GOVERNANCE STABILIZATION
RULE_ID: AUTONOMIC-STABILIZATION-001
CATEGORY: GOVERNANCE_AUTONOMIC_WORLD_MODEL
STATUS: ACTIVE
SOURCE: MASTER
DESCRIPTION: Il MASTER e substrato di bounded autonomic governance e cognitive integrity per ATLAS futuro.
CONSTRAINTS:
- Vietata qualsiasi forma di autorita operativa autonoma non supervisionata dal TL.
- Nessuna estensione puo ridurre TL supremacy o superare SOURCE OF TRUTH POLICY.
- Anti-drift framework obbligatorio: rilevare, contenere, escalare, stabilizzare.
- Anti-fragmentazione rafforzata: nessuna authority autonomica permanente fuori MASTER.
NOTES:
- Stabilizzazione finale del layer di autonomic governance bounded e controllata.

## 67. INSTITUTIONAL REASONING SEMANTICS
RULE_ID: INSTITUTIONAL-REASONING-001
CATEGORY: INSTITUTIONAL_OPERATIONS
STATUS: ACTIVE
SOURCE: TL + MASTER
DESCRIPTION: Il ragionamento istituzionale preserva continuita operativa oltre evento, turno e stato planner locale.
CONSTRAINTS:
- Operational continuity: continuita decisionale tra cicli operativi successivi.
- Long-horizon stabilization: stabilizzazione estesa su orizzonti multi-shift.
- Governance continuity: coerenza persistente tra policy e pratica operativa.
- Institutional operational persistence: conservare identita operativa del sistema.
- Strategic operational inheritance: trasferire strategie robuste validate storicamente.
- Continuity-aware reasoning: preferire traiettorie che minimizzano discontinuita critiche.
- Institutional escalation memory: usare memoria escalation per prevenzione anticipata.
- Persistent operational identity: mantenere coerenza semantica lungo evoluzione sistema.
NOTES:
- Questo layer e cumulativo e non dipende dal singolo evento isolato.

## 68. ORGANIZATIONAL INTELLIGENCE SEMANTICS
RULE_ID: ORGANIZATIONAL-INTELLIGENCE-001
CATEGORY: INSTITUTIONAL_ORGANIZATIONAL_INTELLIGENCE
STATUS: ACTIVE
SOURCE: TL + MASTER
DESCRIPTION: L'intelligenza organizzativa e distribuita, cumulativa, contestuale e governance-aware.
CONSTRAINTS:
- Distributed operational knowledge: conoscenza diffusa tra ruoli, turni e contesti.
- Organizational memory: memoria condivisa di pattern operativi e decisioni efficaci.
- Inter-shift operational learning: apprendimento tra turni con continuita semantica.
- Collective stabilization behavior: pratiche collettive di contenimento instabilita.
- Institutional operational adaptation: adattamento senza perdere confini di governance.
- Organizational reasoning continuity: continuita logica tra decisioni storiche e correnti.
- Systemic operational awareness: visione sistemica oltre singola stazione/ordine.
- Persistent operational context: mantenere contesto storico rilevante nelle escalation.
NOTES:
- L'intelligenza organizzativa non abilita autonomia AI istituzionale.

## 69. LONG-HORIZON OPERATIONAL SEMANTICS
RULE_ID: LONGHORIZON-OPERATIONS-001
CATEGORY: INSTITUTIONAL_LONGHORIZON
STATUS: ACTIVE
SOURCE: MASTER + TL
DESCRIPTION: Le dinamiche operative di lungo orizzonte emergono per accumulo progressivo e ritardi sistemici.
CONSTRAINTS:
- Long-term backlog accumulation: code persistenti alterano robustezza strategica.
- Resilience erosion: resilienza puo ridursi gradualmente sotto stress ricorrente.
- Strategic degradation: degrado progressivo della qualita decisionale strategica.
- Multi-shift instability accumulation: instabilita si accumula tra turni successivi.
- Chronic bottleneck persistence: colli cronici richiedono gestione strutturale.
- Delayed systemic effects: effetti critici possono emergere con ritardo causale.
- Accumulated operational debt: debito operativo cresce con compromessi ripetuti.
- Institutional stabilization fatigue: fatica di stabilizzazione riduce margine di recupero.
NOTES:
- Instabilita long-horizon puo essere latente prima di diventare BLOCCATO esplicito.

## 70. INSTITUTIONAL TRUST SEMANTICS
RULE_ID: INSTITUTIONAL-TRUST-001
CATEGORY: INSTITUTIONAL_TRUST
STATUS: ACTIVE
SOURCE: MASTER + TL
DESCRIPTION: La fiducia istituzionale evolve storicamente in base a affidabilita governance e precedenti operativi.
CONSTRAINTS:
- Persistent governance reliability: affidabilita governance osservata nel tempo.
- Historical operational trust: fiducia derivata da esiti operativi storici coerenti.
- Escalation credibility: credibilita escalation basata su utilita reale pregressa.
- Institutional reasoning confidence: confidenza sul ragionamento istituzionale.
- Long-term stabilization reliability: affidabilita delle strategie di stabilizzazione.
- Governance reputation semantics: reputazione operativa come segnale di fiducia.
- Operational precedent reliability: precedenti robusti aumentano fiducia decisionale.
- Trust degradation accumulation: errori ricorrenti riducono fiducia progressivamente.
NOTES:
- Trust non e istantaneo: cresce/decresce con storia verificabile.

## 71. CROSS-CONTEXT COGNITION SEMANTICS
RULE_ID: CROSSCONTEXT-COGNITION-001
CATEGORY: INSTITUTIONAL_CROSSCONTEXT
STATUS: ACTIVE
SOURCE: MASTER + TL
DESCRIPTION: Il ragionamento cross-context trasferisce pattern in modo bounded, causale e verificabile.
CONSTRAINTS:
- Pattern transfer: trasferire pattern solo con analogia operativa esplicita.
- Contextual analogy: analogie devono dichiarare limiti di validita.
- Controlled semantic reuse: riuso semantico subordinato a SOURCE OF TRUTH POLICY.
- Operational similarity recognition: riconoscere similarita senza forzare equivalenze.
- Cross-route learning: apprendere tra route diverse con vincoli dichiarati.
- Cross-station stabilization transfer: trasferire pratiche di stabilizzazione compatibili.
- Historical analogy awareness: usare precedenti analoghi con cautela contestuale.
- Bounded contextual inference: inferenze cross-context sempre TL-verificabili.
NOTES:
- Cross-context non autorizza generalizzazioni non spiegabili.

## 72. INSTITUTIONAL MEMORY SEMANTICS
RULE_ID: INSTITUTIONAL-MEMORY-001
CATEGORY: INSTITUTIONAL_MEMORY
STATUS: ACTIVE
SOURCE: TL + MASTER
DESCRIPTION: La memoria istituzionale conserva lezioni operative persistenti e influenza la governance futura.
CONSTRAINTS:
- Persistent operational lessons: lezioni consolidate restano riferimento decisionale.
- Stabilization precedent memory: memoria dei percorsi storici di stabilizzazione.
- Escalation history: storia escalation come base di triage futuro.
- Institutional operational scars: tracce di failure critici da non ripetere.
- Chronic instability memory: memoria di instabilita ricorrenti non risolte.
- Recurring governance failures: ricorrenze failure guidano priorita preventive.
- Long-term operational pattern retention: persistenza pattern utili a previsione causale.
- Institutional adaptation history: storia adattamenti e loro efficacia.
NOTES:
- Memoria istituzionale orienta escalation, non sostituisce conferma TL.

## 73. INSTITUTIONAL HUMAN-IN-THE-LOOP SEMANTICS
RULE_ID: INSTITUTIONAL-HITL-001
CATEGORY: INSTITUTIONAL_HITL
STATUS: ACTIVE
SOURCE: TL + MASTER
DESCRIPTION: La continuita istituzionale resta human-led con TL come ancora contestuale e autorita finale.
CONSTRAINTS:
- TL remains: institutional operational authority, contextual continuity anchor, governance stabilizer, operational memory interpreter, final contextual validator.
- AI remains: bounded institutional reasoning support, memory visibility layer, continuity analysis support, historical propagation support, explainable institutional cognition support.
- Human contextual continuity superiority: il contesto reale TL prevale su inferenze istituzionali non confermate.
- Nessuna autonomia istituzionale AI puo bypassare authority umana finale.
NOTES:
- HITL istituzionale e vincolo permanente di continuita operativa.

## 74. INSTITUTIONAL EXPLAINABILITY CONTRACT
RULE_ID: INSTITUTIONAL-EXPLAINABILITY-001
CATEGORY: INSTITUTIONAL_EXPLAINABILITY
STATUS: ACTIVE
SOURCE: MASTER
DESCRIPTION: Ogni catena istituzionale deve essere storicamente coerente, causale e audit-friendly.
CONSTRAINTS:
- Deve spiegare: perche pattern operativi persistono, perche instabilita si accumula storicamente, perche trust degrada/migliora, perche continuita governance conta, perche stabilizzazione storica riesce/fallisce, perche colli ricorrenti persistono, perche memoria istituzionale influenza escalation.
- Deve restare explainable, causal, TL-readable, governance-compatible, historically coherent, audit-friendly.
- Incertezza elevata deve emergere come INFERITO/DA_VERIFICARE con escalation contestuale.
NOTES:
- Contratto istituzionale estende explainability strategica e autonomica.

## 75. INSTITUTIONAL INTELLIGENCE INDEX STABILITY
RULE_ID: INSTITUTIONAL-INDEX-STABILITY-001
CATEGORY: GOVERNANCE_INSTITUTIONAL_INDEX
STATUS: ACTIVE
SOURCE: MASTER
DESCRIPTION: Gli indici istituzionali devono restare stabili, leggeri e cross-referenceable.
CONSTRAINTS:
- Tassonomie istituzionali permanenti introdotte solo via MASTER.
- Indici esterni possono referenziare ma non ridefinire autorita istituzionale.
- Cross-reference obbligatorio tra reasoning, trust, memoria e HITL istituzionale.
NOTES:
- Mantiene interrogabilita AI coerente su orizzonte lungo.

## 76. INSTITUTIONAL STABILIZATION
RULE_ID: INSTITUTIONAL-STABILIZATION-001
CATEGORY: GOVERNANCE_INSTITUTIONAL_WORLD_MODEL
STATUS: ACTIVE
SOURCE: MASTER
DESCRIPTION: Il MASTER e substrato ufficiale di institutional operational intelligence per l'architettura cognitiva ATLAS futura.
CONSTRAINTS:
- Nessuna authority istituzionale autonoma fuori confini TL + SOURCE OF TRUTH POLICY.
- Anti-drift semantico rafforzato su continuita, memoria e trust storico.
- Continuity governance obbligatoria tra turni e contesti operativi.
- TL continuity supremacy non riducibile da estensioni future.
- Anti-fragmentazione: nessuna semantica istituzionale permanente fuori MASTER.
NOTES:
- Consolidamento finale del layer istituzionale di operational intelligence bounded.

## 77. ECOSYSTEM OPERATIONAL SEMANTICS
RULE_ID: ECOSYSTEM-OPERATIONS-001
CATEGORY: ECOSYSTEM_OPERATIONS
STATUS: ACTIVE
SOURCE: MASTER + TL
DESCRIPTION: L'ecosistema operativo connette contesti multipli con coordinamento bounded e continuita causale.
CONSTRAINTS:
- Operational ecosystem continuity: continuita tra domini operativi interdipendenti.
- Cross-domain operational dependencies: dipendenze esplicite tra contesti istituzionali distinti.
- Ecosystem-scale stabilization: stabilizzazione cooperativa senza perdita di authority locale.
- Institutional interaction semantics: interazioni tra istituzioni con confini dichiarati.
- Persistent coordination behavior: coordinamento ripetibile nel lungo periodo.
- Distributed operational equilibrium: equilibrio distribuito tra nodi operativi.
- Ecosystem bottleneck propagation: colli locali possono propagare stress cross-context.
- Bounded coordination semantics: coordinamento sempre entro governance e HITL boundaries.
NOTES:
- Ecosystem reasoning resta bounded, explainable e governance-constrained.

## 78. FEDERATED OPERATIONAL COGNITION
RULE_ID: FEDERATED-COGNITION-001
CATEGORY: ECOSYSTEM_FEDERATION
STATUS: ACTIVE
SOURCE: MASTER + TL
DESCRIPTION: La cognizione federata abilita interoperabilita semantica senza fusione autonoma delle authority.
CONSTRAINTS:
- Federated operational reasoning: ragionamento distribuito con preservazione contesto locale.
- Distributed contextual cognition: ogni nodo mantiene interpretazione contestuale.
- Multi-context coordination: coordinamento tra contesti con regole esplicite.
- Bounded semantic federation: federazione limitata da policy e trust gates.
- Contextual synchronization: sincronizzazione su stati compatibili e verificabili.
- Institutional reasoning interoperability: interoperabilita senza override reciproco implicito.
- Cross-context governance alignment: allineamento governance senza centralizzazione autonoma.
- Distributed stabilization semantics: stabilizzazione cooperativa con responsabilita separate.
NOTES:
- Federazione non implica merger autonomico di governance.

## 79. ECOSYSTEM RESILIENCE SEMANTICS
RULE_ID: ECOSYSTEM-RESILIENCE-001
CATEGORY: ECOSYSTEM_RESILIENCE
STATUS: ACTIVE
SOURCE: MASTER + TL
DESCRIPTION: La resilienza ecosistemica gestisce degrado e recupero distribuiti con cooperazione bounded.
CONSTRAINTS:
- Ecosystem degradation: degrado progressivo su rete multi-contesto.
- Cross-context instability propagation: instabilita locale puo diffondersi tra domini.
- Distributed resilience buffering: buffering coordinato per assorbire stress.
- Institutional stabilization cooperation: cooperazione tra istituzioni per contenimento.
- Ecosystem containment semantics: isolamento propagazioni critiche cross-context.
- Resilience interoperability: pratiche resilienza compatibili tra contesti.
- Cascading ecosystem stress: stress concatenato su piu nodi operativi.
- Multi-context recovery coordination: recupero orchestrato tra contesti distinti.
NOTES:
- Resilienza ecosistemica resta cooperativa, bounded e explainable.

## 80. CIVILIZATION-SCALE OPERATIONAL MEMORY
RULE_ID: CIVSCALE-MEMORY-001
CATEGORY: ECOSYSTEM_MEMORY
STATUS: ACTIVE
SOURCE: TL + MASTER
DESCRIPTION: La memoria operativa ecosistemica conserva precedenti distribuiti su orizzonti lunghi.
CONSTRAINTS:
- Ecosystem operational memory: memoria di pattern e crisi cross-contesto.
- Cross-context institutional memory: retention di lezioni tra istituzioni.
- Distributed stabilization precedents: precedenti di stabilizzazione federata.
- Historical coordination semantics: semantica storica delle cooperazioni riuscite/fallite.
- Persistent ecosystem scars: tracce di failure sistemici ricorrenti.
- Multi-context escalation memory: memoria escalation trasferibile con vincoli.
- Long-range operational continuity: continuita oltre singolo turno/dominio.
- Institutional historical propagation: propagazione storica di pratiche efficaci/inefficaci.
NOTES:
- Memoria resta bounded, contestuale, explainable e governance-constrained.

## 81. CROSS-INSTITUTIONAL TRUST SEMANTICS
RULE_ID: CROSSINSTITUTIONAL-TRUST-001
CATEGORY: ECOSYSTEM_TRUST
STATUS: ACTIVE
SOURCE: MASTER + TL
DESCRIPTION: La fiducia cross-istituzionale abilita coordinamento federato con limiti espliciti e reversibili.
CONSTRAINTS:
- Federated trust boundaries: soglie fiducia per cooperazione tra contesti.
- Cross-context reliability semantics: affidabilita valutata per dominio e storico.
- Distributed governance trust: fiducia distribuita senza autorita unica implicita.
- Interoperability confidence: confidenza nella compatibilita operativa tra nodi.
- Escalation trust transfer: trasferimento escalation solo con condizioni verificate.
- Bounded trust propagation: fiducia non propaga illimitatamente.
- Institutional coherence trust: fiducia legata a coerenza semantica osservata.
- Ecosystem reliability awareness: consapevolezza affidabilita complessiva rete.
NOTES:
- Propagazione trust deve restare bounded, explainable, reversible e auditable.

## 82. ECOSYSTEM HITL GOVERNANCE
RULE_ID: ECOSYSTEM-HITL-001
CATEGORY: ECOSYSTEM_HITL
STATUS: ACTIVE
SOURCE: TL + MASTER
DESCRIPTION: La governance ecosistemica resta human-in-the-loop con authority contestuale istituzione-bound.
CONSTRAINTS:
- Human authority remains contextual, institution-bound, governance-superior, final escalation authority.
- AI remains bounded ecosystem cognition support, interoperability analysis support, continuity visibility layer, distributed propagation analysis layer.
- Human institutional contextual superiority: validazione finale umana su conflitti cross-contesto.
- Nessuna semantica federata puo ridurre TL/HITL supremacy boundaries.
NOTES:
- HITL ecosistemico preserva authority locali e coordinamento cooperativo.

## 83. ECOSYSTEM EXPLAINABILITY CONTRACT
RULE_ID: ECOSYSTEM-EXPLAINABILITY-001
CATEGORY: ECOSYSTEM_EXPLAINABILITY
STATUS: ACTIVE
SOURCE: MASTER
DESCRIPTION: Ogni ragionamento ecosistemico deve essere causale, interoperabile e leggibile per governance HITL.
CONSTRAINTS:
- Deve spiegare: perche instabilita propaga cross-context, perche coordinamento fallisce/riesce, perche trust propaga/degrada, perche buffering resilienza si attiva, perche escalation ecosistemica avviene, perche sincronizzazione istituzionale destabilizza/stabilizza, perche recovery distribuito riesce/fallisce.
- Deve restare explainable, causal, governance-compatible, TL/HITL-readable e audit-friendly.
- Deve dichiarare confini, assunzioni e limiti di trasferibilita cross-contesto.
NOTES:
- Contratto ecosistemico estende explainability istituzionale senza autonomia sistemica.

## 84. ECOSYSTEM INDEX STABILITY
RULE_ID: ECOSYSTEM-INDEX-STABILITY-001
CATEGORY: GOVERNANCE_ECOSYSTEM_INDEX
STATUS: ACTIVE
SOURCE: MASTER
DESCRIPTION: Gli indici ecosistemici devono restare leggeri, stabili e cross-referenceable.
CONSTRAINTS:
- Tassonomie ecosistemiche permanenti introdotte solo via MASTER.
- Indici esterni possono referenziare ma non ridefinire bounded federation semantics.
- Cross-reference obbligatorio tra operations, federation, resilience, trust e HITL ecosistemico.
NOTES:
- Mantiene recupero semantico robusto per federated cognition ATLAS.

## 85. ECOSYSTEM GOVERNANCE STABILIZATION
RULE_ID: ECOSYSTEM-STABILIZATION-001
CATEGORY: GOVERNANCE_ECOSYSTEM_WORLD_MODEL
STATUS: ACTIVE
SOURCE: MASTER
DESCRIPTION: Il MASTER e substrato ufficiale di bounded ecosystem-scale operational cognition per ATLAS futuro.
CONSTRAINTS:
- Vietata qualsiasi semantica di autonomia ecosistemica non supervisionata da authority HITL.
- Bounded federation semantics obbligatoria: interoperabilita senza perdita authority contestuale.
- Anti-drift rafforzato su coordinamento distribuito, trust transfer e memoria ecosistemica.
- TL/HITL supremacy boundaries non riducibili da estensioni future.
- Anti-fragmentazione: nessuna authority ecosistemica permanente fuori MASTER.
NOTES:
- Consolidamento finale del layer ecosistemico di institutional coordination bounded.

## 86. EXECUTABLE SEMANTIC CONTRACTS
RULE_ID: EXECUTABLE-CONTRACTS-001
CATEGORY: EXECUTABLE_GOVERNANCE
STATUS: ACTIVE
SOURCE: MASTER
DESCRIPTION: I contratti semantici sono la base eseguibile di governance senza introdurre autonomia runtime.
CONSTRAINTS:
- Domini contrattuali obbligatori: planner, explainability, governance, confidence, escalation, HITL, semantic safety, bounded autonomy.
- Ogni contratto deve esporre: semantic scope, enforcement semantics, validation semantics, escalation behavior, TL confirmation requirements, rollback semantics, explainability obligations.
- Contratti sempre governance-first, explainable, bounded, TL-supervised.
NOTES:
- I contratti definiscono controlli semantici, non motori di esecuzione.

## 87. MACHINE-QUERYABLE SEMANTIC MAPS
RULE_ID: MACHINE-QUERYABLE-001
CATEGORY: EXECUTABLE_QUERYABILITY
STATUS: ACTIVE
SOURCE: MASTER
DESCRIPTION: Le semantiche devono essere interrogabili in forma stabile per validazione e explainability.
CONSTRAINTS:
- Mappe obbligatorie: semantic registries, rule maps, governance maps, relationship maps, confidence maps, escalation maps, explainability maps, propagation maps.
- Le mappe restano dichiarative, senza dipendenza da implementazione runtime.
- Ogni mappa deve mantenere cross-reference verso RULE_ID canonici.
NOTES:
- Queryability semantica prepara enforcement e auditing futuri.

## 88. GOVERNANCE ENFORCEMENT SEMANTICS
RULE_ID: GOVERNANCE-ENFORCEMENT-001
CATEGORY: EXECUTABLE_ENFORCEMENT
STATUS: ACTIVE
SOURCE: MASTER
DESCRIPTION: L'enforcement semantico applica gate e controlli reversibili sulla coerenza operativa.
CONSTRAINTS:
- Gate obbligatori: semantic gates, reasoning validation, explainability validation, governance integrity checks, drift enforcement, escalation enforcement, bounded authority enforcement, semantic rollback semantics.
- Enforcement sempre explainable, reversible, audit-friendly e TL-governed.
- Nessuna enforcement chain puo bypassare SOURCE OF TRUTH POLICY o TL/HITL supremacy.
NOTES:
- Enforcement semantico e controllo di ammissibilita, non esecuzione autonoma.

## 89. EXECUTABLE EXPLAINABILITY MODEL
RULE_ID: EXECUTABLE-EXPLAINABILITY-001
CATEGORY: EXECUTABLE_EXPLAINABILITY
STATUS: ACTIVE
SOURCE: MASTER
DESCRIPTION: Ogni chain operativa deve soddisfare condizioni minime di spiegabilita eseguibile.
CONSTRAINTS:
- Campi minimi obbligatori: causal basis, propagation basis, confidence basis, escalation basis, governance basis, uncertainty basis, override basis, stabilization basis.
- Explainability sufficiency minima: completezza causale + coerenza con RULE_ID + leggibilita TL.
- Se insufficiente: output DA_VERIFICARE o escalation TL obbligatoria.
NOTES:
- Questo modello rende verificabile la qualita della spiegazione.

## 90. OPERATIONAL VALIDATION SEMANTICS
RULE_ID: OPERATIONAL-VALIDATION-001
CATEGORY: EXECUTABLE_VALIDATION
STATUS: ACTIVE
SOURCE: MASTER
DESCRIPTION: La validazione semantica verifica coerenza operativa prima di ammettere decisioni.
CONSTRAINTS:
- Validazioni obbligatorie: semantic consistency, governance coherence, planner integrity, escalation validity, confidence validity, explainability sufficiency, bounded autonomy validity, contradiction detection.
- Validazione orientata a governance, operativa, explainable e bounded.
- Contraddizioni non risolte bloccano ammissibilita o forzano escalation TL.
NOTES:
- Validazione semantica e prerequisito di readiness.

## 91. SEMANTIC EXECUTION READINESS
RULE_ID: EXECUTION-READINESS-001
CATEGORY: EXECUTABLE_READINESS
STATUS: ACTIVE
SOURCE: MASTER
DESCRIPTION: La readiness semantica definisce quando una decisione e ammissibile a livelli esecutivi futuri.
CONSTRAINTS:
- Requisiti: execution eligibility, governance admissibility, semantic readiness, validation prerequisites, escalation prerequisites, trust prerequisites, explainability prerequisites, rollback readiness.
- Readiness non implica autonomia esecutiva o riduzione confini HITL.
- In assenza prerequisiti: mantenere stato DA_VERIFICARE/BLOCCATO con percorso di escalation.
NOTES:
- Readiness e un gate semantico, non permesso automatico all'azione.

## 92. SEMANTIC COMPRESSION & NORMALIZATION
RULE_ID: SEMANTIC-COMPRESSION-001
CATEGORY: EXECUTABLE_NORMALIZATION
STATUS: ACTIVE
SOURCE: MASTER
DESCRIPTION: La semantica deve restare densa, non inflazionata, con vocabolario stabile e enforceable.
CONSTRAINTS:
- Ridurre duplicazioni concettuali tramite pattern unificati.
- Unificare overlapping governance patterns in regole canoniche riusabili.
- Stabilizzare vocabolario e ridurre ridondanza descrittiva.
- Ogni nuova sezione deve aggiungere valore di operationalization verificabile.
NOTES:
- Obiettivo: piu chiarezza e queryability, non crescita volumetrica.

## 93. EXECUTABLE GOVERNANCE INDEX LAYER
RULE_ID: EXECUTABLE-INDEX-001
CATEGORY: EXECUTABLE_INDEX
STATUS: ACTIVE
SOURCE: MASTER
DESCRIPTION: Indici eseguibili per retrieval semantico, enforcement e validazione.
CONSTRAINTS:
- Indici obbligatori: EXECUTABLE CONTRACT INDEX, VALIDATION INDEX, ENFORCEMENT INDEX, EXPLAINABILITY CONTRACT INDEX, SEMANTIC GATE INDEX, EXECUTION READINESS INDEX.
- Gli indici devono restare lightweight, semantic, operational, cross-referenceable.
- Gli indici referenziano solo authority interna al MASTER.
NOTES:
- Layer ponte tra semantica e futuri controlli operativi.

## 94. GOVERNANCE LEGACY FOR TL
RULE_ID: TL-GOVERNANCE-LEGACY-001
CATEGORY: EXECUTABLE_TL_LEGACY
STATUS: ACTIVE
SOURCE: TL + MASTER
DESCRIPTION: PROMETEO preserva e trasferisce governance operativa umana, non la sostituisce.
CONSTRAINTS:
- Institutional TL governance continuity: continuita dell'autorita TL nel tempo.
- Operational governance inheritance: ereditarieta delle pratiche robuste validate.
- Persistent governance authority: authority TL persistente su escalation critiche.
- Explainable governance lineage: tracciabilita storica delle scelte di governance.
- Strategic operational stewardship: stewardship umana come asse del sistema.
- Bounded institutional transfer semantics: trasferimento conoscenza entro confini verificabili.
NOTES:
- Il sistema operationalizza conoscenza umana, non la rimpiazza.

## 95. EXECUTABLE GOVERNANCE STABILIZATION
RULE_ID: EXECUTABLE-STABILIZATION-001
CATEGORY: GOVERNANCE_EXECUTABLE_WORLD_MODEL
STATUS: ACTIVE
SOURCE: MASTER
DESCRIPTION: Il MASTER e autorita eseguibile di governance semantica per l'architettura operativa futura ATLAS.
CONSTRAINTS:
- Anti-fragmentazione enforcement: nessuna authority eseguibile permanente fuori MASTER.
- Semantic integrity enforcement: drift e contraddizioni devono essere rilevati e contenuti.
- HITL supremacy enforcement: nessuna catena puo ridurre autorita TL/HITL.
- Governance rollback protection: ogni adattamento deve restare reversibile e auditabile.
- Vietata introduzione di autonomia esecutiva runtime non supervisionata.
NOTES:
- Stabilizzazione finale del layer di executable semantic operationalization.
