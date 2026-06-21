# SPEC_INTAKE_PREVIEW_READONLY_BINDING_001

## Status

CONTRACT_ONLY / TEST_ONLY

## Scopo

Permettere a TL Chat di riconoscere l'esistenza di metadata preview locali già generati da SPEC_INTAKE, senza trasformarli in profili operativi attivi.

## Capability

SPEC_INTAKE_PREVIEW_READONLY_BINDING_001

## Ambito ammesso

La capability può leggere solo metadata preview locali già esistenti, con stato esplicito:

- PREVIEW_ONLY
- DA_VERIFICARE
- requires_tl_confirmation = true
- planner_eligible = false

## Output ammesso verso TL Chat

Articolo presente come preview locale DA_VERIFICARE.

Non è un profilo operativo attivo.
Non è planner-eligible.
Serve conferma TL prima di renderlo operativo.

## Ambito vietato

La capability non può:

- rendere un articolo profilo operativo attivo;
- impostare planner_eligible = true;
- scrivere database;
- scrivere SMF;
- normalizzare route definitiva;
- dichiarare componenti, attrezzature o postazioni come CERTE;
- collegare planner;
- collegare ATLAS Engine;
- introdurre retrieval libero;
- leggere immagini, foto o specifiche reali;
- usare LLM libero per interpretazione dati;
- trasformare PREVIEW_ONLY in fonte autoritativa.

## Runtime

runtime_enabled: false

Questa capability è solo contratto documentale.

Ogni futuro binding runtime dovrà essere implementato in una capability separata, con test espliciti e guardrail.

## Planner

planner_enabled: false

La preview non può generare piani, priorità, assegnazioni, workload o decisioni operative.

## Database

db_write: false

Nessuna scrittura database è ammessa.

## SMF

smf_write: false

Nessuna scrittura SMF è ammessa.

## Regola di sicurezza

Una preview SPEC_INTAKE è informazione utile al TL solo come presenza documentale da verificare.

Non è mai fonte operativa certa finché il TL non conferma e finché una capability successiva non la promuove con percorso governato.

## Esempio 12514

Risposta ammessa:

Articolo 12514 presente come preview locale DA_VERIFICARE.

Non è un profilo operativo attivo.
Non è planner-eligible.
Serve conferma TL prima di renderlo operativo.

Risposta vietata:

Articolo 12514 disponibile.
Route confermata.
Componenti confermati.
Planner attivo.

## Verdict

SPEC_INTAKE_PREVIEW_READONLY_BINDING_001 è nello scope solo come read-only preview awareness.

Non è una capability di intake operativo.
Non è una capability planner.
Non è una capability database.
Non è una capability SMF.
