# PROMETEO_ATLAS_DATA_EXPORT_AND_INVENTORY_001

## Stato

- `STATUS`: `DOCUMENTED`
- `MODE`: `READ_ONLY_INVENTORY_AND_EXPORT_CONTRACT`
- `BASELINE`: `main` at `e7d36d6297bbcf52670dc5052b19da204a407759`
- `RUNTIME_AUTHORIZED`: `false`
- `AUTOMATIC_EXPORT_AUTHORIZED`: `false`
- `SECRETS_TRANSFER_AUTHORIZED`: `false`

## Scopo

Inventariare ed esportare da ChatGPT Atlas esclusivamente i dati operativi e informativi necessari alla continuità di Prometeo, senza includere nel repository segreti, credenziali, sessioni autenticate, dati aziendali sensibili o materiale privato.

Questa capability apre un perimetro documentale e operativo read-only. Non autorizza modifiche al runtime Prometeo, automazioni di login, scraping autenticato, importazioni massive o trasferimento di dati sensibili.

## Contesto

La capability precedente `PROMETEO_DEVELOPMENT_ENVIRONMENT_MIGRATION_FROM_ATLAS_001` ha stabilito che Atlas non è una dipendenza tecnica del runtime Prometeo, ma può contenere dipendenze operative e informative da preservare prima della cessazione del servizio.

Le categorie già individuate comprendono:

- segnalibri;
- cronologia utile;
- pagine GitHub, Vercel e Prometeo usate nel lavoro;
- prompt canonici;
- comandi canonici;
- roadmap;
- capability e closure;
- procedure presenti solo nelle conversazioni;
- riferimenti a percorsi locali;
- screenshot operativi non sensibili;
- note sulla continuità tra browser, ChatGPT, Terminale e localhost.

## Fonte di verità

Ordine di autorità:

1. repository GitHub Prometeo;
2. documentazione versionata;
3. output verificabili da Terminale e test;
4. dati esportati da Atlas dopo classificazione e sanitizzazione;
5. memoria o ricostruzioni manuali solo come ultima fonte, sempre marcate come non verificate.

Atlas non diventa una fonte autorevole per logica di dominio, configurazioni runtime, credenziali o stato operativo corrente.

## Perimetro autorizzato

Sono autorizzate esclusivamente attività read-only e manualmente verificabili:

1. elencare le categorie di dati presenti in Atlas;
2. identificare ciò che serve realmente alla continuità di Prometeo;
3. classificare ogni elemento;
4. esportare solo gli elementi autorizzati;
5. sanitizzare prima di qualsiasi salvataggio nel repository;
6. registrare origine, data, formato, destinazione e stato di verifica;
7. eseguire controlli anti-segreti prima di commit o pull request.

## Classificazione obbligatoria

Ogni elemento deve ricevere una sola classificazione primaria:

| Classificazione | Significato | Destinazione ammessa |
|---|---|---|
| `EXPORTABLE_PUBLIC` | Informazione non sensibile e utile al progetto | Repository, dopo verifica |
| `EXPORTABLE_SANITIZED` | Utile ma contenente riferimenti da rimuovere o anonimizzare | Repository solo dopo sanitizzazione |
| `LOCAL_ONLY` | Utile operativamente ma non adatta al repository pubblico | Archivio locale protetto |
| `REFERENCE_ONLY` | Da registrare come esistenza o procedura, senza copiarne il contenuto | Inventario documentale |
| `FORBIDDEN_SECRET` | Segreto, credenziale o materiale di autenticazione | Nessuna esportazione nel repository |
| `FORBIDDEN_SENSITIVE` | Dato aziendale, personale o industriale non necessario | Nessuna esportazione nel repository |
| `DISCARD` | Dato duplicato, obsoleto o senza valore operativo | Nessuna conservazione richiesta |

## Inventario iniziale

