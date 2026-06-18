import { useEffect, useRef, useState } from "react";
import { tlChat, type TLChatResponse } from "../lib/api/prometeo";

type ChatMessage = {
  id: number;
  role: "user" | "assistant";
  content: string;
};

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
    return "PROMETEO non è raggiungibile. Verificare il runtime locale e riprovare.";
  }

  return "Errore durante l'interrogazione TL Chat. Riprovare.";
}

function nextMessageId(): number {
  return Date.now() + Math.floor(Math.random() * 1000);
}

export default function TLChatPage() {
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const bottomRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, loading]);

  async function submit() {
    const cleanQuestion = question.trim();

    if (!cleanQuestion || loading) return;

    const userMessage: ChatMessage = {
      id: nextMessageId(),
      role: "user",
      content: cleanQuestion,
    };

    setMessages((current) => [...current, userMessage]);
    setQuestion("");
    setLoading(true);

    try {
      const article = extractArticle(cleanQuestion);

      const data: TLChatResponse = await tlChat({
        question: cleanQuestion,
        context: article ? { article } : {},
      });

      const assistantMessage: ChatMessage = {
        id: nextMessageId(),
        role: "assistant",
        content: data.answer,
      };

      setMessages((current) => [...current, assistantMessage]);
    } catch (err) {
      const assistantMessage: ChatMessage = {
        id: nextMessageId(),
        role: "assistant",
        content: normalizeError(err),
      };

      setMessages((current) => [...current, assistantMessage]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main
      style={{
        minHeight: "calc(100vh - 72px)",
        display: "grid",
        gridTemplateRows: "auto 1fr auto",
        gap: 16,
        maxWidth: 980,
        margin: "0 auto",
        padding: "12px 16px 20px",
      }}
    >
      <header style={{ display: "grid", gap: 4 }}>
        <h1 style={{ margin: 0, fontSize: 22 }}>TL Chat</h1>
        <p style={{ margin: 0, color: "#9ca3af", fontSize: 14 }}>
          Scrivi una richiesta operativa come in un prompt. PROMETEO risponde senza modificare dati.
        </p>
      </header>

      <section
        aria-label="Cronologia conversazione TL"
        style={{
          minHeight: 360,
          display: "grid",
          alignContent: messages.length === 0 ? "center" : "start",
          gap: 14,
          overflowY: "auto",
          padding: "8px 0 24px",
        }}
      >
        {messages.length === 0 && (
          <div
            style={{
              justifySelf: "center",
              maxWidth: 680,
              textAlign: "center",
              color: "#d4d4d8",
              display: "grid",
              gap: 10,
            }}
          >
            <div style={{ fontSize: 28, fontWeight: 800 }}>Come posso aiutarti nel turno?</div>
            <div style={{ color: "#9ca3af" }}>
              Esempio: “Che criticità ha il 12066?” oppure “Spiegami la sequenza per questo articolo.”
            </div>
          </div>
        )}

        {messages.map((message) => (
          <article
            key={message.id}
            style={{
              justifySelf: message.role === "user" ? "end" : "start",
              maxWidth: message.role === "user" ? "72%" : "86%",
              border: "1px solid #27272a",
              background: message.role === "user" ? "#1f2937" : "#0b0b0c",
              color: "#fff",
              borderRadius: 18,
              padding: "12px 14px",
              whiteSpace: "pre-wrap",
              lineHeight: 1.45,
            }}
          >
            {message.content}
          </article>
        ))}

        {loading && (
          <article
            style={{
              justifySelf: "start",
              maxWidth: "86%",
              border: "1px solid #27272a",
              background: "#0b0b0c",
              color: "#9ca3af",
              borderRadius: 18,
              padding: "12px 14px",
              lineHeight: 1.45,
            }}
          >
            PROMETEO sta rispondendo…
          </article>
        )}

        <div ref={bottomRef} />
      </section>

      <form
        onSubmit={(e) => {
          e.preventDefault();
          submit();
        }}
        style={{
          position: "sticky",
          bottom: 0,
          display: "grid",
          gap: 8,
          border: "1px solid #27272a",
          background: "#09090b",
          borderRadius: 22,
          padding: 12,
          boxShadow: "0 -12px 30px rgba(0, 0, 0, 0.22)",
        }}
      >
        <textarea
          aria-label="Prompt TL"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              submit();
            }
          }}
          rows={3}
          style={{
            width: "100%",
            boxSizing: "border-box",
            resize: "vertical",
            border: 0,
            outline: "none",
            background: "transparent",
            color: "#fff",
            padding: "6px 4px",
            fontSize: 16,
            lineHeight: 1.4,
          }}
          placeholder="Scrivi un prompt TL..."
        />

        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 12 }}>
          <span style={{ color: "#71717a", fontSize: 13 }}>Invio per mandare · Shift+Invio per andare a capo</span>

          <button
            type="submit"
            disabled={loading || !question.trim()}
            style={{
              border: "1px solid #444",
              background: loading || !question.trim() ? "#18181b" : "#fff",
              color: loading || !question.trim() ? "#71717a" : "#000",
              borderRadius: 999,
              padding: "9px 15px",
              fontWeight: 800,
              cursor: loading || !question.trim() ? "not-allowed" : "pointer",
            }}
          >
            Invia
          </button>
        </div>
      </form>
    </main>
  );
}
