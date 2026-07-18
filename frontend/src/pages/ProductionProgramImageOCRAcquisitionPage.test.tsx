import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { cleanup, fireEvent, render, screen } from "@testing-library/react";

const {
  acquireProductionProgramImageOCR,
  confirmProductionProgramSnapshot,
} = vi.hoisted(() => ({
  acquireProductionProgramImageOCR: vi.fn(),
  confirmProductionProgramSnapshot: vi.fn(),
}));

vi.mock("../lib/api/prometeo", () => ({
  acquireProductionProgramImageOCR,
  confirmProductionProgramSnapshot,
}));

import ProductionProgramImageOCRAcquisitionPage from "./ProductionProgramImageOCRAcquisitionPage";

function syntheticFile(
  bytes: number[],
  name: string,
  type: string
): File {
  const file = new File([new Uint8Array(bytes)], name, { type });

  Object.defineProperty(file, "arrayBuffer", {
    value: vi.fn().mockResolvedValue(new Uint8Array(bytes).buffer),
  });

  return file;
}

function governedResponse(overrides: Record<string, unknown> = {}) {
  return {
    ok: true,
    status: "PREVIEW_READY",
    source_id: "production-program-image:sha256:test",
    source_hash: "hash-test",
    media_type: "image/png",
    provider: "synthetic-local-ocr",
    error_code: null,
    requires_confirmation: true,
    semantic_status: "DA_VERIFICARE",
    persisted: false,
    writer_called: false,
    planner_called: false,
    pattern_learning_called: false,
    observed_text: "ARTICOLO SYNTH-01",
    normalized_lines: ["ARTICOLO SYNTH-01"],
    snapshot_preview: {
      status: "PREVIEW_READY",
      article: "SYNTH-01",
    },
    ...overrides,
  };
}

