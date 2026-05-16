# PROMETEO Goal Map

Scopo: trasformare la visione PROMETEO in capacita verificabili, senza usare dati reali nel documento.

Fonte primaria: `docs/PROMETEO_MASTER.md` e `docs/architecture/PROMETEO_MANIFESTO_v1.md`.

## Obiettivo Finale

PROMETEO supporta il Team Leader nella lettura semantica del turno produttivo, evidenziando priorita, vincoli, rischi e incertezze senza assumere autorita autonoma.

## Mappa Capacita

| Capacita richiesta | Moduli coinvolti | Stato attuale | Gap operativo | Prova di completamento |
| --- | --- | --- | --- | --- |
| Riconoscere vincoli bloccanti | `ProductionEvent`, planner, ATLAS | Struttura presente | Dataset pilota consolidato e casi regressione | Caso eval con `blocking_constraint` produce blocco spiegabile e nessuna azione autonoma |
| Distinguere certezza da inferenza | semantic registry, TL Chat, ATLAS | Registry e binding leggeri presenti | Uso uniforme nei percorsi diagnostici | Test mostra `CERTO`, `INFERITO`, `DA_VERIFICARE`, `BLOCCATO` coerenti tra accessor e runtime |
| Segnalare rischio saturazione stazione | planner, ATLAS, TL summary | Segnali tecnici presenti | Casi pilota sintetici e poi campioni reali sanificati | Eval segnala saturazione senza assegnare operatori |
| Gestire componenti condivisi | ATLAS, planner, domain registry | Concetto presente | Copertura sistematica su fanout e conflitti | Eval evidenzia componente condiviso e conflitto evitato |
| Proteggere dati reali verso AI esterna | data boundary guard, AI router | Primo guard locale presente | Enforcement progressivo sugli adapter | Test blocca prompt non sanificato e non salva raw prompt |
| Spiegare decisioni e suggerimenti | explainability, semantic registry | Spiegazioni parziali presenti | Sufficienza minima misurata per capability | Eval richiede causa, vincolo, confidence e azione TL |
| Conservare memoria tecnica locale | `session_memory`, `context_pack.py` | Tooling locale presente | Uso disciplinato per diagnosi e decisioni | `context_pack.py --last N` produce sintesi locale senza leggere dati vietati |

## Regola Di Avanzamento

Una capacita avanza di stato solo se esiste almeno una prova ripetibile:

- test unitario o contract test,
- caso eval sintetico,
- report locale sanificato,
- conferma TL documentata fuori dai dati privati.

## Anti-Goal

PROMETEO non deve diventare:

- CRUD generico,
- planner autonomo non spiegabile,
- canale di uscita per specifiche, BOM, SMF, immagini o dati personali,
- memoria AI esterna per dettagli operativi reali.

## Prossimo Passo Misurabile

Portare le capacita chiave da `STRUCTURAL_READY` a `TESTED_SYNTHETIC` con il primo harness in `evals/prometeo_pilot_cases/`.
