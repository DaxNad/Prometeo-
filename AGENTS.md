# AGENTS.md — Regole operative vincolanti per Codex in PROMETEO

## 1) Scopo del file
Questo file definisce le regole operative **obbligatorie** che Codex deve seguire quando modifica il repository PROMETEO.

Obiettivo: tradurre i principi architetturali permanenti in criteri pratici di sviluppo, revisione e chiusura modifica.

---

## 2) Fonte architetturale primaria
La fonte architetturale primaria e vincolante è:

- `docs/architecture/PROMETEO_MANIFESTO_v1.md`

In caso di dubbio, conflitto locale o ambiguità implementativa, prevale sempre il Manifesto.

---

## 3) Regole di coerenza dominio (non negoziabili)

### 3.1 Modello dominio centrale
- Non rompere il modello: **Order -> ProductionEvent -> Station/Phase**.
- `Order` resta l'aggregato centrale.
- `ProductionEvent` resta traccia della realtà operativa, non un log secondario opzionale.
- `Station` e `Phase` restano semantiche di processo, non semplici etichette UI.

### 3.2 Unicità semantica cross-modulo
- Non introdurre duplicazioni incoerenti tra `smf_core`, `backend`, `planner`, `frontend`.
- Evitare copie divergenti di regole dominio, enum, mapping, priorità o interpretazioni.
- Ogni regola dominio deve avere una singola fonte autorevole, referenziata dagli altri moduli.

### 3.3 Identità del prodotto
- Non trasformare PROMETEO in CRUD generico.
- Ogni modifica deve preservare la natura di orchestratore semantico decisionale.
- Le feature puramente gestionali sono accettabili solo se rafforzano lettura dominio, continuità operativa o capacità decisionale del Team Leader.

---

## 4) Regole di explainability
- Ogni nuova logica planner o decisionale deve essere spiegabile in output tecnico-funzionale.
- Ogni decisione/suggerimento deve poter esplicitare almeno:
  - perché è stata prodotta,
  - quali vincoli hanno influito,
  - quali conflitti sono stati evitati,
  - quali priorità sono state applicate,
  - eventuali disaccordi tra moduli.
- Evitare euristiche opache non tracciabili.
- Se una decisione non è spiegabile, non è pronta per essere considerata stabile.

---

## 5) Priorità di sviluppo (ordine operativo)
Quando esistono più opzioni implementative, seguire questa priorità:

1. **Guard rail anti-rottura** (sicurezza architetturale e regressioni critiche).
2. **Densificazione dominio reale** (migliore aderenza ai vincoli produttivi reali).
3. **Registry semantico** (famiglie, compatibilità, comportamenti condivisi).
4. **Planner spiegabile** (decisioni motivabili e verificabili).
5. **Interfaccia utile TL** (supporto operativo reale al Team Leader, non cosmetica).

---

## 6) Regole di modifica codice
- Preferire patch **minime, robuste, reversibili**.
- Evitare hardcode fragile (valori magici senza contesto dominio).
- Evitare nuove dipendenze non necessarie o non giustificate dal dominio.
- Preservare modularità, separazione responsabilità e confini tra componenti.
- Non spostare logica dominio critica verso layer inadatti (es. UI-only o adapter temporanei).
- Ogni refactor deve chiarire il dominio, non solo "ripulire" la forma.

---

## 7) Regole di verifica finale (obbligatorie in chiusura)
In ogni chiusura modifica Codex deve dichiarare esplicitamente:

1. Quali file toccano il dominio.
2. Se la modifica impatta uno o più tra:
   - Manifesto / coerenza architetturale,
   - Planner,
   - Registry semantico,
   - Backend dominio.
3. Se è necessaria review architetturale (sì/no) e perché.

Se il cambiamento altera semantica di `Order`, `ProductionEvent`, `Station`, `Phase`, regole planner o coerenza cross-modulo, la review architetturale è fortemente raccomandata.

---

## ARCHITECTURE GUARD CHECKLIST
Prima di chiudere una modifica, Codex deve rispondere **SÌ/NO** a tutte le domande:

1. La modifica preserva il modello `Order -> ProductionEvent -> Station/Phase`?
2. Ho evitato duplicazioni o divergenze tra `smf_core`, `backend`, `planner`, `frontend`?
3. La modifica mantiene PROMETEO come sistema semantico e non come CRUD generico?
4. Le nuove decisioni planner/logiche sono spiegabili con motivazioni e vincoli?
5. Le priorità implementate rispettano l'ordine: guard rail, dominio reale, registry, planner spiegabile, interfaccia TL?
6. Ho applicato patch minime e robuste evitando hardcode fragile?
7. Ho evitato dipendenze nuove non necessarie?
8. La modularità del sistema è preservata o migliorata?
9. Ho indicato chiaramente gli impatti su manifesto/planner/registry/backend?
10. Ho dichiarato se è necessaria review architetturale?

Se una risposta critica è "NO", la modifica non è pronta alla chiusura.

## PROMETEO — Non-negotiable data protection policy

The following rules are mandatory for every AI agent, automation, browser agent, Claude, Codex, ChatGPT, or human-assisted workflow operating on this repository.

### Private production material

The following material is strictly private and must never be committed, pushed, attached to pull requests, copied into public logs, or exposed through generated artifacts:

- `specs_finitura/*/*.png`
- `specs_finitura/*/*.jpg`
- `specs_finitura/*/*.jpeg`
- `specs_finitura/*/*.pdf`
- `specs_finitura/*/metadata.json`
- real Excel production files
- screenshots, photos, industrial documents, database dumps, local logs, API keys, tokens, passwords, real `DATABASE_URL` values, personal names, personal email addresses, and local user paths

Only these `specs_finitura` files may be versioned:

- `specs_finitura/index.json`
- `specs_finitura/_templates/metadata.template.json`

### Forbidden actions

Agents must not run or suggest:

- `git add -f` on private production files
- commits containing private images, metadata, Excel files, dumps, logs, or secrets
- pull requests that modify security guards together with unrelated runtime/application changes
- bypasses of `Privacy Guard` or `Data Leak Guard`

### Required checks before push or merge

Before any push or merge, agents must verify:

- `python3 scripts/privacy_guard_specs.py`
- `python3 scripts/data_leak_guard.py`
- `git status --short`
- `git diff --cached --stat`

A pull request must not be merged if either `Privacy Guard` or `Data Leak Guard` fails.

### Guard policy changes

Changes to guard scripts or guard workflows must be isolated in a dedicated pull request. No runtime, planner, API, frontend, SMF, or domain logic may be mixed into the same PR.


