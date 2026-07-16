import { useState, type FormEvent } from "react";
import {
  acquireProductionProgramImageOCR,
  type ProductionProgramImageOCRAcquisitionResponse,
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

function booleanLabel(value: boolean): string {
  return value ? "true" : "false";
}

function normalizeTransportError(error: unknown): string {
  const message = error instanceof Error ? error.message : "";

  if (
    message.includes("Failed to fetch") ||
    message.includes("NetworkError") ||
    message.includes("POST /production-program/image-ocr/acquire failed")
  ) {
    return "PROMETEO non è raggiungibile oppure ha rifiutato la richiesta.";
  }

  return "Acquisizione OCR non completata. Verificare il file e riprovare.";
}

function outcomeTitle(result: ProductionProgramImageOCRAcquisitionResponse): string {
  switch (result.status) {
    case "PREVIEW_READY":
      return "Preview OCR disponibile";
    case "PREVIEW_BLOCKED":
      return "Preview OCR bloccata";
    case "OCR_FAILED":
      return "OCR non completato";
    case "REJECTED":
      return "Immagine rifiutata";
    default:
      return result.ok ? "Risultato OCR disponibile" : "Acquisizione OCR non riuscita";
  }
}

export default function ProductionProgramImageOCRAcquisitionPage() {
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] =
    useState<ProductionProgramImageOCRAcquisitionResponse | null>(null);
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
      const response = await acquireProductionProgramImageOCR({
        image_base64: imageBase64,
      });
      setResult(response);
    } catch (caughtError) {
      setError(normalizeTransportError(caughtError));
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
          Acquisizione programma produzione
        </h1>
        <p style={{ margin: 0, color: "#a1a1aa", lineHeight: 1.5 }}>
          Estrazione OCR locale da una singola immagine PNG o JPEG.
          Il risultato è una preview non autorevole e non viene persistito.
        </p>
        <p style={{ margin: 0, color: "#a1a1aa", lineHeight: 1.5 }}>
          Una risposta HTTP 200 non equivale automaticamente a successo operativo.
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
            <span style={{ fontWeight: 700 }}>
              Immagine programma produzione
            </span>
            <input
              aria-label="Immagine programma produzione"
              type="file"
              accept="image/png,image/jpeg"
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
            {loading ? "Acquisizione in corso…" : "Acquisisci preview OCR"}
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
          <strong>Errore di trasporto</strong>
          <div style={{ marginTop: 6 }}>{error}</div>
        </section>
      )}

      {result && (
        <section
          aria-label="Esito acquisizione OCR"
          style={{
            border: "1px solid #27272a",
            background: "#0b0b0c",
            borderRadius: 12,
            padding: 16,
            display: "grid",
            gap: 16,
          }}
        >
          <div>
            <h2 style={{ margin: 0, fontSize: 19 }}>
              {outcomeTitle(result)}
            </h2>
            <div style={{ marginTop: 6, color: "#a1a1aa" }}>
              Stato backend: {result.status}
            </div>
          </div>

          <dl
            style={{
              margin: 0,
              display: "grid",
              gridTemplateColumns: "minmax(190px, auto) 1fr",
              gap: "8px 14px",
            }}
          >
            <dt>Stato semantico</dt>
            <dd style={{ margin: 0 }}>{result.semantic_status}</dd>

            <dt>Errore</dt>
            <dd style={{ margin: 0 }}>{result.error_code ?? "nessuno"}</dd>

            <dt>Fonte</dt>
            <dd style={{ margin: 0 }}>{result.source_id ?? "non disponibile"}</dd>

            <dt>Hash fonte</dt>
            <dd style={{ margin: 0 }}>{result.source_hash ?? "non disponibile"}</dd>

            <dt>Tipo immagine</dt>
            <dd style={{ margin: 0 }}>{result.media_type ?? "non disponibile"}</dd>

            <dt>Provider OCR</dt>
            <dd style={{ margin: 0 }}>{result.provider ?? "non disponibile"}</dd>

            <dt>Conferma richiesta</dt>
            <dd style={{ margin: 0 }}>
              {booleanLabel(result.requires_confirmation)}
            </dd>

            <dt>Persistito</dt>
            <dd style={{ margin: 0 }}>{booleanLabel(result.persisted)}</dd>

            <dt>Writer chiamato</dt>
            <dd style={{ margin: 0 }}>{booleanLabel(result.writer_called)}</dd>

            <dt>Planner chiamato</dt>
            <dd style={{ margin: 0 }}>{booleanLabel(result.planner_called)}</dd>

            <dt>Pattern Learning chiamato</dt>
            <dd style={{ margin: 0 }}>
              {booleanLabel(result.pattern_learning_called)}
            </dd>
          </dl>

          <section>
            <h3 style={{ margin: "0 0 8px", fontSize: 16 }}>
              Testo OCR osservato
            </h3>
            <pre
              style={{
                margin: 0,
                whiteSpace: "pre-wrap",
                overflowWrap: "anywhere",
                background: "#050505",
                border: "1px solid #27272a",
                borderRadius: 8,
                padding: 12,
              }}
            >
              {result.observed_text || "non disponibile"}
            </pre>
          </section>

          <section>
            <h3 style={{ margin: "0 0 8px", fontSize: 16 }}>
              Righe normalizzate
            </h3>
            {result.normalized_lines.length > 0 ? (
              <ul style={{ margin: 0, paddingLeft: 20 }}>
                {result.normalized_lines.map((line, index) => (
                  <li key={`${index}-${line}`}>{line}</li>
                ))}
              </ul>
            ) : (
              <div>non disponibili</div>
            )}
          </section>

          <section>
            <h3 style={{ margin: "0 0 8px", fontSize: 16 }}>
              Snapshot preview
            </h3>
            <pre
              style={{
                margin: 0,
                whiteSpace: "pre-wrap",
                overflowWrap: "anywhere",
                background: "#050505",
                border: "1px solid #27272a",
                borderRadius: 8,
                padding: 12,
              }}
            >
              {result.snapshot_preview
                ? JSON.stringify(result.snapshot_preview, null, 2)
                : "non disponibile"}
            </pre>
          </section>
        </section>
      )}
    </main>
  );
}
