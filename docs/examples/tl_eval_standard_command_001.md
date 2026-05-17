# TL eval standard command 001

Obiettivo: stabilizzare il comando locale per eseguire la pipeline eval TL sanificata.

Comandi supportati:

- ./scripts/run_tl_eval.sh
- make tl-eval

Il comando:
- esegue python3 evals/run_tl_semantic_eval.py
- stampa report PASS/FAIL
- restituisce exit code 0/1
- non avvia runtime applicativo
- non usa frontend
- non usa AI esterna
- non usa file reali
- non usa specifiche
- non usa immagini
- non usa codici reali

Stato: TL_EVAL_STANDARD_COMMAND_READY