| Categoria | Esempi | Classificazione predefinita | Azione |
|---|---|---|---|
| Segnalibri tecnici | repository, PR, Vercel, documentazione, localhost | `EXPORTABLE_PUBLIC` o `EXPORTABLE_SANITIZED` | esportare URL e titolo, rimuovendo riferimenti privati |
| Cronologia utile | pagine consultate per sviluppo e diagnostica | `REFERENCE_ONLY` | inventariare solo le voci necessarie, non esportare la cronologia completa |
| Prompt canonici | preflight, mapping, test-first, closure | `EXPORTABLE_PUBLIC` o `EXPORTABLE_SANITIZED` | consolidare in documenti versionati |
| Comandi canonici | avvio backend/frontend, test, Git, diagnostica | `EXPORTABLE_SANITIZED` | rimuovere percorsi utente, host, token e valori locali |
| Roadmap e capability | prossime mosse, limiti, criteri di accettazione | `EXPORTABLE_PUBLIC` | riportare nei documenti canonici |
| Procedure in conversazione | flussi operativi non ancora documentati | `EXPORTABLE_SANITIZED` | trasformare in procedura verificabile, non copiare intere chat |
| Screenshot operativi | errori UI, stato localhost, routing | `LOCAL_ONLY` o `REFERENCE_ONLY` | non esportare immagini; conservare localmente oppure registrare soltanto un riepilogo testuale non sensibile o un riferimento descrittivo |
| Percorsi locali | home directory, file system, mount | `REFERENCE_ONLY` | documentare placeholder generici, mai il percorso personale reale |
| Dati di autenticazione | password, cookie, token, API key, sessioni | `FORBIDDEN_SECRET` | non esportare, non trascrivere, non committare |
| Dati aziendali reali | ordini, articoli, documenti, immagini, Excel | `FORBIDDEN_SENSITIVE` o `LOCAL_ONLY` | nessun repository pubblico; usare dati sintetici |
| Conversazioni ChatGPT | decisioni e procedure Prometeo | `REFERENCE_ONLY` | estrarre solo decisioni e contratti, non archiviare indiscriminatamente le chat |

## Matrice di registrazione

Ogni elemento candidato deve essere registrato con questi campi minimi:

| Campo | Obbligatorio | Regola |
|---|---|---|
| `item_id` | sì | identificatore stabile e non sensibile |
| `source_category` | sì | categoria Atlas osservata |
| `source_description` | sì | descrizione sintetica, senza segreti |
| `business_need` | sì | motivo concreto per cui serve a Prometeo |
| `classification` | sì | una classificazione ammessa |
| `sanitization_required` | sì | `true` o `false` |
| `destination` | sì | repository, archivio locale protetto, reference-only o discard |
| `verification_status` | sì | `NOT_REVIEWED`, `REVIEWED`, `SANITIZED`, `EXPORTED`, `REJECTED` |
| `verified_by` | sì | ruolo o identificatore non sensibile |
| `verified_at` | sì | timestamp o data ISO |
| `notes` | no | solo note non sensibili |

## Procedura deterministica di export

1. Selezionare una sola categoria Atlas.
2. Elencare gli elementi candidati senza copiarne ancora il contenuto.
3. Assegnare la classificazione primaria.
4. Scartare immediatamente `FORBIDDEN_SECRET` e `FORBIDDEN_SENSITIVE`.
5. Per `EXPORTABLE_SANITIZED`, creare una copia di lavoro locale e rimuovere:
   - token;
   - password;
   - cookie;
   - chiavi API;
   - chiavi private;
   - sessioni autenticate;
   - email personali;
   - nomi personali non necessari;
   - percorsi locali reali;
   - host interni;
   - identificativi aziendali;
   - dati di produzione reali.
6. Verificare che il contenuto risultante sia minimo, necessario e comprensibile fuori da Atlas.
7. Salvare nel repository solo file testuali autorizzati e coerenti con la struttura documentale Prometeo.
8. Eseguire i guard obbligatori.
9. Fermarsi su qualsiasi violazione o ambiguità.
10. Registrare l'esito nell'inventario.

## Guard obbligatori

Prima di commit, push o merge devono essere eseguiti dal checkout locale:

```bash
cd ~/PROMETEO
./tools/py scripts/privacy_guard_specs.py
./tools/py scripts/data_leak_guard.py
git status --short
git diff --cached --stat
```

La capability non può essere dichiarata chiusa se uno dei due guard fallisce.

## Regole di sicurezza

Non devono mai entrare nel repository:

- password;
- token;
- cookie;
- API key;
- chiavi SSH private;
- sessioni autenticate;
- valori reali di variabili ambiente sensibili;
- URL contenenti credenziali o token;
- database dump;
- log locali;
- file Excel reali;
- screenshot con dati aziendali o personali;
- documenti industriali reali;
- percorsi utente personali;
- email personali;
- nomi personali non necessari.

Non usare `git add -f` per aggirare i guard o il `.gitignore`.

## Formati ammessi nel repository

Per la prima slice sono ammessi solo:

- Markdown;
- JSON sintetico e senza dati sensibili;
- testo semplice;
- YAML esclusivamente per configurazioni non sensibili e solo se necessario.

Sono esclusi nella prima slice:

- immagini;
- PDF;
- archivi compressi;
- database;
- log;
- esportazioni complete di cronologia;
- dump di conversazioni;
- file binari;
- file di autenticazione.

## Slice verticale minima

La prima slice verificabile consiste in:

```text
una categoria Atlas
→ inventario degli elementi candidati
→ classificazione
→ sanitizzazione quando necessaria
→ export di un solo artefatto testuale non sensibile
→ esecuzione dei guard
→ verifica che l'artefatto resti utilizzabile fuori da Atlas
```

La categoria raccomandata per la prima slice è `prompt canonici`, perché può essere verificata senza dati aziendali, credenziali o dipendenze runtime.

## Criteri di accettazione

La capability può essere chiusa solo quando:

1. esiste un inventario verificabile delle categorie Atlas rilevanti;
2. ogni elemento esportato ha classificazione, destinazione e stato di verifica;
3. almeno un artefatto testuale non sensibile è stato esportato e verificato fuori da Atlas;
4. nessun segreto o dato sensibile è stato copiato nel repository;
5. `Privacy Guard` e `Data Leak Guard` risultano verdi;
6. non sono state modificate configurazioni runtime, rete, porte, Tailscale o mini-server;
7. non sono state introdotte nuove dipendenze;
8. non è stata dichiarata equivalenza tra Atlas e strumenti sostitutivi senza smoke;
9. il risultato è comprensibile e utilizzabile senza accesso ad Atlas;
10. la capability precedente di migrazione resta invariata.

## Stop conditions

Fermarsi immediatamente se:

- l'export richiede credenziali, token, cookie o sessioni;
- la fonte contiene dati aziendali reali non separabili;
- la sanitizzazione non può essere verificata;
- il formato è binario o non ispezionabile;
- il file candidato è escluso dal `Data Leak Guard`;
- servono modifiche al runtime Prometeo;
- servono modifiche ai guard di sicurezza;
- il perimetro si espande a cronologia completa, backup completo o scraping autenticato;
- il diff contiene file diversi dall'inventario o dalla documentazione autorizzata.

## Limiti

Questa capability non autorizza:

- modifica o cancellazione di dati Atlas;
- esportazione automatica dell'intero profilo;
- automazione di login;
- accesso o copia di password e cookie;
- acquisizione di dati da account diversi da quello autorizzato;
- modifica del runtime Prometeo;
- importazione automatica in database o registry;
- modifiche a backend, frontend, planner, TL Chat o Pattern Learning;
- modifiche a rete, porte, SSH, Tailscale o mini-server;
- dichiarazione di migrazione completata.

## Impatto architetturale

- Modello `Order -> ProductionEvent -> Station/Phase`: invariato.
- Planner: nessun impatto.
- Registry semantico: nessun impatto.
- Backend dominio: nessun impatto.
- Frontend: nessun impatto.
- Review architetturale: non necessaria per questa modifica documentale; necessaria solo se una futura slice introduce runtime, automazione o nuove fonti dati.

## Esito documentale

`ATLAS_DATA_EXPORT_AND_INVENTORY_CONTRACT_READY`

La capability è documentata ma non chiusa. L'inventario reale e la prima esportazione verificabile devono ancora essere eseguiti.

## Prossima mossa

Eseguire una mappatura read-only dei `prompt canonici` presenti nelle conversazioni Atlas, selezionare un solo prompt non sensibile, trasformarlo in artefatto versionato e verificare i guard locali prima del merge.
