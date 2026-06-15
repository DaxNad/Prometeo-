# MEMORY_RETRIEVAL_RUNTIME_CONTRACT_001

Fonte primaria: `docs/MEMORY_RETRIEVAL_BINDING_CONTRACT_001.md`.

## 1. Scopo

Questo contratto prepara un futuro runtime binding governato per usare
`ContextPack` come supporto contestuale read-only.

Questa capability non implementa runtime, non crea test, non modifica backend,
non modifica `memory/` e non collega la pipeline a TL Chat,
`governed_retrieval.py`, planner, LLM locale, database o SMF.

Obiettivi del contratto:

- definire input ammessi per un futuro runtime binding;
- definire output ammesso;
- definire gate obbligatori prima di qualunque integrazione runtime;
- mantenere `ContextPack` come supporto, non come fonte autorevole;
- impedire integrazione diretta non testata.

## 2. Principio architetturale

La pipeline memory/retrieval resta una pipeline di evidence candidate:

```text
memory/*.md autorizzati
-> EvidenceItem
-> ContextPack
```

Principi:

- `memory/` produce `EvidenceItem` solo da fonti autorizzate.
- `ContextPack` ordina, limita e rende spiegabili le evidence candidate.
- `ContextPack` non decide.
- `ContextPack` non promuove `confidence`.
- AI, agenti e LLM non sono fonti autorevoli.
- Planner suggerisce, non decide.
- TL resta autorita operativa finale.
- Specifica reale e conferma TL prevalgono sempre su `ContextPack`.

Nessuna informazione da `ContextPack` puo promuovere automaticamente una
`INFERENZA` o un `DA_VERIFICARE` a `CERTO`.

## 3. Input ammessi per futuro runtime

Un futuro runtime potra ricevere solo:

- query o intent esplicito;
- `memory_root` autorizzato;
- `max_items`;
- `max_chars_per_item`;
- context purpose;
- caller dichiarato.

Il futuro runtime non potra ricevere:

- path arbitrari;
- file fuori `memory/`;
- contenuto sensibile;
- prompt libero non classificato;
- dati produttivi reali grezzi;
- `.env` o segreti.

Ogni input dovra essere validato prima di generare o restituire un
`ContextPack`.

## 4. Output ammesso

Un futuro runtime potra restituire solo:

- `ContextPack`;
- `selected_count`;
- `total_candidates`;
- `truncated`;
- `build_reason`;
- items con:
  - `source_id`;
  - `source_path`;
  - `authority`;
  - `confidence`;
  - `section`;
  - `text`;
  - `reason`;
  - `rank_reason`.

Il futuro runtime non potra restituire:

- decisioni operative finali;
- modifiche a stato ordine;
- comandi di apply;
- suggerimenti planner vincolanti;
- promozioni automatiche a `CERTO`.

## 5. Gate obbligatori futuri

Prima di qualunque runtime binding dovranno esistere almeno:

- contract test sul runtime contract;
- test su `ContextPack`;
- test anti-sensitive;
- test no-runtime-mutation;
- test no-TL-Chat-side-effect;
- test no-planner-side-effect;
- test no-SMF/database-write;
- audit log minimo o preview log read-only.

Senza questi gate, il runtime binding deve restare non implementato.

## 6. Divieti espliciti

Questo contratto vieta:

- collegamento diretto a TL Chat in questa fase;
- chiamata diretta da `governed_retrieval.py` senza capability dedicata;
- uso LLM locale;
- planner mutation;
- backend mutation;
- scrittura su `memory/`;
- scrittura su SMF;
- scrittura su database;
- lettura di `specs_finitura/`;
- lettura di `.env`;
- lettura immagini/PDF/Excel reali;
- uso di `ContextPack` come fonte superiore a specifica reale o conferma TL;
- promozione automatica di `INFERENZA` o `DA_VERIFICARE` a `CERTO`;
- accesso a dati produttivi reali grezzi;
- apply operativo;
- side effect runtime non dichiarati e non testati.

Qualunque eccezione richiede capability dedicata, contratto aggiornato e guard
automatico prima dell'implementazione.

## 7. Stop condition

Il futuro runtime deve fermarsi e restituire esito vuoto o blocked se:

- `memory_root` non e autorizzato;
- `ContextPack` contiene `sensitive=true`;
- `source_path` non e sotto `memory/`;
- `confidence` e mancante;
- `authority` e mancante;
- caller non e dichiarato;
- query o intent e vuoto o non classificato;
- viene richiesto apply o mutation;
- viene richiesto accesso a fonti vietate.

In presenza di stop condition, il runtime non deve generare decisioni
operative, non deve chiamare planner e non deve modificare backend, database,
SMF o `memory/`.

## 8. Schema preview runtime futuro

Schema testuale minimo, non codice eseguibile:

```text
runtime_request:
- query
- intent
- caller
- memory_root
- max_items
- max_chars_per_item
- dry_run

runtime_response:
- ok
- blocked
- block_reason
- context_pack
- audit_reason
```

Il campo `dry_run` deve restare obbligatorio nella prima versione runtime. La
risposta deve essere spiegabile e non deve produrre side effect.

## 9. Criteri futuri per MEMORY_RETRIEVAL_RUNTIME_GUARD_001

La futura capability `MEMORY_RETRIEVAL_RUNTIME_GUARD_001` dovra verificare:

- documento `docs/MEMORY_RETRIEVAL_RUNTIME_CONTRACT_001.md` presente;
- sezioni obbligatorie presenti;
- input ammessi presenti;
- output ammesso presente;
- gate obbligatori presenti;
- divieti presenti;
- stop condition presenti;
- schema request/response presente;
- nessuna frase che autorizzi TL Chat binding diretto;
- nessuna frase che autorizzi mutation/runtime apply;
- nessuna frase che autorizzi LLM locale;
- nessuna frase che autorizzi planner mutation;
- nessuna frase che autorizzi scrittura su `memory/`, SMF o database.

Il guard dovra fallire se il contratto viene modificato per autorizzare
integrazione runtime diretta prima di una capability implementativa dedicata.

## 10. Non obiettivi

Questa capability non deve:

- implementare codice;
- creare test;
- modificare backend;
- modificare `memory/`;
- collegare runtime;
- collegare TL Chat;
- collegare `governed_retrieval.py`;
- usare LLM;
- modificare planner;
- scrivere su database o SMF;
- leggere dati sensibili;
- fare commit, push o PR.

## 11. Verdict del contratto

`MEMORY_RETRIEVAL_RUNTIME_CONTRACT_001` e completo quando il documento definisce
il perimetro di un futuro runtime binding governato e non autorizza alcuna
integrazione runtime diretta in questa capability.

Verdict atteso per questa capability: `PASS_DOCUMENTALE`.
