# TL semantic eval CLI 001

Obiettivo: aggiungere un comando CLI locale eval-only per la matrice TL semantica sanificata.

Comando:

python3 evals/run_tl_semantic_eval.py

Il comando:
- legge evals/fixtures/tl_semantic_eval_matrix_001.json
- valuta i casi con il runner deterministico
- stampa report PASS/FAIL
- restituisce exit code 0 se tutti i casi passano
- restituisce exit code 1 se almeno un caso fallisce

Perimetro:
- nessun runtime applicativo
- nessun frontend
- nessuna AI esterna
- nessun SMF reale
- nessuna specifica
- nessuna immagine
- nessun codice reale

Stato: TL_SEMANTIC_EVAL_CLI_READY