describe("Production program image OCR acquisition page", () => {
  afterEach(() => {
    cleanup();
  });

  beforeEach(() => {
    vi.resetAllMocks();
  });

  it("renders a review-only form and disables submit without a file", () => {
    render(<ProductionProgramImageOCRAcquisitionPage />);

    expect(
      screen.getByRole("heading", {
        name: /acquisizione programma produzione/i,
      })
    ).toBeDefined();

    expect(
      screen.getByText(/preview non autorevole e non viene persistito/i)
    ).toBeDefined();

    expect(
      screen.getByText(/http 200 non equivale automaticamente/i)
    ).toBeDefined();

    expect(
      (
        screen.getByRole("button", {
          name: /acquisisci preview ocr/i,
        }) as HTMLButtonElement
      ).disabled
    ).toBe(true);

    expect(
      screen.queryByRole("button", { name: /conferma|persisti/i })
    ).toBeNull();
  });

  it("converts a synthetic PNG to Base64 and renders PREVIEW_READY", async () => {
    acquireProductionProgramImageOCR.mockResolvedValue(governedResponse());

    const file = syntheticFile(
      [137, 80, 78, 71, 13, 10, 26, 10],
      "programma.png",
      "image/png"
    );

    render(<ProductionProgramImageOCRAcquisitionPage />);

    fireEvent.change(
      screen.getByLabelText(/immagine programma produzione/i),
      { target: { files: [file] } }
    );

    fireEvent.click(
      screen.getByRole("button", { name: /acquisisci preview ocr/i })
    );

    expect(
      await screen.findByRole("heading", {
        name: /preview ocr disponibile/i,
      })
    ).toBeDefined();

    expect(acquireProductionProgramImageOCR).toHaveBeenCalledWith({
      image_base64: "iVBORw0KGgo=",
    });

    expect(
      screen.getByText((_, element) =>
        element?.tagName === "DIV" &&
        element.textContent === "Stato backend: PREVIEW_READY"
      )
    ).toBeDefined();
    expect(screen.getByText("DA_VERIFICARE")).toBeDefined();
    expect(
      screen.getAllByText("ARTICOLO SYNTH-01").length
    ).toBeGreaterThanOrEqual(2);
    expect(screen.getByText("synthetic-local-ocr")).toBeDefined();
    expect(screen.getAllByText("false").length).toBeGreaterThanOrEqual(4);
    expect(screen.getByText("true")).toBeDefined();
  });

  it("accepts a synthetic JPEG", async () => {
    acquireProductionProgramImageOCR.mockResolvedValue(
      governedResponse({
        media_type: "image/jpeg",
        source_id: "production-program-image:sha256:jpeg",
      })
    );

    const file = syntheticFile(
      [255, 216, 255, 224],
      "programma.jpg",
      "image/jpeg"
    );

    render(<ProductionProgramImageOCRAcquisitionPage />);

    fireEvent.change(
      screen.getByLabelText(/immagine programma produzione/i),
      { target: { files: [file] } }
    );

    fireEvent.click(
      screen.getByRole("button", { name: /acquisisci preview ocr/i })
    );

    expect(
      await screen.findByText("image/jpeg")
    ).toBeDefined();

    expect(acquireProductionProgramImageOCR).toHaveBeenCalledTimes(1);
  });

  it("does not present PREVIEW_BLOCKED as success", async () => {
    acquireProductionProgramImageOCR.mockResolvedValue(
      governedResponse({
        ok: false,
        status: "PREVIEW_BLOCKED",
        error_code: "MISSING_DELIMITER",
      })
    );

    render(<ProductionProgramImageOCRAcquisitionPage />);

    fireEvent.change(
      screen.getByLabelText(/immagine programma produzione/i),
      {
        target: {
          files: [
            syntheticFile([137, 80, 78, 71], "blocked.png", "image/png"),
          ],
        },
      }
    );

    fireEvent.click(
      screen.getByRole("button", { name: /acquisisci preview ocr/i })
    );

    expect(
      await screen.findByRole("heading", {
        name: /preview ocr bloccata/i,
      })
    ).toBeDefined();

    expect(screen.getByText("MISSING_DELIMITER")).toBeDefined();
    expect(
      screen.queryByText(/preview ocr disponibile/i)
    ).toBeNull();
  });

  it.each([
    ["OCR_FAILED", "OCR_TIMEOUT", /ocr non completato/i],
    ["REJECTED", "UNSUPPORTED_IMAGE_TYPE", /immagine rifiutata/i],
  ])(
    "renders %s and its error code",
    async (status, errorCode, heading) => {
      acquireProductionProgramImageOCR.mockResolvedValue(
        governedResponse({
          ok: false,
          status,
          error_code: errorCode,
          observed_text: null,
          normalized_lines: [],
          snapshot_preview: null,
        })
      );

      render(<ProductionProgramImageOCRAcquisitionPage />);

      fireEvent.change(
        screen.getByLabelText(/immagine programma produzione/i),
        {
          target: {
            files: [
              syntheticFile([137, 80, 78, 71], "failed.png", "image/png"),
            ],
          },
        }
      );

      fireEvent.click(
        screen.getByRole("button", { name: /acquisisci preview ocr/i })
      );

      expect(
        await screen.findByRole("heading", { name: heading })
      ).toBeDefined();

      expect(screen.getByText(errorCode)).toBeDefined();
    }
  );

  it("shows transport failure", async () => {
    acquireProductionProgramImageOCR.mockRejectedValue(
      new Error(
        "POST /production-program/image-ocr/acquire failed: 500"
      )
    );

    render(<ProductionProgramImageOCRAcquisitionPage />);

    fireEvent.change(
      screen.getByLabelText(/immagine programma produzione/i),
      {
        target: {
          files: [
            syntheticFile([137, 80, 78, 71], "error.png", "image/png"),
          ],
        },
      }
    );

    fireEvent.click(
      screen.getByRole("button", { name: /acquisisci preview ocr/i })
    );

    expect(
      await screen.findByRole("alert")
    ).toBeDefined();

    expect(
      screen.getByText(/prometeo non è raggiungibile oppure ha rifiutato/i)
    ).toBeDefined();
  });

  it("persists only after explicit authorized confirmation", async () => {
    acquireProductionProgramImageOCR.mockResolvedValue(governedResponse());
    confirmProductionProgramSnapshot.mockResolvedValue({
      ok: true,
      error_code: null,
      status: "CONFERMATO",
      semantic_status: "CONFERMATO",
      requires_confirmation: false,
      persisted: true,
      write_performed: true,
      registry_id: "production-program-verified:sha256:synthetic",
      snapshot_id: "production-program-snapshot:sha256:synthetic",
      version: 1,
      source: "production_program_snapshot_registry",
      source_id: "production-program-image:sha256:test",
      source_hash: "hash-test",
      confirmed_by: {
        actor_id: "synthetic-team-leader",
        authority_role: "RESPONSABILE_PRODUZIONE",
      },
      confirmed_at: "2026-08-01T08:30:00Z",
    });

    render(<ProductionProgramImageOCRAcquisitionPage />);
    fireEvent.change(
      screen.getByLabelText(/immagine programma produzione/i),
      {
        target: {
          files: [syntheticFile([137, 80, 78, 71], "confirm.png", "image/png")],
        },
      }
    );
    fireEvent.click(
      screen.getByRole("button", { name: /acquisisci preview ocr/i })
    );

    await screen.findByRole("button", {
      name: /conferma e persisti snapshot/i,
    });
    expect(screen.queryByText(/snapshot confermato/i)).toBeNull();
    fireEvent.change(screen.getByLabelText(/identificativo attore/i), {
      target: { value: "synthetic-team-leader" },
    });
    fireEvent.change(screen.getByLabelText(/nota audit/i), {
      target: { value: "Synthetic confirmation." },
    });
    fireEvent.click(
      screen.getByRole("button", {
        name: /conferma e persisti snapshot/i,
      })
    );

    expect(
      await screen.findByRole("heading", { name: /snapshot confermato/i })
    ).toBeDefined();
    expect(confirmProductionProgramSnapshot).toHaveBeenCalledWith({
      source_id: "production-program-image:sha256:test",
      source_hash: "hash-test",
      observed_text: "ARTICOLO SYNTH-01",
      snapshot_preview: {
        status: "PREVIEW_READY",
        article: "SYNTH-01",
      },
      actor_id: "synthetic-team-leader",
      authority_role: "RESPONSABILE_PRODUZIONE",
      confirmed_at: expect.any(String),
      audit_note: "Synthetic confirmation.",
    });
    expect(screen.getByText("CONFERMATO")).toBeDefined();
    expect(screen.queryByText("CERTO")).toBeNull();
  });

  it("does not show persisted success when confirmation fails", async () => {
    acquireProductionProgramImageOCR.mockResolvedValue(governedResponse());
    confirmProductionProgramSnapshot.mockResolvedValue({
      ok: false,
      error_code: "WRITE_FAILED",
      status: "BLOCCATO",
      semantic_status: "BLOCCATO",
      requires_confirmation: true,
      persisted: false,
      write_performed: false,
    });

    render(<ProductionProgramImageOCRAcquisitionPage />);
    fireEvent.change(
      screen.getByLabelText(/immagine programma produzione/i),
      {
        target: {
          files: [syntheticFile([137, 80, 78, 71], "failed.png", "image/png")],
        },
      }
    );
    fireEvent.click(
      screen.getByRole("button", { name: /acquisisci preview ocr/i })
    );
    await screen.findByRole("button", {
      name: /conferma e persisti snapshot/i,
    });
    fireEvent.change(screen.getByLabelText(/identificativo attore/i), {
      target: { value: "synthetic-team-leader" },
    });
    fireEvent.change(screen.getByLabelText(/nota audit/i), {
      target: { value: "Synthetic confirmation." },
    });
    fireEvent.click(
      screen.getByRole("button", {
        name: /conferma e persisti snapshot/i,
      })
    );

    expect(await screen.findByRole("alert")).toBeDefined();
    expect(screen.getByText("WRITE_FAILED")).toBeDefined();
    expect(
      screen.queryByRole("heading", { name: /snapshot confermato/i })
    ).toBeNull();
  });
});
