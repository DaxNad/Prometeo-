import { useState, type FormEvent } from "react";
import {
  acquireProductionProgramImageOCR,
  acquireProductionProgramImagesOCR,
  confirmProductionProgramSnapshot,
  type ProductionProgramImageOCRAcquisitionResponse,
  type ProductionProgramSnapshotConfirmationResponse,
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
  const [files, setFiles] = useState<File[]>([]);
  const [result, setResult] =
    useState<ProductionProgramImageOCRAcquisitionResponse | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [actorId, setActorId] = useState("");
  const [auditNote, setAuditNote] = useState("");
  const [confirmation, setConfirmation] =
    useState<ProductionProgramSnapshotConfirmationResponse | null>(null);
  const [confirmationError, setConfirmationError] = useState("");
  const [confirming, setConfirming] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (files.length === 0 || loading) return;

    setLoading(true);
    setError("");
    setResult(null);
    setConfirmation(null);
    setConfirmationError("");

    try {
      const imagesBase64 = await Promise.all(files.map(fileToBase64));
      const response =
        imagesBase64.length === 1
          ? await acquireProductionProgramImageOCR({
              image_base64: imagesBase64[0],
            })
          : await acquireProductionProgramImagesOCR({
              images_base64: imagesBase64,
            });
      setResult(response);
    } catch (caughtError) {
      setError(normalizeTransportError(caughtError));
    } finally {
      setLoading(false);
    }
  }

  async function confirm(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (
      !result?.ok ||
      result.status !== "PREVIEW_READY" ||
      !result.source_id ||
      !result.source_hash ||
      !result.observed_text ||
      !result.snapshot_preview ||
      !actorId.trim() ||
      !auditNote.trim() ||
      confirming
    ) {
      return;
    }

    setConfirming(true);
    setConfirmation(null);
    setConfirmationError("");
    try {
      const response = await confirmProductionProgramSnapshot({
        source_id: result.source_id,
        source_hash: result.source_hash,
        observed_text: result.observed_text,
        snapshot_preview: result.snapshot_preview,
        actor_id: actorId.trim(),
        authority_role: "RESPONSABILE_PRODUZIONE",
        confirmed_at: new Date().toISOString(),
        audit_note: auditNote.trim(),
      });
      if (
        response.ok &&
        response.persisted &&
        response.status === "CONFERMATO"
      ) {
        setConfirmation(response);
      } else {
        setConfirmationError(
          response.error_code || "CONFERMA_NON_PERSISTITA"
        );
      }
    } catch {
      setConfirmationError(
        "PROMETEO non è raggiungibile oppure ha rifiutato la conferma."
      );
    } finally {
      setConfirming(false);
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
          Estrazione OCR locale da una o più immagini PNG o JPEG.
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
              multiple
              disabled={loading}
              onChange={(event) => {
                setFiles(Array.from(event.target.files ?? []));
                setResult(null);
                setError("");
                setConfirmation(null);
                setConfirmationError("");
              }}
            />
          </label>

          {files.length > 0 && (
            <div style={{ color: "#d4d4d8", fontSize: 14 }}>
              File selezionati:{" "}
              <strong>{files.map((selectedFile) => selectedFile.name).join(", ")}</strong>
            </div>
          )}

          <button
            type="submit"
            disabled={files.length === 0 || loading}
            style={{
              justifySelf: "start",
              border: "1px solid #444",
              borderRadius: 8,
              padding: "10px 16px",
              fontWeight: 800,
              cursor: files.length === 0 || loading ? "not-allowed" : "pointer",
              background: files.length === 0 || loading ? "#18181b" : "#fff",
              color: files.length === 0 || loading ? "#71717a" : "#000",
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

          {result.ok &&
            result.status === "PREVIEW_READY" &&
            result.source_id &&
            result.source_hash &&
            result.observed_text &&
            result.snapshot_preview && (
              <section
                aria-label="Conferma snapshot programma produzione"
                style={{
                  borderTop: "1px solid #27272a",
                  paddingTop: 16,
                }}
              >
                <h3 style={{ margin: "0 0 8px", fontSize: 16 }}>
                  Conferma umana autorizzata
                </h3>
                <p style={{ color: "#a1a1aa" }}>
                  La conferma persiste una versione CONFERMATO; non promuove
                  lo snapshot a CERTO e non attiva il planner.
                </p>
                <form onSubmit={confirm} style={{ display: "grid", gap: 12 }}>
                  <label style={{ display: "grid", gap: 6 }}>
                    <span>Identificativo attore</span>
                    <input
                      aria-label="Identificativo attore"
                      value={actorId}
                      disabled={confirming}
                      onChange={(event) => setActorId(event.target.value)}
                    />
                  </label>
                  <div>
                    Ruolo autorizzato: <strong>RESPONSABILE_PRODUZIONE</strong>
                  </div>
                  <label style={{ display: "grid", gap: 6 }}>
                    <span>Nota audit</span>
                    <textarea
                      aria-label="Nota audit"
                      value={auditNote}
                      disabled={confirming}
                      onChange={(event) => setAuditNote(event.target.value)}
                    />
                  </label>
                  <button
                    type="submit"
                    disabled={
                      confirming || !actorId.trim() || !auditNote.trim()
                    }
                    style={{ justifySelf: "start" }}
                  >
                    {confirming
                      ? "Conferma in corso…"
                      : "Conferma e persisti snapshot"}
                  </button>
                </form>
              </section>
            )}

          {confirmationError && (
            <section role="alert">
              <strong>Conferma non persistita</strong>
              <div>{confirmationError}</div>
            </section>
          )}

          {confirmation && (
            <section aria-label="Snapshot confermato">
              <h3>Snapshot confermato</h3>
              <dl>
                <dt>Stato persistito</dt>
                <dd>{confirmation.status}</dd>
                <dt>Versione</dt>
                <dd>{confirmation.version}</dd>
                <dt>Identità registry</dt>
                <dd>{confirmation.registry_id}</dd>
              </dl>
            </section>
          )}
        </section>
      )}
    </main>
  );
}
