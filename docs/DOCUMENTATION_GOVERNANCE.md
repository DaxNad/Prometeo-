# PROMETEO Documentation Governance

Riferimento semantico superiore: `docs/PROMETEO_MASTER.md`.

## Scopo

Questo documento governa ordine, recupero, manutenzione e obsolescenza della
documentazione PROMETEO. Non introduce autorità di dominio: stabilisce come
individuare la fonte corretta senza confondere contratti, stato corrente,
evidenze di chiusura e materiale storico.

## Ordine di recupero

1. `docs/DOCUMENTATION_CATALOG.md` — indice unico e stato lifecycle.
2. `docs/PROMETEO_MASTER.md` — autorità semantica e gerarchia delle fonti.
3. `docs/architecture/PROMETEO_MANIFESTO_v1.md` — confini architetturali.
4. `docs/CURRENT_STATE.md` — stato verificato del repository.
5. Documento capability `ACTIVE` pertinente.
6. Contratto e test della capability.
7. Closure, audit e snapshot solo come evidenza storica.

Il codice e i test su `main` prevalgono sempre sulle dichiarazioni di stato
tecnico contenute nei documenti.

## Lifecycle obbligatorio

| Stato | Significato | Utilizzo |
|---|---|---|
| `CANONICAL` | Autorità o indice stabile | Prima lettura |
| `ACTIVE` | Contratto o guida ancora applicabile | Implementazione e verifica |
| `REFERENCE` | Informazione utile, non stato corrente | Consultazione mirata |
| `SUPERSEDED` | Sostituito da una fonte indicata | Solo storia e confronto |
| `ARCHIVED` | Evidenza conclusa o snapshot datato | Audit storico |

Un documento `SUPERSEDED` o `ARCHIVED` non può essere usato per determinare la
prossima capability o dichiarare lo stato corrente.

## Classificazione funzionale

La documentazione segue il modello Diátaxis adattato al repository:

- `GOVERNANCE`: autorità, policy e vincoli;
- `STATE`: stato corrente e priorità;
- `CONTRACT`: comportamento verificabile di una capability;
- `HOW_TO`: procedure operative ripetibili;
- `REFERENCE`: mappe, schemi, tassonomie e indici;
- `DECISION`: ADR e decisioni architetturali;
- `EVIDENCE`: closure, audit, eval e checkpoint;
- `ARCHIVE`: snapshot e materiale storico non operativo.

## Regole anti-obsolescenza

- Esiste un solo stato corrente: `docs/CURRENT_STATE.md`.
- Board, handoff, audit datati e closure non rappresentano lo stato corrente.
- Ogni documento superato deve indicare `Superseded by`.
- Una capability è chiusa soltanto se codice/test su `main` ne forniscono prova.
- I gate che controllano marker documentali non provano readiness runtime.
- I percorsi usati da codice, test o script non vengono spostati senza migrazione
  atomica di tutti i riferimenti.
- Il catalogo deve essere rigenerato dopo aggiunte, rinomine o cambi lifecycle.

## Manutenzione

Comandi canonici:

```bash
make docs-catalog
make docs-check
```

Il primo rigenera il catalogo deterministico. Il secondo blocca link locali
rotti, documenti non catalogati e marker lifecycle incoerenti.
