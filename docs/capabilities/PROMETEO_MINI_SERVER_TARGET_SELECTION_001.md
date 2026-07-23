# PROMETEO_MINI_SERVER_TARGET_SELECTION_001

## Stato

- `STATUS`: `OPEN_READ_ONLY_SELECTION`
- `MODE`: `READ_ONLY_RESEARCH_AND_DECISION`
- `BASELINE`: `main` at `3986cf9`
- `PURCHASE_AUTHORIZED`: `false`
- `INSTALLATION_AUTHORIZED`: `false`
- `INFRASTRUCTURE_CHANGES_AUTHORIZED`: `false`
- `RUNTIME_CHANGES_AUTHORIZED`: `false`

## Scopo

Definire e verificare il profilo hardware del primo mini-server dedicato a Prometeo, confrontare un numero ristretto di target reali compatibili e produrre una decisione motivata prima di qualsiasi acquisto o installazione.

Questa capability non autorizza l'acquisto del dispositivo, l'installazione di Prometeo, modifiche alla rete, configurazioni SSH, Tailscale, firewall, servizi automatici o runtime.

## Contesto

La capability `PROMETEO_END_TO_END_MINI_SERVER_READINESS_PREFLIGHT_001` ha identificato il contratto di esecuzione sul mini-server come primo anello non ancora provato.

La verifica sul target non può essere eseguita perché il mini-server non è stato ancora acquistato.

Lo stato corrente è:

```text
MINI_SERVER_TARGET = NOT_ACQUIRED
MINI_SERVER_READINESS = BLOCKED_BY_TARGET_ABSENCE
```

Prima di aprire una capability installativa è necessario selezionare un target adatto con criteri espliciti, verificabili e proporzionati al carico reale di Prometeo.

## Fonte di verità

Ordine di autorità:

1. requisiti osservati nel repository Prometeo;
2. dipendenze backend e frontend versionate;
3. requisiti ufficiali dei componenti utilizzati;
4. specifiche ufficiali dei produttori hardware;
5. test o benchmark riproducibili;
6. recensioni commerciali solo come fonti secondarie;
7. memoria o preferenze non verificate solo come ipotesi.

Nessun requisito hardware deve essere assunto senza collegarlo a una necessità concreta del runtime Prometeo.

## Carico iniziale previsto

Il primo mini-server deve sostenere almeno:

```text
repository Prometeo
→ backend Python / FastAPI / Uvicorn
→ frontend build e servizio web
→ OCR Tesseract locale
→ persistenza locale governata
→ registry e read-back
→ TL Chat
→ smoke sintetico end-to-end
```

Non rientrano nel dimensionamento iniziale:

- training o fine-tuning locale;
- modelli linguistici di grandi dimensioni eseguiti localmente;
- cluster o alta disponibilità;
- Kubernetes;
- elaborazione massiva di immagini;
- database distribuiti;
- carichi industriali non ancora misurati.

## Requisiti funzionali obbligatori

Il target deve consentire:

1. sistema operativo server mantenuto;
2. esecuzione stabile di Python;
3. esecuzione di Node e npm;
4. installazione ed esecuzione di Tesseract OCR;
5. storage persistente locale;
6. accesso amministrativo controllato;
7. funzionamento continuativo;
8. backup dei dati persistenti;
9. diagnostica di CPU, RAM, disco e processi;
10. ripristino documentabile;
11. rete Ethernet;
12. funzionamento senza monitor;
13. riavvio dopo interruzione elettrica configurabile;
14. esecuzione del futuro smoke end-to-end Prometeo.

## Requisiti hardware iniziali da verificare

| Area | Minimo candidato | Raccomandato iniziale | Motivazione |
|---|---:|---:|---|
| CPU | 4 core moderni | 6-8 core moderni | backend, OCR, build e servizi concorrenti |
| RAM | 8 GB | 16 GB | margine per sistema, backend, frontend e persistenza |
| Storage | 256 GB SSD | 512 GB NVMe SSD | repository, dipendenze, persistenza e backup temporanei |
| Rete | 1 GbE | 1 GbE o superiore | accesso stabile dalla rete locale |
| Architettura | `x86_64` o `arm64` | da decidere | compatibilità e manutenzione |
| Raffreddamento | adeguato | attivo e controllato | stabilità continuativa |
| Alimentazione | affidabile | UPS valutabile | integrità della persistenza |
| Espandibilità RAM | preferibile | preferibile | crescita controllata |
| Storage sostituibile | preferibile | richiesto nella short-list | manutenzione e ripristino |

I valori sono ipotesi iniziali da verificare e non costituiscono autorizzazione all'acquisto.

## Requisiti software da verificare

Per ogni candidato devono essere verificati:

