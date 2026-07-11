# ARTICLE_SPECIFICATION_INTAKE_BINDING_CONTRACT_001

Lifecycle: `ACTIVE`

Fonte semantica: `docs/PROMETEO_MASTER.md`.

## Scopo

Collegare il risultato governato dell’acquisizione immagine di una specifica
articolo alla facade di intake strutturato già esistente.

## Flusso

`ArticleSpecificationImageAcquisitionResult`
→ payload parser ordinati
→ `process_structured_intake_payload`
→ classificazione e placement governato

## Vincoli

- accetta soltanto acquisition `EXTRACTED` con parser valido;
- conserva ordine e `source_id` dei payload;
- accetta soltanto `semantic_status = DA_VERIFICARE`;
- ogni payload passa una sola volta dalla facade;
- non esegue OCR, parsing, I/O o persistenza direttamente;
- non introduce nuovi writer o destinazioni autorevoli;
- `requires_review` resta vero;
- `persisted` resta falso;
- qualsiasi `writer_called=true` è una violazione fail-closed.

## Prova

`backend/tests/test_article_specification_intake_binding.py`

Il contratto chiude il binding service-to-service. Non espone upload API, UI,
Pattern Learning o promozione automatica a `CERTO`.

