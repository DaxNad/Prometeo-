# PROMETEO — DECISION LOG ARCHIVE

- `STATUS`: `HISTORICAL_NON_AUTHORITATIVE`
- `ARCHIVED_ON`: `2026-07-13`
- `REASON`: decisioni conservate come provenienza; le fonti canoniche correnti prevalgono.
- `DO_NOT_USE_AS`: stato corrente, autorizzazione runtime, capability attiva o `NEXT_MOVE`.

---

# PROMETEO Decision Log

## Regole del registro

Questo file conserva soltanto decisioni consolidate. Non contiene trascrizioni di chat, chain-of-thought, brainstorming, backlog, ipotesi non verificate o output completi dei modelli.

Ogni decisione deve avere:

- identificativo stabile;
- data;
- stato;
- fonti verificabili;
- decisione;
- motivazione sintetica;
- conseguenze e limiti;
- eventuale condizione di revisione.

Un modello può preparare una proposta, ma solo una decisione umana esplicita o una fonte canonica autorizzativa può produrre una voce `CONFIRMED`.

## Decisioni consolidate

### DEC-2026-07-13-001 — Interazione per fasi

- `STATUS`: `CONFIRMED`
- `SCOPE`: metodo di sviluppo PROMETEO
- `SOURCES`:
  - `docs/PROMETEO_PORTABLE_WORK_METHOD_001.md`
  - istruzione umana del 2026-07-13
- `DECISION`: usare le fasi Osservazione, Comprensione, Decisione opzionale, Implementazione e Verifica.
- `RATIONALE`: separare fatti, comprensione, decisione e patch riduce allucinazioni, scope creep e dipendenza da una singola chat.
- `CONSEQUENCES`: nessuna fase eredita automaticamente i permessi della fase precedente; ogni passaggio ha un gate verificabile.
- `REVIEW_WHEN`: il metodo produce duplicazioni o impedisce una chiusura verificabile.

### DEC-2026-07-13-002 — Routing dei ruoli

- `STATUS`: `CONFIRMED`
- `SCOPE`: collaborazione Luna, Terra, Sol, GPT-5.5 e GPT-5.6
- `SOURCES`:
  - `docs/LLM_GOVERNANCE_PROMETEO.md`
  - `docs/PROMETEO_AGENT_OPERATING_MODEL.md`
  - istruzione umana del 2026-07-13
- `DECISION`:
  - Luna osserva il runtime esistente;
  - GPT-5.5 verifica osservazioni e regressioni;
  - Terra definisce il perimetro e implementa solo dopo autorizzazione;
  - Sol interviene solo su una decisione materiale;
  - GPT-5.6 coordina pacchetti, handoff e `NEXT_MOVE`.
- `RATIONALE`: specializzare i ruoli senza trasformarli in agenti autonomi o autorità di dominio.
- `CONSEQUENCES`: i ruoli sono sostituibili; il modello usato non cambia permessi, fonti o gate.
- `REVIEW_WHEN`: cambia la governance AI canonica.

### DEC-2026-07-13-003 — Contesto minimo, non conversazione completa

- `STATUS`: `CONFIRMED`
- `SCOPE`: handoff fra modelli e sessioni
- `SOURCES`:
  - `docs/PROMETEO_PORTABLE_WORK_METHOD_001.md`
  - istruzione umana del 2026-07-13
- `DECISION`: trasferire soltanto stato repository, fonti canoniche, evidenze, scope, decisioni consolidate, unknown e una `NEXT_MOVE`.
- `RATIONALE`: impedire che rumore, istruzioni superate o dati sensibili della chat diventino contesto implicito.
- `CONSEQUENCES`: ogni sessione rigenera il pacchetto; le chat precedenti non sono fonte di verità.
- `REVIEW_WHEN`: il pacchetto minimo non contiene una prova necessaria.

### DEC-2026-07-13-004 — Gate runtime customer demand

- `STATUS`: `SUPERSEDED`
- `SCOPE`: `customer_demand_registry`
- `SOURCES`:
  - `docs/contracts/CUSTOMER_DEMAND_READONLY_SOURCE_CONTRACT_001.md`
  - `docs/capabilities/TL_CHAT_UNIFIED_DATA_ACCESS_VERTICAL_SLICE_002.md`
  - istruzione umana del 2026-07-13
- `DECISION`: non aprire la capability runtime successiva finché il perimetro read-only del reader non è definito e accettato esplicitamente.
- `RATIONALE`: al momento della decisione il contratto era perimeter-only e reader, query, source registration e binding non erano ancora autorizzati.
- `CONSEQUENCES`: la vecchia `NEXT_MOVE` era `DEFINE_CUSTOMER_DEMAND_RUNTIME_READONLY_PERIMETER`; non è più applicabile perché la catena è stata successivamente autorizzata, implementata, verificata e unita.
- `REVIEW_WHEN`: non applicabile; voce conservata come storico.

## Questioni aperte non decisionali originali

Le seguenti voci erano questioni aperte al momento della registrazione e non costituivano autorizzazione:

- forma esatta dell'interfaccia reader;
- boundary di connessione database;
- registrazione del source ID;
- policy verificabile di freshness;
- file allowlist della futura patch;
- binding TL Chat e relativi test.

Queste voci non descrivono lo stato corrente e sono conservate esclusivamente come provenienza storica.

## Template storico

```text
### DEC-YYYY-MM-DD-NNN — Titolo

- STATUS: PROPOSED | CONFIRMED | SUPERSEDED
- SCOPE:
- SOURCES:
- DECISION:
- RATIONALE:
- CONSEQUENCES:
- REVIEW_WHEN:
```
