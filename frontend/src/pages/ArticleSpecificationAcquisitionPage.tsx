import { useState, type FormEvent } from "react";
import {
  acquireArticleSpecification,
  type ArticleSpecificationAcquisitionResponse,
} from "../lib/api/prometeo";

async function fileToBase64(file: File): Promise<string> {
  const buffer = await file.arrayBuffer();
  const bytes = new Uint8Array(buffer);
  const chunkSize = 0x8000;
  let binary = "";

  for (let offset = 0; offset < bytes.length; offset += chunkSize) {
    const chunk = bytes.subarray(offset, offset + chunkSize);
    binary += String.fromCharCode(...chunk);
  }

  return window.btoa(binary);
}

function normalizeError(error: unknown): string {
  const message = error instanceof Error ? error.message : "";

  if (
    message.includes("Failed to fetch") ||
    message.includes("NetworkError") ||
    message.includes("POST /article-specification/acquire failed")
  ) {
    return "PROMETEO non è raggiungibile oppure ha rifiutato la richiesta.";
  }

  return "Acquisizione non completata. Verificare il file e riprovare.";
}

function booleanLabel(value: boolean): string {
  return value ? "true" : "false";
}

export default function ArticleSpecificationAcquisitionPage() {
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] =
    useState<ArticleSpecificationAcquisitionResponse | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!file || loading) return;

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const imageBase64 = await fileToBase64(file);
      const response = await acquireArticleSpecification({
        image_base64: imageBase64,
      });
      setResult(response);
    } catch (caughtError) {
      setError(normalizeError(caughtError));
    } finally {
      setLoading(false);
    }
  }

  return (
    <main
      style={{
        maxWidth: 980,
        margin: "0 auto",
        padding: "20px 16px 40px",
        display: "grid",
        gap: 16,
      }}
    >
      <header style={{ display: "grid", gap: 6 }}>
        <h1 style={{ margin: 0, fontSize: 24 }}>
          Acquisizione specifica articolo
        </h1>
        <p style={{ margin: 0, color: "#a1a1aa", lineHeight: 1.5 }}>
          Estrazione locale destinata esclusivamente alla revisione umana.
          Nessun dato viene salvato o promosso automaticamente.
        </p>
      </header>

      <section
        style={{
          border: "1px solid #27272a",
          background: "#0b0b0c",
          borderRadius: 12,
          padding: 16,
        }}
      >
        <form onSubmit={submit} style={{ display: "grid", gap: 14 }}>
          <label style={{ display: "grid", gap: 8 }}>
            <span style={{ fontWeight: 700 }}>Immagine della specifica</span>
            <input
              aria-label="Immagine della specifica"
              type="file"
              accept="image/*"
              disabled={loading}
              onChange={(event) => {
                setFile(event.target.files?.[0] ?? null);
                setResult(null);
                setError("");
              }}
            />
          </label>

          {file && (
            <div style={{ color: "#d4d4d8", fontSize: 14 }}>
              File selezionato: <strong>{file.name}</strong>
            </div>
          )}

          <button
            type="submit"
            disabled={!file || loading}
            style={{
              justifySelf: "start",
              border: "1px solid #444",
              borderRadius: 8,
              padding: "10px 16px",
              fontWeight: 800,
              cursor: !file || loading ? "not-allowed" : "pointer",
              background: !file || loading ? "#18181b" : "#fff",
              color: !file || loading ? "#71717a" : "#000",
            }}
          >
            {loading ? "Acquisizione in corso…" : "Acquisisci"}
          </button>
        </form>
      </section>

      {error && (
        <section
          role="alert"
          style={{
            border: "1px solid #7f1d1d",
            background: "#1f0a0a",
            borderRadius: 12,
            padding: 16,
          }}
        >
          <strong>Errore</strong>
          <div style={{ marginTop: 6 }}>{error}</div>
        </section>
      )}

      {result && (
        <section
          aria-label="Esito acquisizione"
          style={{
            border: "1px solid #27272a",
            background: "#0b0b0c",
            borderRadius: 12,
            padding: 16,
            display: "grid",
            gap: 14,
          }}
        >
          <div>
            <h2 style={{ margin: 0, fontSize: 19 }}>
              {result.ok
                ? "Acquisizione completata"
                : "Acquisizione rifiutata"}
            </h2>
            <div style={{ marginTop: 6, color: "#a1a1aa" }}>
              Il risultato non costituisce dato autorevole.
            </div>
          </div>

          <dl
            style={{
              margin: 0,
              display: "grid",
              gridTemplateColumns: "minmax(180px, auto) 1fr",
              gap: "8px 14px",
            }}
          >
            <dt>Stato</dt>
            <dd style={{ margin: 0 }}>{result.status}</dd>

            <dt>Stato semantico</dt>
            <dd style={{ margin: 0 }}>
              {result.semantic_status ?? "non disponibile"}
            </dd>

            <dt>Revisione richiesta</dt>
            <dd style={{ margin: 0 }}>
              {booleanLabel(result.requires_review)}
            </dd>

            <dt>Writer chiamato</dt>
            <dd style={{ margin: 0 }}>
              {booleanLabel(result.writer_called)}
            </dd>

            <dt>Persistito</dt>
            <dd style={{ margin: 0 }}>
              {booleanLabel(result.persisted)}
            </dd>

            <dt>Stato acquisizione</dt>
            <dd style={{ margin: 0 }}>{result.acquisition.status}</dd>

            <dt>Tipo immagine</dt>
            <dd style={{ margin: 0 }}>
              {result.acquisition.media_type ?? "non disponibile"}
            </dd>

            <dt>Errore binding</dt>
            <dd style={{ margin: 0 }}>
              {result.error_code ?? "nessuno"}
            </dd>

            <dt>Errore acquisizione</dt>
            <dd style={{ margin: 0 }}>
              {result.acquisition.error_code ?? "nessuno"}
            </dd>
          </dl>

          <div>
            <h3 style={{ margin: "0 0 8px", fontSize: 16 }}>
              Payload da revisionare
            </h3>

            {result.review_payloads.length === 0 ? (
              <div style={{ color: "#a1a1aa" }}>
                Nessun payload disponibile.
              </div>
            ) : (
              <pre
                style={{
                  margin: 0,
                  padding: 12,
                  overflowX: "auto",
                  borderRadius: 8,
                  background: "#050505",
                  border: "1px solid #27272a",
                  whiteSpace: "pre-wrap",
                }}
              >
                {JSON.stringify(result.review_payloads, null, 2)}
              </pre>
            )}
          </div>
        </section>
      )}
    </main>
  );
}
