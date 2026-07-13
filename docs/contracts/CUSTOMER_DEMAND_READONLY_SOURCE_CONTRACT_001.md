# CUSTOMER_DEMAND_READONLY_SOURCE_CONTRACT_001

## Stato

- `CONTRACT_STATUS`: `PERIMETER_ONLY`
- `RUNTIME_STATUS`: `NOT_AUTHORIZED`
- `SOURCE_ID_PROPOSED`: `customer_demand_registry`
- `STRUCTURAL_ORIGIN`: tabella logica `customer_demand`
- `ACCESS_MODE_FUTURE`: `READ_ONLY`

Questo documento definisce esclusivamente il perimetro di una possibile fonte
logica futura. Non registra la fonte, non abilita query, non autorizza accesso
al database e non modifica il runtime TL Chat.

## 1. Identità e autorità della fonte

`customer_demand_registry` è il source ID logico proposto per una futura
lettura governata della tabella `customer_demand`.

La tabella è una copia strutturata della domanda cliente importata da una
fonte fisica esterna. Non è la fonte fisica originaria e non prova, da sola,
che il dato sia corrente, confermato o operativo. Il source ID non è presente
in `memory/context_source_index.json` alla data di questo contratto.

Nessun record proveniente da questa fonte può essere classificato
automaticamente come `CERTO`. In assenza di una freshness verificabile e di
una policy di autorità successiva, il dato resta `DA_VERIFICARE` o assume uno stato più prudente.

## 2. Campi leggibili ammessi

Una futura capability runtime potrà restituire esclusivamente un sottoinsieme
dei seguenti campi:

| Campo | Significato ammesso | Limiti |
|---|---|---|
| `articolo` | Chiave articolo usata dal registry per cercare la domanda importata. | Non prova che l'articolo sia attivo o pianificabile. |
| `codice_articolo` | Codice articolo riportato nella copia importata; può essere assente. | Non assumere che sia sempre uguale ad `articolo`, anche se l'importer corrente li valorizza allo stesso modo. |
| `quantita` | Quantità richiesta riportata nella copia importata. | Non equivale a quantità residua, prodotta, spedita, disponibile o assegnata a un ordine. |
| `data_spedizione` | Copia normalizzata della colonna sorgente `Data richiesta cliente` usata dall'importer corrente. | Deve essere presentata come data richiesta cliente registrata, non come spedizione avvenuta o impegno operativo confermato. |
| `priorita_cliente` | Priorità testuale cliente riportata nella copia importata. | Non è una priorità planner e non autorizza sequenziamento o decisioni produttive. |

Campi ulteriori della tabella, inclusi `id`, `note` e `created_at`, non sono
campi business leggibili autorizzati da questo contratto.

## 3. Semantica temporale

Per questa fonte valgono le seguenti distinzioni vincolanti:

- `data_spedizione` è il nome della colonna del registry, ma l'importer
  corrente vi copia `Data richiesta cliente`;
- `data richiesta cliente` è una richiesta importata, non una conferma di
  spedizione, una data di completamento o una decisione di produzione;
- `due_date` non è un campo della tabella `customer_demand` e non può essere
  ricavato da `data_spedizione`;
- non sono ammesse equivalenze tra `data_spedizione`, `due_date`, data
  pianificata, data promessa, data di produzione o data di spedizione
  effettiva senza un contratto successivo e una fonte esplicita.

Se una domanda TL richiede una semantica temporale diversa da quella
documentata, la risposta deve dichiarare il dato mancante invece di adattare o
reinterpretare il valore disponibile.

## 4. Vincoli read-only

Dopo una futura autorizzazione runtime, l'unica classe di operazioni ammessa
sarà `SELECT`, con query parametrizzate e limitate ai campi autorizzati.

Restano vietati:

- `INSERT`, `UPDATE`, `DELETE`, DDL e transazioni mutanti;
- l'esecuzione o l'invocazione di
  `backend/app/importers/import_customer_demand.py`;
- l'accesso diretto al file SMF, al suo path predefinito o a path fisici
  esterni;
- l'uso di `SMFAdapter` o di altri importer;
- l'accesso a `production_orders`, `board_state`, viste di sequenziamento o
  sorgenti planner;
- decisioni di pianificazione, priorità o sequenziamento;
- qualsiasi scrittura indiretta, bootstrap o aggiornamento della fonte.

Il presente contratto non autorizza neppure le query `SELECT`: descrive solo
la forma che potranno assumere dopo una capability runtime separata.

## 5. Provenance minima futura

Ogni risultato futuro dovrà rendere disponibili almeno:

- `source_id`: `customer_demand_registry`;
- tabella logica: `customer_demand`;
- timestamp di lettura, se previsto dall'infrastruttura;
- riferimento e stato della freshness, anche quando il valore è `UNKNOWN`;
- elenco dei campi effettivamente restituiti;
- `source_status`;
- `semantic_status`;
- `confidence`;
- `missing_data`.

