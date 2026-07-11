# PROMETEO_PRODUCT_CORE_CLOSURE_V1

Lifecycle: `SUPERSEDED`

Superseded by: `docs/CURRENT_STATE.md` per lo stato corrente. Questo documento
resta attivo esclusivamente come contratto del gate storico
`product-core-closure-v1`; il suo `NON_PASS` non è una fotografia aggiornata.

## SCOPO

Questo gate verifica se PROMETEO possiede oggi un core prodotto minimo
verificabile, protetto, eseguibile e orientato a completamento
gestionale/SaaS/MES.

Il gate non dichiara PROMETEO prodotto completo. Serve a fissare una baseline
severa: cosa e gia chiuso, cosa manca, cosa blocca la vendibilita e quali
capability sono obbligatorie per arrivare a prodotto completo.

## STATO_ATTUALE

PROMETEO e in stato di sistema interno assistivo avanzato.

Sono presenti backend, frontend/PWA di base, TL Chat, planner assistivo,
guardrail privacy/data leak, eval TL, AI boundary, runtime locale documentato e
roadmap prodotto. La chiusura `PROMETEO_GOAL_COMPLETE_V1` non equivale pero a
prodotto completo o vendibile come SaaS/MES.

Valutazione corrente: `PRODUCT_CORE_CLOSURE_V1 = NON_PASS`.

## CORE_GIA_CHIUSO

- Backend FastAPI con health/runtime base.
- TL Chat con contract test e practical query set.
- TL semantic eval locale.
- Data Leak Guard e Privacy Guard.
- AI external boundary con sanitizer/policy gate.
- Documentazione runtime locale.
- Roadmap prodotto `PROMETEO_PRODUCT_COMPLETE_ROADMAP_V1`.
- Separazione dichiarata tra dati sensibili reali e materiali demo/sintetici.

## CORE_NON_CHIUSO

- Flusso ingest dati reale non ancora chiuso come preview/diff/conferma/apply/audit.
- Dominio articoli/processi non ancora abbastanza denso e misurabile.
- Planner operativo non ancora verificato end-to-end su scenario turno completo.
- Eventi/blocchi non ancora chiusi come timeline persistente completa.
- Audit/log override umano non ancora completo con rollback id operativo.
- PWA TL non ancora validata come interfaccia mobile reparto completa.
- Utenti/ruoli non ancora chiusi oltre API key.
- Deploy staging/prod non ancora governato con smoke, backup, rollback e checklist.
- Dataset demo/onboarding cliente sanificato non ancora completo.

## GAP_VENDIBILITA

PROMETEO non va trattato come prodotto commerciale completo finche mancano:

- demo end-to-end con dati sanificati;
- onboarding cliente ripetibile;
- documentazione operativa minima per installazione e uso;
- audit modifiche operative;
- protezione dati verificabile in ambiente cliente;
- PWA usabile da responsabile operativo senza supporto tecnico continuo;
- test minimi ripetibili su flusso ingest, planner, TL Chat, eventi e audit.

Vendibilita realistica attuale: consulenza/prototipo controllato, non SaaS
standard.

## GAP_SAAS_MES

PROMETEO non e ancora SaaS/MES-ready perche mancano:

- multi-tenant;
- modello utenti/ruoli completo;
- isolamento dati cliente;
- provisioning ambiente cliente;
- backup/export/restore governati;
- osservabilita produzione;
- integrazioni MES/ERP formalizzate;
- contratti API stabili e versionati;
- procedure staging/prod complete.

SaaS/MES readiness resta fase successiva alla chiusura interna del prodotto.

## CAPABILITY_OBBLIGATORIE

Per arrivare a prodotto completo sono obbligatorie:

- dominio/anagrafica articoli affidabile e progressiva;
- pipeline import controllata;
- SMF bridge governato;
- schema DB forte per entita core;
- TL Chat collegata a dominio reale denso;
- planner operativo end-to-end;
- eventi/blocchi persistenti;
- audit timeline e override umano;
- PWA mobile reale;
- utenti/ruoli;
- AI local/cloud boundary completa;
- deploy staging/prod;
- demo sintetica end-to-end;
- SaaS/MES readiness solo dopo validazione interna.

## GUARDRAIL_OBBLIGATORI

- Nessun dato reale sensibile in git.
- Nessuna modifica a `specs_finitura`, SMF reale, PDF, immagini, Excel reali,
  `.env`, token o dump DB.
- Nessuna AI esterna senza data boundary, sanitizer, policy gate e audit.
- Nessuna decisione produttiva autonoma: planner e TL Chat restano assistivi.
- Nessun apply operativo senza preview/diff/conferma/audit.
- Nessuna nuova architettura parallela.

## TEST_DI_CHIUSURA

Comandi minimi per questo gate:

```bash
bash scripts/product_core_closure_v1_check.sh
make product-core-closure-v1
```

Il check e documentale/di guardia: fallisce se questo documento o i marker
minimi mancano. Non modifica runtime, dati, backend, frontend, planner o SMF.

## CRITERI_GO_NO_GO

`GO` solo quando:

- il documento esiste;
- tutti i marker minimi sono presenti;
- il target Makefile e ripetibile;
- i guardrail obbligatori sono espliciti;
- lo stato non dichiara PROMETEO prodotto completo.

`NO_GO` se:

- il gate dichiara vendibilita piena senza capability mancanti;
- mancano marker obbligatori;
- il check richiede dati reali;
- il check tocca runtime o dati sensibili;
- la roadmap SaaS/MES viene trattata come completata.

## PROSSIMO_MICRO_PASSO

Chiudere una capability tecnica alla volta, partendo da:

1. pipeline import controllata;
2. schema DB core piu forte;
3. eventi/blocchi persistenti;
4. audit timeline e override;
5. planner end-to-end su dataset sintetico.