- sistema operativo disponibile;
- ciclo di supporto;
- supporto Python;
- supporto Node e npm;
- disponibilità di Tesseract;
- compatibilità delle dipendenze native;
- gestione dei servizi;
- filesystem e permessi;
- strumenti di backup;
- accesso SSH;
- compatibilità Tailscale, senza configurazione;
- aggiornamenti di sicurezza;
- procedure di recovery.

## Architetture candidate

### `x86_64`

Da valutare per:

- ampia compatibilità software;
- disponibilità di mini-PC;
- manutenzione ordinaria;
- espansione RAM e storage.

### `arm64`

Da valutare per:

- consumi ridotti;
- dimensioni contenute;
- compatibilità con Python, Node e Tesseract;
- eventuali limiti delle dipendenze native;
- disponibilità e sostituibilità dello storage.

La scelta non deve essere basata esclusivamente su prestazioni teoriche o consumo energetico.

## Matrice obbligatoria di confronto

La short-list finale deve contenere da due a tre dispositivi e compilare:

| Campo | Obbligatorio |
|---|---|
| `candidate_id` | sì |
| `manufacturer` | sì |
| `model` | sì |
| `cpu` | sì |
| `architecture` | sì |
| `ram_installed` | sì |
| `ram_maximum` | sì |
| `storage_included` | sì |
| `storage_replaceable` | sì |
| `ethernet` | sì |
| `operating_system_plan` | sì |
| `python_compatibility` | sì |
| `node_compatibility` | sì |
| `tesseract_compatibility` | sì |
| `idle_power` | sì, se verificabile |
| `load_power` | sì, se verificabile |
| `noise_profile` | sì |
| `warranty` | sì |
| `price_observed` | sì |
| `source_date` | sì |
| `risks` | sì |
| `decision` | sì |

Prezzi e disponibilità devono essere osservati al momento della ricerca e non memorizzati come valori permanenti.

## Criteri di selezione

Ogni candidato deve essere valutato per:

1. compatibilità software;
2. affidabilità continuativa;
3. storage sostituibile;
4. RAM disponibile ed espandibile;
5. consumo energetico;
6. rumorosità;
7. supporto e garanzia;
8. costo totale;
9. disponibilità;
10. semplicità di ripristino;
11. rischio di dipendenza da componenti proprietari;
12. margine operativo per la prima installazione Prometeo.

## Slice verticale minima

```text
requisiti osservati nel repository
→ profilo hardware minimo e raccomandato
→ ricerca di massimo tre candidati
→ matrice comparativa verificabile
→ esclusione dei candidati incompatibili
→ una sola raccomandazione
→ decisione di acquisto separata
```

## Criterio di accettazione

La capability può essere chiusa quando:

1. il carico iniziale Prometeo è delimitato;
2. i requisiti minimi sono collegati a esigenze osservabili;
3. sono confrontati da due a tre target reali;
4. ogni dato commerciale ha fonte e data;
5. compatibilità Python, Node e Tesseract è verificata;
6. rischi e limiti sono espliciti;
7. esiste una sola raccomandazione motivata;
8. nessun acquisto è stato effettuato automaticamente;
9. nessuna infrastruttura o configurazione è stata modificata;
10. Privacy Guard e Data Leak Guard risultano verdi.

## Stop conditions

Fermarsi se:

- la ricerca richiede credenziali o account privati;
- le specifiche ufficiali non sono verificabili;
- il candidato richiede componenti non inclusi nel costo dichiarato;
- la compatibilità software resta ambigua;
- il confronto supera tre dispositivi;
- vengono introdotti requisiti per carichi non autorizzati;
- la decisione richiede modifiche runtime;
- il diff coinvolge file diversi dalla capability e dal catalogo generato.

## Limiti

Questa capability non autorizza:

- acquisto;
- ordine commerciale;
- installazione del sistema operativo;
- installazione di Prometeo;
- configurazione SSH o Tailscale;
- modifica di router, firewall o porte;
- creazione di servizi automatici;
- migrazione dei dati;
- uso di dati aziendali reali;
- chiusura del readiness preflight.

## Impatto architetturale

- Modello `Order -> ProductionEvent -> Station/Phase`: invariato.
- Backend e frontend: invariati.
- OCR e registry: invariati.
- TL Chat: invariata.
- Nessuna nuova dipendenza runtime.
- Nessuna review architetturale richiesta per questa apertura documentale.

## Esito documentale

`MINI_SERVER_TARGET_SELECTION_CONTRACT_READY`

## Prossima mossa

Verificare dal repository i requisiti effettivi di Python, Node, npm, Tesseract, persistenza e build. Solo dopo questa mappatura eseguire una ricerca corrente di massimo tre dispositivi reali.
