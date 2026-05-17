# TL semantic eval runner 001

Obiettivo: collegare la matrice TL semantica a un runner deterministico locale.

Il runner:
- valuta una risposta candidata
- confronta la risposta con i significati richiesti
- restituisce PASS/FAIL deterministico
- non usa runtime applicativo
- non usa frontend
- non usa AI esterna
- non usa SMF reale
- non usa specifiche
- non usa immagini
- non usa codici reali

Fonte fixture:
- evals/fixtures/tl_semantic_eval_matrix_001.json

Stato: TL_SEMANTIC_EVAL_RUNNER_READY
