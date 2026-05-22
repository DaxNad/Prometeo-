# CONTROLLED_IMPORT_PIPELINE_V1

## SCOPO

Definire il contratto tecnico minimo per una futura pipeline di import dati
controllata, verificabile e sicura.

Questa capability non importa dati reali e non dichiara completo il flusso di
import. Stabilisce invece le regole minime che ogni implementazione runtime
successiva dovra rispettare per non introdurre scritture dirette, regressioni o
esposizione di dati sensibili.

## INPUT_AMMESSO

Input ammesso solo se:

- proviene da payload sintetico, sanificato o locale autorizzato;
- contiene campi operativi minimi dichiarati;
- e tracciabile a una fonte non sensibile;
- non include allegati reali, immagini, PDF, Excel o specifiche produttive;
- puo essere validato senza accesso a dati reali non versionabili.

Campi minimi attesi per una futura preview:

- identificativo ordine o riferimento sanificato;
- codice articolo sanificato o demo;
- quantita;
- scadenza o priorita se disponibile;
- route/postazione se disponibili;
- nota operativa sanificata opzionale.

## INPUT_VIETATO

Sono vietati:

- dati reali sensibili;
- `specs_finitura/**`;
- `data/local_smf/**`;
- Excel reali;
- PDF reali;
- immagini reali;
- `.env`, token, dump DB;
- log contenenti clienti, operatori, codici o path sensibili;
- qualunque input che richieda OCR reale, AI runtime o cloud.

## VALIDAZIONE

Ogni import futuro deve validare almeno:

- presenza dei campi minimi;
- quantita numerica e positiva;
- formato data se presente;
- route/postazione entro vocabolario ammesso;
- codice classificato come `CERTO`, `INFERITO` o `DA_VERIFICARE`;
- assenza di marker sensibili noti;
- impossibilita di procedere in caso di errore bloccante.

## PREVIEW_ONLY

La prima fase della pipeline deve produrre solo preview.

La preview deve mostrare:

- record normalizzato;
- campi mancanti;
- warning;
- errori bloccanti;
- classificazione fonte;
- stato di confidenza;
- eventuale necessita di conferma umana.

Nessuna preview puo scrivere su SMF, DB, planner state o file dati reali.

## RISK_CLASSIFICATION

Ogni record deve essere classificato almeno in:

- `LOW`: input completo, sanificato, demo/sintetico;
- `MEDIUM`: input incompleto o inferito;
- `HIGH`: route/postazione ambigua, codice non certo, conflitto operativo;
- `BLOCKED`: dati sensibili, allegati reali, scrittura richiesta o validazione
  fallita.

I record `HIGH` richiedono conferma umana. I record `BLOCKED` non possono
avanzare.

## HUMAN_CONFIRMATION_REQUIRED

Ogni passaggio da preview ad applicazione futura richiede conferma umana
esplicita.

La conferma deve essere separata dalla preview e deve includere:

- chi conferma;
- cosa viene applicato;
- motivo;
- rischio;
- differenza tra prima e dopo;
- rollback id previsto.

## NO_DIRECT_WRITE

Questa capability vieta scritture dirette verso:

- SMF;
- database operativo;
- planner state;
- file runtime;
- metadata articolo reale;
- dati cliente o produzione.

Qualunque runtime futuro deve passare da preview, risk classification,
conferma umana e audit minimo.

## SANITIZATION

Output e log devono essere sanificati.

Non devono contenere:

- nomi cliente reali;
- nomi operatori;
- path locali sensibili;
- immagini o riferimenti a documenti reali;
- token/segreti;
- contenuti tecnici non autorizzati;
- dati riconducibili a produzione reale.

## AUDIT_LOG_MINIMO

Il contratto minimo di audit richiede:

- timestamp;
- fonte;
- tipo operazione;
- esito validazione;
- classificazione rischio;
- conferma richiesta;
- stato `preview_only`;
- nessun payload sensibile completo;
- riferimento rollback solo quando esiste apply futuro.

In questa versione il gate non crea audit runtime: ne definisce il contratto.

## FAILURE_MODES

Il check deve fallire se:

- questo documento manca;
- un marker obbligatorio manca;
- il target Makefile manca;
- il documento dichiara import reale completato;
- il documento autorizza scritture dirette;
- il documento richiede dati reali, OCR reale, AI runtime o cloud.

## TEST_DI_CAPABILITY

Comandi minimi:

```bash
bash scripts/controlled_import_pipeline_v1_check.sh
make controlled-import-pipeline-v1
```

Il check e non distruttivo e non accede a dati reali.

## PROSSIMO_PASSO_RUNTIME

Il prossimo passo runtime, da autorizzare separatamente, sara un endpoint/helper
di preview su payload sintetico che:

1. valida input minimo;
2. produce preview sanificata;
3. classifica rischio;
4. dichiara `preview_only`;
5. non scrive su SMF, DB o planner.
