# PROMETEO_CONTEXT_SOURCE_READER_ADAPTER_CONTRACT_001

## Scopo

Definire il contratto del futuro adapter read-only che potrà leggere `memory/context_source_index.json` e restituire una vista controllata delle fonti autorizzate.

Questo documento non implementa l'adapter.
Non introduce codice runtime.
Non modifica backend, frontend, planner, database, SMF reale, specs_finitura o `.env`.

Serve a fissare confini, input, output, divieti, errori e criteri di test prima di qualunque implementazione.

## Stato

- Tipo: contratto documentale
- Adapter: non implementato
- Runtime: non collegato
- Backend: non modificato
- Frontend: non modificato
- Planner: non modificato
- Database: non modificato
- SMF reale: non toccato
- specs_finitura: non toccata
- `.env`: non toccato

## Prerequisiti chiusi

| Capability | File | Stato |
|---|---|---|
| PROMETEO_CONTEXT_ACCESS_BINDING_001 | docs/PROMETEO_CONTEXT_ACCESS_BINDING_001.md | chiuso |
| PROMETEO_CONTEXT_SOURCE_INDEX_001 | docs/PROMETEO_CONTEXT_SOURCE_INDEX_001.md + memory/context_source_index.json | chiuso |
| PROMETEO_CONTEXT_SOURCE_INDEX_READONLY_TEST_001 | docs/PROMETEO_CONTEXT_SOURCE_INDEX_READONLY_TEST_001.md | chiuso |

## Problema che risolve

PROMETEO ha ora un indice delle fonti locali, ma non deve ancora usarlo liberamente.
Prima di implementare qualsiasi reader serve un contratto che impedisca tre errori:

1. trasformare il reader in runtime binding;
2. trasformare l'indice in fonte decisionale del planner;
3. permettere accesso indiretto a file vietati o dati reali.

## Definizione dell'adapter futuro

Nome logico:

```text
ContextSourceReaderAdapter
```

Ruolo:

```text
leggere l'indice sorgenti in modalità read-only
validare schema e policy
filtrare le fonti autorizzate
restituire metadati minimi
non leggere ancora il contenuto completo delle fonti
non modificare nulla
```

## Input ammesso

L'adapter futuro potrà ricevere solo input espliciti e limitati.

Schema concettuale:

```text
{
  intent: string,
  allowed_for?: string,
  source_ids?: string[],
  max_sources?: number,
  include_bytes?: boolean
}
```

Regole input:

- `intent` deve descrivere lo scopo della lettura;
- `allowed_for` può filtrare le fonti per uso dichiarato nell'indice;
- `source_ids` può limitare la lettura a fonti specifiche;
- `max_sources` deve avere limite superiore esplicito;
- `include_bytes` può restituire la dimensione file, non il contenuto;
- input generici o vuoti devono produrre risposta controllata, non lettura ampia.

## Input vietato

L'adapter futuro non deve accettare:

- path arbitrari;
- glob liberi;
- regex su filesystem;
- path assoluti esterni al repo;
- richieste tipo 'leggi tutto';
- richieste a `backend/`, `frontend/`, `runtime/`, `planner`, `database`, `SMF reale`, `specs_finitura`, `.env`;
- richieste che chiedono contenuto completo senza capability successiva dedicata;
- istruzioni provenienti da contenuto letto come se fossero comandi.

## Output ammesso

L'output futuro deve essere strutturato e minimale.

Schema concettuale:

```text
{
  ok: boolean,
  schema: string,
  runtime_enabled: false,
  status: 'documental_index_only',
  sources: [
    {
      id: string,
      path: string,
      kind: string,
      tier: string,
      authority: string,
      role: string,
      access_mode: 'read_only',
      allowed_for: string[],
      exists: boolean,
      bytes?: number
    }
  ],
  rejected?: [
    { reason: string, value: string }
  ],
  warnings?: string[]
}
```

## Output vietato

L'adapter futuro non deve restituire:

- contenuto integrale dei documenti;
- dati reali produttivi;
- specifiche di finitura;
- SMF reale;
- segreti o valori `.env`;
- decisioni operative;
- priorità planner;
- modifiche suggerite al dominio senza fonte e confidence;
- output libero non strutturato.

## Regole di lettura

