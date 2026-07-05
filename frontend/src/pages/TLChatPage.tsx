import { useEffect, useRef, useState } from "react";
import { tlChat, type TLChatResponse } from "../lib/api/prometeo";
import "./TLChatPage.css";

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
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, loading]);

  useEffect(() => {
    const textarea = textareaRef.current;
    if (!textarea) return;

    textarea.style.height = "auto";
    textarea.style.height = `${Math.min(textarea.scrollHeight, 180)}px`;
  }, [question]);

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

      setMessages((current) => [
        ...current,
        {
          id: nextMessageId(),
          role: "assistant",
          content: data.answer,
        },
      ]);
    } catch (err) {
      setMessages((current) => [
        ...current,
        {
          id: nextMessageId(),
          role: "assistant",
          content: normalizeError(err),
        },
      ]);
    } finally {
      setLoading(false);
      requestAnimationFrame(() => textareaRef.current?.focus());
    }
  }

  function resetConversation() {
    if (loading) return;
    setMessages([]);
    setQuestion("");
    requestAnimationFrame(() => textareaRef.current?.focus());
  }

  return (
    <main className="tl-chat">
      <header className="tl-chat__header">
        <div>
          <h1 className="tl-chat__title">TL Chat</h1>
          <p className="tl-chat__subtitle">Supporto operativo governato per il turno</p>
        </div>

        <button
          type="button"
          className="tl-chat__reset"
          onClick={resetConversation}
          disabled={loading || messages.length === 0}
        >
          Nuova chat
        </button>
      </header>

      <section className="tl-chat__scroll" aria-label="Cronologia conversazione TL">
        <div className="tl-chat__conversation">
          {messages.length === 0 && (
            <div className="tl-chat__empty">
              <h2 className="tl-chat__empty-title">Come posso aiutarti nel turno?</h2>
              <p className="tl-chat__empty-copy">
                Chiedi informazioni su articoli, route, componenti, stati o criticità operative.
              </p>
            </div>
          )}

          {messages.map((message) => (
            <article
              key={message.id}
              className={`tl-chat__message tl-chat__message--${message.role}`}
              aria-label={message.role === "user" ? "Messaggio utente" : "Risposta PROMETEO"}
            >
              <div className="tl-chat__bubble">{message.content}</div>
            </article>
          ))}

          {loading && (
            <article className="tl-chat__message tl-chat__message--assistant" aria-live="polite">
              <div className="tl-chat__loading" aria-label="PROMETEO sta rispondendo">
                <span className="tl-chat__dot" />
                <span className="tl-chat__dot" />
                <span className="tl-chat__dot" />
              </div>
            </article>
          )}

          <div ref={bottomRef} />
        </div>
      </section>

      <div className="tl-chat__composer-wrap">
        <form
          className="tl-chat__composer"
          onSubmit={(event) => {
            event.preventDefault();
            submit();
          }}
        >
          <textarea
            ref={textareaRef}
            className="tl-chat__input"
            aria-label="Prompt TL"
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter" && !event.shiftKey) {
                event.preventDefault();
                submit();
              }
            }}
            rows={1}
            disabled={loading}
            placeholder="Chiedi a PROMETEO"
          />

          <button
            type="submit"
            className="tl-chat__send"
            disabled={loading || !question.trim()}
            aria-label="Invia domanda"
          >
            ↑
          </button>

          <div className="tl-chat__hint">Invio per mandare · Shift+Invio per andare a capo</div>
        </form>
      </div>
    </main>
  );
}
