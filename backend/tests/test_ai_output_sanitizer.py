from app.ai_adapters.output_sanitizer import sanitize_ai_output


def test_sanitize_ai_output_removes_done_thinking_block():
    raw = """Thinking...
Thinking Process:
1. Analyze request.
2. Draft answer.
...done thinking.

Risposta finale operativa.
Non pianificare automaticamente."""

    assert sanitize_ai_output(raw) == (
        "Risposta finale operativa.\n"
        "Non pianificare automaticamente."
    )


def test_sanitize_ai_output_keeps_clean_response():
    raw = "Strategia operativa reale: verificare ZAW-1 prima di CP finale."

    assert sanitize_ai_output(raw) == raw


def test_sanitize_ai_output_handles_empty_text():
    assert sanitize_ai_output("   ") == ""


def test_sanitize_ai_output_removes_gemma_style_reasoning_prefix():
    raw = """Thinking...
Thinking Process:

1. Analyze the Request:
* Context PROMETEO.

Un articolo REFERENCE_ONLY va conosciuto come riferimento.
Non entra nel planner standard."""

    assert sanitize_ai_output(raw) == (
        "Un articolo REFERENCE_ONLY va conosciuto come riferimento.\n"
        "Non entra nel planner standard."
    )