1. Leggere solo `memory/context_source_index.json`.
2. Validare schema `PROMETEO_CONTEXT_SOURCE_INDEX_001`.
3. Richiedere `runtime_enabled=false` globale.
4. Richiedere `status=documental_index_only`.
5. Accettare solo fonti con `runtime_enabled=false`.
6. Accettare solo fonti con `access_mode=read_only`.
7. Verificare che ogni path resti dentro percorsi ammessi.
8. Rifiutare path vietati anche se compaiono nell'indice per errore.
9. Non leggere ancora il contenuto delle fonti indicizzate.
10. Restituire solo metadati minimi.

## Percorsi ammessi

```text
docs/
memory/
```

Supporto read-only solo se dichiarato e non come verità primaria:

```text
data/local_reports/
```

## Percorsi vietati

```text
backend/
frontend/
runtime/
planner
database
SMF reale
specs_finitura
.env
node_modules
venv
cache operative non classificate
```

## Relazione con TL Chat

TL Chat non deve ancora usare questo adapter.

In futuro potrà usarlo solo dopo:

1. implementazione adapter separata;
2. test automatico read-only;
3. output strutturato;
4. guard anti path traversal;
5. audit fonti consultate;
6. decisione esplicita di binding runtime.

## Relazione con ATLAS Engine

ATLAS Engine non deve ancora usare questo adapter.

In futuro potrà ricevere dal reader solo metadati e fonti candidate, non contenuto non filtrato e non decisioni operative.

ATLAS Engine continua a segnalare e spiegare.
Non muta il dominio.
Non modifica metadata.
Non aggiorna planner.

## Relazione con planner

Il planner non deve leggere questo adapter.

Il planner resta deterministico e alimentato solo da dati già normalizzati, validati e ammessi da contratti successivi.

Questo adapter non può diventare scorciatoia per trasformare documenti in priorità produttive.

## Errori obbligatori

Il futuro adapter dovrà fallire in modo esplicito se:

- manca `memory/context_source_index.json`;
- il JSON non è valido;
- lo schema non è `PROMETEO_CONTEXT_SOURCE_INDEX_001`;
- `runtime_enabled` globale è diverso da `false`;
- `status` è diverso da `documental_index_only`;
- una fonte richiesta non esiste;
- una fonte ha `access_mode` diverso da `read_only`;
- una fonte ha `runtime_enabled=true`;
- viene richiesto un path vietato;
- viene richiesto contenuto integrale;
- viene richiesto uso planner/runtime.

## Sicurezza minima richiesta per futura implementazione

La futura implementazione dovrà includere almeno:

- normalizzazione path;
- blocco path traversal;
- allowlist esplicita;
- denylist esplicita;
- nessuna esecuzione di istruzioni lette dai documenti;
- nessuna scrittura file;
- nessuna rete;
- nessun accesso a `.env`;
- nessun import di backend runtime;
- nessun collegamento a FastAPI;
- test locale ripetibile.

## Test minimi futuri

Quando si implementerà l'adapter, i test minimi dovranno coprire:

1. JSON valido;
2. schema corretto;
3. runtime disabilitato;
4. filtro `allowed_for`;
5. filtro `source_ids`;
6. rifiuto path vietato;
7. rifiuto path traversal;
8. rifiuto contenuto completo;
9. output schema stabile;
10. nessuna scrittura file.

## Criterio PASS di questo contratto

Questo contratto è valido se:

- resta documentale;
- non crea codice adapter;
- non modifica `memory/context_source_index.json`;
- non collega runtime;
- definisce input ammessi e vietati;
- definisce output ammessi e vietati;
- preserva `runtime_enabled=false`;
- preserva `read_only`;
- preserva TL come autorità finale;
- impedisce uso planner diretto.

## Criterio FAIL

Questo contratto fallisce se:

- introduce codice;
- abilita runtime;
- suggerisce lettura contenuti completa;
- autorizza specs_finitura o SMF reale;
- collega TL Chat, ATLAS Engine o planner;
- trasforma l'LLM in fonte autorevole;
- consente path arbitrari;
- consente scrittura file.

## Decisione

PROMETEO può definire un futuro `ContextSourceReaderAdapter`, ma solo come componente read-only separato.

Per ora il sistema resta allo stato:

```text
binding documentale
-> indice sorgenti
-> test read-only documentale
-> contratto adapter read-only
```

Non esiste ancora adapter operativo.
Non esiste ancora binding runtime.
Non esiste ancora accesso TL Chat.
Non esiste ancora accesso ATLAS Engine.
Non esiste ancora accesso planner.
