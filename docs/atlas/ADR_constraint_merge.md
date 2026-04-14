# ADR: Constraint-Aware Decision Merge

## Contesto

ATLAS riceve segnali parziali da moduli diversi, ciascuno focalizzato su una superficie decisionale specifica: disponibilita componenti, capacita linea, priorita spedizione, pressione dei colli di bottiglia, avanzamento di fase e capacita operatori.

Questi segnali non devono essere fusi con una media statistica, perche il dominio contiene vincoli non compensabili: un blocco materiale non puo essere annullato da una buona priorita commerciale.

## Problema

Serve un livello decisionale puro e deterministico che:

- fonda risultati eterogenei senza accesso a database o runtime esterni;
- preservi una gerarchia esplicita dei vincoli;
- produca un output spiegabile e facile da testare;
- resti estendibile verso solver o policy engine piu sofisticati.

## Scelta Architetturale

Si introduce `decision_merge_engine.py` come modulo isolato nel namespace `atlas_engine`.

Il modulo espone:

- `MergeSignal`: segnale normalizzato prodotto da un modulo di analisi;
- `MergeInput`: contenitore esplicito dei sei ingressi previsti;
- `MergeResult`: esito finale con decisione, score, vincoli attivi, conflitti e explain;
- `solve_decision_merge(input: MergeInput) -> MergeResult`: entry point puro e deterministico.

La precedenza e definita in modo esplicito:

1. `BLOCK` domina sempre.
2. `DEFER` domina `ALLOW`.
3. `BOOST` aumenta il `priority_score`, ma non supera mai `BLOCK` o `DEFER`.
4. `NEUTRAL` e ignorato.

Lo score non usa medie tra moduli. Viene invece derivato dal segnale dominante piu forte, con regole fisse per ciascun livello decisionale.

## Alternative Considerate

1. Media pesata dei punteggi dei moduli.
   Scartata perche rende compensabili vincoli che nel dominio non lo sono.

2. Fusione dentro `solve()` o dentro il runtime applicativo.
   Scartata perche accoppia il merge decisionale a endpoint, orchestrazione e fonti dati.

3. Introduzione immediata di OR-Tools, Pyomo o rule engine esterno.
   Scartata in questo step per mantenere patch minima, testabile e senza dipendenze pesanti.

## Implicazioni Future

- Il modulo puo diventare il punto unico di ingresso per politiche piu avanzate.
- `MergeSignal` puo essere adattato per ricevere output da OR-Tools, Pyomo, planner multi-agent o rule engine esterni.
- La gerarchia di precedenza resta stabile anche se la logica di scoring fine viene sostituita.
- L'assenza di dipendenze runtime lo rende sicuro da riusare in test, simulatori e pipeline di explainability.
