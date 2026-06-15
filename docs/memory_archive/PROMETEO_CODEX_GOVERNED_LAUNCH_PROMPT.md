# PROMETEO — Codex governed launch prompt

## Scopo

Questa nota archivia il prompt operativo usato per avviare Codex in modalità governata su PROMETEO.

Il prompt serve a impedire modifiche impulsive, push diretti su main, accesso a dati sensibili e deviazioni architetturali.

## Regole Codex da conservare

- Non modificare file subito.
- Prima leggere la governance PROMETEO.
- Una sola capability alla volta.
- Nessun push diretto su main.
- Branch dedicato, commit mirato e PR.
- Nessuna nuova architettura non richiesta.
- Nessun agente libero.
- Nessun workaround temporaneo non dichiarato.
- Nessuna regex o patch cieca che rimuova logica runtime critica.

## File vietati o protetti

- .env
- specs_finitura/**
- immagini PNG, JPEG, PDF reali
- SMF reale
- dati sensibili o produttivi reali
- backend o frontend non collegati allo scope dichiarato

## Output richiesto a Codex

Codex deve sempre dichiarare:

- cosa ha letto;
- rischio rilevato;
- patch sì/no;
- test eseguiti;
- verdict finale PASS, FAIL o DA_VERIFICARE.

## Sicurezza tool

Usare solo Codex ufficiale/OpenAI o CLI già installata e verificata.

Evitare pacchetti non affidabili tipo Codex UI o strumenti simili trovati online, perché possono imitare tool legittimi e rubare credenziali.

## Nota operativa

Il prompt originale era legato a OCR_PARSER_001. Questa versione archiviata conserva solo le regole permanenti utili per futuri avvii Codex governati.
