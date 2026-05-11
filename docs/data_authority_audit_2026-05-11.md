# PROMETEO Data Authority Audit (2026-05-11)

## Scope
- Audit tecnico read-only su fonti dati articolo/codice/route/stazione.
- Nessun refactor runtime.
- Regola dominio applicata: fonte autorevole operativa = `SPECIFICA DI FINITURA` + conferma `TL`.

## 1) Moduli/File che leggono articoli/codici (runtime principali)

### Resolver / Domain
- `backend/app/domain/article_profile_resolver.py`
  - legge `specs_finitura/<ARTICOLO>/metadata.json` (authoritative first)
  - fallback su `article_process_matrix` derivato
- `backend/app/domain/article_process_matrix.py`
  - legge `.../local_smf/finiture/article_route_matrix.json`
  - cache in-memory `_CACHE_DATA`
- `backend/app/domain/article_tl_summary.py`
  - legge profili via `article_process_matrix.get_article_profile` (non via resolver)
- `backend/app/domain/article_pilot_profile.py`
  - costruisce profilo da `BOM_Specs/BOM_Operations/BOM_Controls`

### Services
- `backend/app/services/sequence_planner.py`
  - usa `resolve_article_profile(article_code)` (ordine corretto: authoritative -> derived)
  - scrive cache runtime: `backend/app/data/global_sequence.json`, `turn_plan.json`
- `backend/app/services/component_usage_service.py`
  - usa viste/derivati BOM/board per impatti componenti condivisi

### API
- `backend/app/api/tl_chat.py`
  - legge:
    - `specs_finitura/*/metadata.json`
    - `data/local_smf/article_lifecycle_registry.json`
    - `data/local_smf/codici_staging_preview.json`
    - `data/local_smf/finiture/article_route_matrix.preview.json`
  - ordine corrente risposta articolo:
    1. `build_article_tl_summary` (derivato da `article_process_matrix`)
    2. metadata locale specs
    3. lifecycle
    4. preview matrix
- `backend/app/api/real_ingest.py`
  - usa BOM_Specs read-only per validazione/inferenza codice
- `backend/app/api/production_events.py`, `backend/app/api/events.py`
  - stream eventi produzione/operativi (non fonte route autorevole)

### Data folders con contenuti articolo/codice
- `specs_finitura/**` (+ `specs_finitura/index.json`)
- `data/local_smf/*.csv`, `data/local_smf/*.json`, `data/local_smf/finiture/*.json`
- `data/export/*.json`
- `backend/app/data/*.json`

## 2) Classificazione fonti dati

## AUTHORITATIVE
- `specs_finitura/<articolo>/metadata.json` con schema `PROMETEO_REAL_DATA_PILOT_V1` e conferma route TL.
- Campi chiave: `route_status`, `route_source`, `route_steps`, `constraints`, `confidence`.

## DERIVED
- `data/local_smf/BOM_Specs.csv`
- `data/local_smf/BOM_Operations.csv`
- `data/local_smf/BOM_Components.csv`
- `data/local_smf/BOM_Controls.csv`
- `data/local_smf/BOM_Variants.csv`
- `data/local_smf/finiture/article_route_matrix.json`
- `backend/app/domain/article_process_matrix.py` (loader di matrice derivata)
- `backend/app/domain/article_pilot_profile.py`

## CACHE
- `backend/app/data/global_sequence.json`
- `backend/app/data/turn_plan.json`
- `backend/app/data/events*.json`
- `data/export/global_sequence.json`
- `data/export/turn_plan.json`

## PREVIEW
- `data/local_smf/finiture/article_route_matrix.preview.json`
- `data/local_smf/codici_staging_preview.json`
- `data/local_smf/article_lifecycle_registry.json` (supporto TL/reparto, non route-authority)
- flussi API preview: `backend/app/api/real_ingest.py`

## DIRTY_LEGACY / RISCHIO
- Qualunque `article_route_matrix.json` derivata non riconciliata con metadata specs TL.
- Lifecycle/staging preview usati come fallback operativi senza resolver autorevole.
- Cache runtime esportate riusate come fonte decisionale invece che come output.

## 3) Punti runtime dove fonti derivate possono superare autorevoli

1. `backend/app/api/tl_chat.py`
- `_build_contract_response` usa prima `_response_from_article_summary(article)` e solo dopo metadata specs.
- `build_article_tl_summary` pesca da `article_process_matrix` (derivato), quindi un derivato può prevalere su specs/TL in risposta chat.

2. `backend/app/domain/article_tl_summary.py`
- dipende da `get_article_profile` (`article_process_matrix`) e non da `resolve_article_profile`.
- questo bypassa gerarchia authoritative-first già implementata in `article_profile_resolver.py`.

3. `backend/app/domain/article_process_matrix.py`
- path matrice derivata esterno (`SMF_BASE_PATH/.../article_route_matrix.json`) e cache persistente in memoria.
- rischio di stale matrix che continua ad alimentare route/segnali.

4. `backend/app/api/real_ingest.py`
- validazione codice può risultare `INFERITO_DA_BOM` basata su BOM_Specs.
- corretto come preview/supporto, ma non deve essere promossa a route authority.

## 4) Rischi concreti (esempio articolo 12063)

- Se `specs_finitura/12063/metadata.json` (route TL confermata) diverge da `article_route_matrix.json`:
  - planner è protetto (usa resolver autorevole).
  - TL chat può mostrare sintesi da derivato prima del metadata locale.
- Effetto pratico: operatore vede risposta incoerente (es. stazione ZAW o sequenza CP) rispetto alla specifica/TL.
- Rischio secondario: confusione su classificazione (`CERTO` vs `INFERITO`/`DA_VERIFICARE`) quando la preview/derivata contiene mismatch.

## 5) Proposta spina dorsale dati (target architetturale)

1. **Authoritative Resolver unico**
- mantenere `resolve_article_profile(article)` come ingresso unico per route/segnali/certezza articolo.
- resolver già implementa:
  - first: `specs_finitura/*/metadata.json`
  - fallback: `article_process_matrix` derivata.

2. **Subordinazione esplicita derived/cache/preview**
- derived (`BOM_*`, matrix) solo fallback, mai override.
- cache/export solo output diagnostico, non input autoritativo.
- preview (`*.preview.json`, lifecycle staging) solo supporto TL, non planner authority.

3. **Consumo runtime**
- planner: già quasi allineato (usa resolver).
- TL chat: should call resolver-backed summary first (non direttamente matrix).
- API preview: etichettare sempre come non-authoritative.

## 6) Patch minima consigliata (non applicata in questo audit)

Opzione A (più piccola, ad alto impatto positivo):
- aggiornare `article_tl_summary` per leggere via `resolve_article_profile` invece di `article_process_matrix.get_article_profile`.
- risultato: TL chat eredita gerarchia autorevole senza refactor ampio.

Opzione B (guard/test leggero):
- aggiungere test boundary che fallisce se flusso TL article summary usa direttamente `article_process_matrix` bypassando resolver.

In questo task non è stata applicata patch runtime; solo audit documentale.

## 7) Decisione operativa

- Stato attuale: gerarchia autorevole esiste ma non è uniformemente applicata.
- Blocco principale: TL chat summary path può privilegiare derivato prima di metadata specs/TL.
- Priorità: introdurre guard su path TL summary -> resolver, mantenendo preview come fallback subordinato.
