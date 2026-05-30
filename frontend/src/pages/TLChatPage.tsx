import { useState } from "react";
import { tlChat, type TLChatResponse } from "../lib/api/prometeo";

function extractArticle(question: string): string | undefined {
  const match = question.match(/\b\d{5}\b/);
  return match?.[0];
}

function normalizeError(err: unknown): string {
  const message = err instanceof Error ? err.message : "";

  if (
    message.includes("Failed to fetch") ||
    message.includes("NetworkError") ||
    message.includes("POST /tl/chat failed")
  ) {
    return "PROMETEO non è raggiungibile. Riprovare o verificare il runtime locale.";
  }

  return "Errore durante l'interrogazione TL Chat. Riprovare.";
}

export default function TLChatPage() {
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<TLChatResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function submit(nextQuestion = question) {
    const cleanQuestion = nextQuestion.trim();

    if (!cleanQuestion) {
      setResponse(null);
      setError("Inserisci una domanda TL prima di interrogare PROMETEO.");
      return;
    }

    setQuestion(cleanQuestion);
    setLoading(true);
    setError(null);

    try {
      const article = extractArticle(cleanQuestion);

      const data = await tlChat({
        question: cleanQuestion,
        context: article ? { article } : {},
      });

      setResponse(data);
    } catch (err) {
      setResponse(null);
      setError(normalizeError(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <main style={{ maxWidth: 900, margin: "0 auto", padding: 16, display: "grid", gap: 16 }}>
      <header style={{ display: "grid", gap: 4 }}>
        <h1 style={{ margin: 0 }}>PROMETEO TL Chat</h1>
        <p style={{ margin: 0, color: "#9ca3af" }}>
          Interfaccia operativa interrogabile. Nessun dettaglio tecnico, nessun radar, nessuna scrittura.
        </p>
      </header>

      <section style={{ display: "grid", gap: 8 }}>
        <label htmlFor="tl-question" style={{ fontWeight: 700 }}>
          Domanda TL
        </label>

        <textarea
          id="tl-question"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={(e) => {
            if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
              e.preventDefault();
              submit();
            }
          }}
          rows={4}
          style={{
            width: "100%",
            boxSizing: "border-box",
            borderRadius: 10,
            border: "1px solid #333",
            background: "#080808",
            color: "#fff",
            padding: 12,
            fontSize: 16,
          }}
          placeholder=""
        />

        <button
          onClick={() => submit()}
          disabled={loading}
          style={{
            width: "fit-content",
            border: "1px solid #444",
            background: loading ? "#222" : "#fff",
            color: loading ? "#aaa" : "#000",
            borderRadius: 10,
            padding: "10px 16px",
            fontWeight: 700,
            cursor: loading ? "not-allowed" : "pointer",
          }}
        >
          {loading ? "Interrogo PROMETEO…" : "Chiedi a PROMETEO"}
        </button>
      </section>
      {loading && (
        <section style={{ border: "1px solid #27272a", background: "#111", borderRadius: 12, padding: 12 }}>
          PROMETEO sta analizzando la richiesta…
        </section>
      )}

      {error && (
        <section style={{ border: "1px solid #7f1d1d", background: "#1f0a0a", borderRadius: 12, padding: 12 }}>
          <strong>Errore</strong>
          <div style={{ color: "#fca5a5", marginTop: 6 }}>{error}</div>
        </section>
      )}

      {response && (
        <section style={{ border: "1px solid #27272a", background: "#0b0b0c", borderRadius: 14, padding: 16 }}>
          <div style={{ fontSize: 20, lineHeight: 1.35, whiteSpace: "pre-wrap" }}>
            {response.answer}
          </div>
        </section>
      )}
    </main>
  );
}
