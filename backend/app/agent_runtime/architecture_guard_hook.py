"""
ARCHITECTURE GUARD HOOK v0

Hook non invasivo per attivare il controllo architetturale.
Non modifica comportamento runtime.
Produce solo segnale semantico nei log.
"""

from typing import Dict
from .architecture_guard import evaluate_architecture_guard, summarize_guard_result


def run_architecture_guard(change_context: Dict) -> Dict:

    result = evaluate_architecture_guard(change_context)

    summary = summarize_guard_result(result)

    # log leggero
    print(
        "[ARCHITECTURE_GUARD]",
        summary
    )

    return summary

