from __future__ import annotations

import re


THINKING_MARKERS = [
    "...done thinking.",
    "done thinking.",
]


def sanitize_ai_output(text: str) -> str:
    """
    Remove local-model reasoning scaffolding before exposing output to PROMETEO UI.

    Purpose:
    - Gemma-like models may emit "Thinking..." / "Thinking Process:" blocks.
    - TL Chat must receive only the final operational answer.
    - This function is deterministic and does not rewrite the final answer content.
    """
    if not isinstance(text, str):
        return ""

    cleaned = text.strip()
    if not cleaned:
        return ""

    lowered = cleaned.lower()

    # Preferred path: keep only text after explicit done-thinking marker.
    for marker in THINKING_MARKERS:
        idx = lowered.rfind(marker)
        if idx != -1:
            cleaned = cleaned[idx + len(marker):].strip()
            lowered = cleaned.lower()
            break

    # Fallback: remove leading Thinking/Thinking Process block when no done marker exists.
    if lowered.startswith("thinking"):
        lines = cleaned.splitlines()
        cut_index = 0

        for i, line in enumerate(lines):
            line_clean = line.strip()
            line_lower = line_clean.lower()

            if not line_clean:
                continue

            # Heuristic: final answer in PROMETEO usually starts after a non-English
            # reasoning scaffold and does not start with internal process labels.
            if (
                i > 0
                and not line_lower.startswith(("thinking", "thinking process", "analyze", "analysis", "draft", "final output", "generate final"))
                and not re.match(r"^\d+\.\s", line_clean)
                and not line_clean.startswith(("*", "-", "•"))
            ):
                cut_index = i
                break

        if cut_index:
            cleaned = "\n".join(lines[cut_index:]).strip()

    # Remove accidental leftover labels at the beginning.
    cleaned = re.sub(r"^(thinking\s*\.\.\.|thinking process\s*:?)\s*", "", cleaned, flags=re.IGNORECASE).strip()
    cleaned = re.sub(r"^\.\.\.done thinking\.\s*", "", cleaned, flags=re.IGNORECASE).strip()

    return cleaned or "Nessuna risposta dal modello."