Il timestamp di lettura descrive quando è avvenuto il recupero e non dimostra
la freshness della copia. `created_at` esiste nello schema, ma non è tra i
campi autorizzati e, senza una policy verificata sull'importazione, non può
essere assunto come timestamp della fonte fisica originaria.

La provenance non deve esporre `DATABASE_URL`, path filesystem, contenuti del
file SMF o dettagli di connessione.

## 6. Freshness e validità

La freshness deve essere gestita in modo esplicito:

| Condizione | Trattamento richiesto |
|---|---|
| Freshness sconosciuta | Dichiarare `UNKNOWN`, mantenere il dato `DA_VERIFICARE` e richiedere verifica della fonte. |
| Freshness assente | Dichiarare il riferimento mancante in `missing_data`; non usare il record come dato corrente. |
| Freshness scaduta | Dichiarare il dato non corrente e impedirne la presentazione come valido per decisioni operative. |
| Freshness verificata in futuro | Conservare riferimento e criterio usato; la freshness, da sola, non promuove il dato a `CERTO`. |

Non sono ammesse inferenze su esistenza, validità corrente, stato, residuo,
conferma o avanzamento di un ordine. La tabella non contiene un identificativo
ordine autorizzato da questo contratto.

## 7. Stati governati

| Fase | `source_status` richiesto | Esito utente |
|---|---|---|
| Prima della registrazione nel source index | `SOURCE_MISSING` | `MISSING_DATA` per i dati di domanda cliente richiesti. |
| Source ID registrato e autorizzato, runtime ancora disabilitato | `SOURCE_AUTHORIZED_BUT_UNAVAILABLE` | `MISSING_DATA`, con indicazione che la fonte non è disponibile nel runtime. |
| Dopo una futura attivazione completa | Stato prodotto dal reader governato e verificato | Dati restituiti solo con provenance, semantic status, confidence e limiti di freshness. |

`MISSING_DATA` è l'esito rivolto all'utente quando il recupero non è possibile;
non deve essere sostituito da valori inventati. Nessuno degli stati autorizza
una promozione automatica a dato operativo certo.

## 8. Condizioni per una futura attivazione

L'apertura di una capability runtime successiva richiede tutte le seguenti
condizioni:

1. registrazione separata di `customer_demand_registry` nel source index;
2. autorizzazione esplicita del source ID e del perimetro database;
3. reader dedicato e strettamente read-only;
4. query `SELECT` parametrizzate e limitate ai campi ammessi;
5. test di non mutazione del database e di assenza di chiamate all'importer;
6. binding governato con TL Chat, senza fallback a path o fonti non
   autorizzate;
7. definizione verificabile della freshness e del relativo comportamento in
   caso di dato assente, sconosciuto o scaduto;
8. test per fonte presente, mancante, autorizzata ma indisponibile e dato
   temporalmente non affidabile;
9. autorizzazione esplicita tramite una capability successiva.

Il soddisfacimento parziale delle condizioni non abilita il runtime.

## 9. Non autorizzazioni

Questo contratto non autorizza:

- runtime, adapter, reader o binding TL Chat;
- query SQL o accesso al database;
- modifica di `memory/context_source_index.json`;
- creazione o modifica di test;
- uso di `SMFAdapter`, importer o file SMF;
- modifiche a migrazioni SQL o configurazioni runtime;
- accesso a ordini, planner, board o viste di sequenziamento;
- promozione a `CERTO` o decisioni operative.

## 10. Checklist di accettazione reviewer

Un reviewer può determinare da questo documento che:

- la sola fonte logica proposta è `customer_demand_registry`, basata sulla
  tabella `customer_demand`;
- i soli campi business leggibili sono `articolo`, `codice_articolo`,
  `quantita`, `data_spedizione` e `priorita_cliente`;
- `data_spedizione` rappresenta attualmente la copia della data richiesta dal
  cliente e non equivale a `due_date`;
- ogni operazione mutante, importer, path esterno, planner e fonte ordine è
  vietata;
- prima della registrazione la fonte è `SOURCE_MISSING`, mentre dopo una
  futura autorizzazione con runtime disabilitato è
  `SOURCE_AUTHORIZED_BUT_UNAVAILABLE`;
- la copia non è autorità fisica originaria e la freshness deve essere
  dichiarata, mai presunta;
- una capability runtime potrà essere aperta solo dopo il soddisfacimento di
  tutte le condizioni della sezione 8 e una nuova autorizzazione esplicita.

## Stop condition

La consegna termina con questo documento. Non sono autorizzati aggiornamenti
al source index, implementazioni runtime, query, test, reader o binding.
