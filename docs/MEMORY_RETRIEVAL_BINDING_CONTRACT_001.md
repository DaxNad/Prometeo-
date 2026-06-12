# MEMORY_RETRIEVAL_BINDING_CONTRACT_001

Fonte primaria: `docs/PROMETEO_MASTER.md`.

## 1. Scopo

Questo contratto prepara un futuro binding read-only tra `memory/` e retrieval
governato.

Questa capability non implementa runtime, non crea helper, non crea test, non
modifica `memory/` e non collega la memoria a TL Chat, planner, LLM locale o
backend mutation.

Obiettivi del contratto:

- definire quali file `memory/` potranno essere letti in futuro;
- definire quali sezioni saranno leggibili;
- definire il formato minimo di evidence candidate;
- fissare fonti vietate e stop condition;
- impedire che `memory/` diventi fonte automatica di verita operativa.

## 2. Principio architetturale

`memory/` non e fonte automatica di verita.

`memory/` puo produrre solo evidence candidate, cioe contesto sintetico
governato che deve restare subordinato a:

1. specifica reale;
2. conferma TL;
3. `docs/PROMETEO_MASTER.md`;
4. struttura dominio;
5. fonti operative autorizzate.

Regole:

- AI, agenti e LLM non sono fonti autorevoli.
- Planner suggerisce, non decide.
- TL resta autorita operativa finale.
- Nessuna informazione da `memory/` puo promuovere automaticamente una
  `INFERENZA` o un `DA_VERIFICARE` a `CERTO`.
- Nessuna evidence candidate da `memory/` puo prevalere su specifica reale,
  conferma TL o `PROMETEO_MASTER.md`.

## 3. File ammessi in futuro

Un futuro helper read-only potra leggere solo file Markdown sotto `memory/`.

Ogni file leggibile dovra avere front matter YAML valido e tutti questi campi:

- `memory_id`;
- `type`;
- `status`;
- `authority`;
- `confidence`;
- `allowed_for_retrieval`;
- `sensitive`;
- `last_review`.

Condizioni obbligatorie:

- `allowed_for_retrieval: true`;
- `sensitive: false`;
- `memory_id` presente e non vuoto;
- `type` presente e non vuoto;
- `status` presente e non vuoto;
- `authority` presente e non vuoto;
- `confidence` presente e non vuoto;
- `last_review` presente e non vuoto.

Se una sola condizione manca, il file deve essere escluso dal retrieval.

## 4. Sezioni leggibili

Il futuro helper read-only potra estrarre testo solo da queste sezioni:

- `FATTO`;
- `INFERENZA`;
- `DA_VERIFICARE`.

La sezione `NON_USARE_COME_FONTE` puo essere letta solo come guardrail di
esclusione o warning, non come evidence operativa.

Qualunque altra sezione deve essere ignorata dal retrieval salvo contratto
dedicato futuro.

## 5. Output evidence pack

Il futuro binding dovra produrre solo evidence candidate read-only.

Schema minimo per ogni item:

```text
source_id: string
source_path: string
source_type: string
authority: string
confidence: string
section: FATTO | INFERENZA | DA_VERIFICARE
text: string
reason: string
retrieval_allowed: boolean
sensitive: boolean
```

Vincoli:

- `source_id` deve derivare da `memory_id`;
- `source_path` deve restare sotto `memory/`;
- `source_type` deve derivare da `type`;
- `authority` deve derivare dal front matter;
- `confidence` deve derivare dal front matter o dalla sezione, senza
  promozione automatica;
- `retrieval_allowed` deve essere `true`;
- `sensitive` deve essere `false`;
- `reason` deve spiegare perche il testo e stato recuperato.

## 6. Fonti vietate

Il futuro binding deve vietare esplicitamente:

- `.env`;
- `specs_finitura/`;
- `data/local_smf`;
- immagini;
- PDF;
- Excel;
- dump database;
- cache non governate;
- log privati;
- embeddings non governati;
- file fuori `memory/`.

Sono vietati anche path, contenuti o riferimenti che richiedano accesso a dati
produttivi reali, credenziali, token, file privati o documenti sensibili.

## 7. Divieti espliciti

Questo contratto vieta:

- collegamento a TL Chat;
- collegamento a `governed_retrieval.py` runtime;
- LLM locale;
- planner;
- mutation backend;
- scrittura su `memory/`;
- modifica SMF;
- modifica database;
- promozione automatica di `INFERENZA` o `DA_VERIFICARE` a `CERTO`;
- uso di `memory/` come fonte superiore a specifica reale o conferma TL;
- apply operativo;
- side effect runtime;
- lettura di file sensibili o non governati.

Qualunque implementazione futura dovra essere una capability separata,
read-only, testata e senza collegamento TL Chat nella prima versione.

## 8. Criteri futuri per guard

La futura capability `MEMORY_RETRIEVAL_BINDING_GUARD_001` dovra controllare
almeno:

- documento `docs/MEMORY_RETRIEVAL_BINDING_CONTRACT_001.md` presente;
- sezioni obbligatorie presenti;
- divieti espliciti presenti;
- fonti vietate presenti;
- schema evidence pack presente;
- campi front matter richiesti presenti nel contratto;
- nessuna frase che autorizzi runtime binding diretto;
- nessuna frase che autorizzi TL Chat integration;
- nessuna frase che autorizzi LLM locale;
- nessuna frase che autorizzi planner integration;
- nessuna frase che autorizzi backend mutation;
- nessuna frase che autorizzi scrittura su `memory/`, SMF o database.

Il guard dovra fallire se il contratto viene modificato per consentire
integrazione runtime diretta prima di una capability implementativa dedicata.

## 9. Non obiettivi

Questa capability non deve:

- implementare codice;
- creare test;
- modificare `memory/`;
- collegare `memory/` al retrieval;
- modificare TL Chat;
- modificare runtime;
- introdurre LLM locale;
- modificare planner;
- leggere dati sensibili;
- fare commit, push o PR.

## 10. Verdict del contratto

`MEMORY_RETRIEVAL_BINDING_CONTRACT_001` e completo quando il documento definisce
il perimetro read-only futuro e non autorizza alcun binding runtime.

Verdict atteso per questa capability: `PASS_DOCUMENTALE`.
