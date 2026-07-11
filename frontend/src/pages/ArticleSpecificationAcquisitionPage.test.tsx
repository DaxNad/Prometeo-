import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { cleanup, fireEvent, render, screen } from "@testing-library/react";

const {
  acquireArticleSpecification,
  confirmArticleSpecification,
} = vi.hoisted(() => ({
  acquireArticleSpecification: vi.fn(),
  confirmArticleSpecification: vi.fn(),
}));

vi.mock("../lib/api/prometeo", () => ({
  acquireArticleSpecification,
  confirmArticleSpecification,
}));

import ArticleSpecificationAcquisitionPage from "./ArticleSpecificationAcquisitionPage";

describe("Article specification acquisition page", () => {
  afterEach(() => {
    cleanup();
  });

  beforeEach(() => {
    vi.resetAllMocks();
  });

  it("renders a review-only acquisition form", () => {
    render(<ArticleSpecificationAcquisitionPage />);

    expect(
      screen.getByRole("heading", {
        name: /acquisizione specifica articolo/i,
      })
    ).toBeDefined();

    expect(
      screen.getByText(/nessun dato viene salvato o promosso automaticamente/i)
    ).toBeDefined();

    expect(
      (
        screen.getByRole("button", {
          name: /^acquisisci$/i,
        }) as HTMLButtonElement
      ).disabled
    ).toBe(true);
  });

  it("submits the image and exposes governed result fields", async () => {
    acquireArticleSpecification.mockResolvedValue({
      ok: true,
      status: "BOUND",
      source_id: "source-1",
      semantic_status: "DA_VERIFICARE",
      writer_called: false,
      persisted: false,
      requires_review: true,
      error_code: null,
      acquisition: {
        ok: true,
        status: "EXTRACTED",
        source_id: "source-1",
        source_hash: "hash-1",
        media_type: "image/png",
        error_code: null,
      },
      review_payloads: [
        {
          article: "SYNTH-01",
          semantic_status: "DA_VERIFICARE",
        },
      ],
      facade_results: [
        {
          ok: true,
          status: "NOT_EXECUTED",
          writer_called: false,
          source_id: "source-1",
          error_code: null,
        },
      ],
    });

    const file = new File(
      [new Uint8Array([137, 80, 78, 71])],
      "specifica.png",
      { type: "image/png" }
    );

    Object.defineProperty(file, "arrayBuffer", {
      value: vi.fn().mockResolvedValue(
        new Uint8Array([137, 80, 78, 71]).buffer
      ),
    });

    render(<ArticleSpecificationAcquisitionPage />);

    fireEvent.change(
      screen.getByLabelText(/immagine della specifica/i),
      {
        target: { files: [file] },
      }
    );

    fireEvent.click(
      screen.getByRole("button", { name: /^acquisisci$/i })
    );

    expect(
      await screen.findByRole("heading", {
        name: /acquisizione completata/i,
      })
    ).toBeDefined();

    expect(
      acquireArticleSpecification
    ).toHaveBeenCalledTimes(1);

    expect(
      await screen.findByText("DA_VERIFICARE")
    ).toBeDefined();

    expect(
      screen.getByText(/il risultato non costituisce dato autorevole/i)
    ).toBeDefined();

    expect(
      screen.getByText(/SYNTH-01/i)
    ).toBeDefined();

    expect(
      screen.getAllByText("false").length
    ).toBeGreaterThanOrEqual(2);

    expect(
      screen.getByText("true")
    ).toBeDefined();
  });

  it("submits a separate governed human confirmation", async () => {
    acquireArticleSpecification.mockResolvedValue({
      ok: true,
      status: "BOUND",
      source_id: "source-confirm-1",
      semantic_status: "DA_VERIFICARE",
      writer_called: false,
      persisted: false,
      requires_review: true,
      error_code: null,
      acquisition: {
        ok: true,
        status: "EXTRACTED",
        source_id: "source-confirm-1",
        source_hash: "hash-confirm-1",
        media_type: "image/png",
        error_code: null,
      },
      review_payloads: [
        {
          field_name: "article",
          value: "SYNTH-CONFIRM-UI",
          semantic_status: "DA_VERIFICARE",
        },
        {
          field_name: "drawing",
          value: "DRAW-01",
          semantic_status: "DA_VERIFICARE",
        },
      ],
      facade_results: [],
    });
    confirmArticleSpecification.mockResolvedValue({
      ok: true,
      status: "ORCHESTRATED",
      source_id: "source-confirm-1",
      writer_called: true,
      persisted: true,
      created: true,
      updated: false,
      error_code: null,
    });

    const file = new File([new Uint8Array([137])], "specifica.png", {
      type: "image/png",
    });
    Object.defineProperty(file, "arrayBuffer", {
      value: vi.fn().mockResolvedValue(new Uint8Array([137]).buffer),
    });

    render(<ArticleSpecificationAcquisitionPage />);

    fireEvent.change(
      screen.getByLabelText(/immagine della specifica/i),
      { target: { files: [file] } }
    );
    fireEvent.click(
      screen.getByRole("button", { name: /^acquisisci$/i })
    );

    await screen.findByLabelText(/conferma umana/i);

    fireEvent.change(screen.getByLabelText(/classe operativa/i), {
      target: { value: "STANDARD" },
    });
    fireEvent.click(screen.getByLabelText(/planner eligible/i));
    fireEvent.click(screen.getByLabelText(/conferma tl richiesta/i));
    fireEvent.change(screen.getByLabelText(/nota audit/i), {
      target: { value: "Conferma verificata dal responsabile." },
    });
    fireEvent.click(
      screen.getByLabelText(
        /conferma autorità responsabile produzione/i
      )
    );
    fireEvent.click(
      screen.getByRole("button", { name: /conferma e persisti/i })
    );

    expect(confirmArticleSpecification).toHaveBeenCalledWith({
      article: "SYNTH-CONFIRM-UI",
      operational_class: "STANDARD",
      planner_eligible: true,
      tl_confirmation_required: false,
      authority_role: "RESPONSABILE_PRODUZIONE",
      audit_note: "Conferma verificata dal responsabile.",
      source_id: "source-confirm-1",
      drawing: "DRAW-01",
      material: undefined,
      description: undefined,
    });

    expect(
      await screen.findByText("ORCHESTRATED")
    ).toBeDefined();
    expect(
      screen.getByLabelText(/esito conferma/i)
    ).toBeDefined();
  });

  it("exposes a governed write failure without claiming persistence", async () => {
    acquireArticleSpecification.mockResolvedValue({
      ok: true,
      status: "BOUND",
      source_id: "source-write-failure",
      semantic_status: "DA_VERIFICARE",
      writer_called: false,
      persisted: false,
      requires_review: true,
      error_code: null,
      acquisition: {
        ok: true,
        status: "EXTRACTED",
        source_id: "source-write-failure",
        source_hash: "hash-write-failure",
        media_type: "image/png",
        error_code: null,
      },
      review_payloads: [
        {
          field_name: "article",
          value: "SYNTH-WRITE-FAIL-UI",
          semantic_status: "DA_VERIFICARE",
        },
      ],
      facade_results: [],
    });
    confirmArticleSpecification.mockResolvedValue({
      ok: false,
      status: "ORCHESTRATION_FAILED",
      source_id: "source-write-failure",
      writer_called: true,
      persisted: false,
      created: false,
      updated: false,
      error_code: "WRITE_FAILED",
    });

    const file = new File([new Uint8Array([137])], "specifica.png", {
      type: "image/png",
    });
    Object.defineProperty(file, "arrayBuffer", {
      value: vi.fn().mockResolvedValue(
        new Uint8Array([137]).buffer
      ),
    });

    render(<ArticleSpecificationAcquisitionPage />);

    fireEvent.change(
      screen.getByLabelText(/immagine della specifica/i),
      { target: { files: [file] } }
    );
    fireEvent.click(
      screen.getByRole("button", { name: /^acquisisci$/i })
    );

    await screen.findByLabelText(/conferma umana/i);

    fireEvent.change(screen.getByLabelText(/nota audit/i), {
      target: { value: "Conferma con fallimento sintetico." },
    });
    fireEvent.click(
      screen.getByLabelText(
        /conferma autorità responsabile produzione/i
      )
    );
    fireEvent.click(
      screen.getByRole("button", { name: /conferma e persisti/i })
    );

    expect(
      await screen.findByText("ORCHESTRATION_FAILED")
    ).toBeDefined();
    expect(screen.getByText("WRITE_FAILED")).toBeDefined();

    const outcome = screen.getByLabelText(/esito conferma/i);
    expect(outcome.textContent).toMatch(/persistito.*false/i);
  });

  it("shows confirmation failure without claiming persistence", async () => {
    acquireArticleSpecification.mockResolvedValue({
      ok: true,
      status: "BOUND",
      source_id: "source-confirm-failure",
      semantic_status: "DA_VERIFICARE",
      writer_called: false,
      persisted: false,
      requires_review: true,
      error_code: null,
      acquisition: {
        ok: true,
        status: "EXTRACTED",
        source_id: "source-confirm-failure",
        source_hash: "hash-confirm-failure",
        media_type: "image/png",
        error_code: null,
      },
      review_payloads: [
        {
          field_name: "article",
          value: "SYNTH-CONFIRM-FAIL",
          semantic_status: "DA_VERIFICARE",
        },
      ],
      facade_results: [],
    });
    confirmArticleSpecification.mockRejectedValue(
      new Error(
        "POST /article-specification/confirm failed: 500 WRITE_FAILED"
      )
    );

    const file = new File([new Uint8Array([137])], "specifica.png", {
      type: "image/png",
    });
    Object.defineProperty(file, "arrayBuffer", {
      value: vi.fn().mockResolvedValue(
        new Uint8Array([137]).buffer
      ),
    });

    render(<ArticleSpecificationAcquisitionPage />);

    fireEvent.change(
      screen.getByLabelText(/immagine della specifica/i),
      { target: { files: [file] } }
    );
    fireEvent.click(
      screen.getByRole("button", { name: /^acquisisci$/i })
    );

    await screen.findByLabelText(/conferma umana/i);

    fireEvent.change(screen.getByLabelText(/nota audit/i), {
      target: { value: "Tentativo controllato." },
    });
    fireEvent.click(
      screen.getByLabelText(
        /conferma autorità responsabile produzione/i
      )
    );
    fireEvent.click(
      screen.getByRole("button", { name: /conferma e persisti/i })
    );

    const alert = await screen.findByRole("alert");
    expect(alert.textContent).toMatch(
      /prometeo ha rifiutato la richiesta/i
    );
    expect(
      screen.queryByLabelText(/esito conferma/i)
    ).toBeNull();
  });

  it("shows a rejected fail-closed result without hiding governance fields", async () => {
    acquireArticleSpecification.mockResolvedValue({
      ok: false,
      status: "REJECTED",
      source_id: null,
      semantic_status: "DA_VERIFICARE",
      writer_called: false,
      persisted: false,
      requires_review: true,
      error_code: "ACQUISITION_NOT_EXTRACTED",
      acquisition: {
        ok: false,
        status: "REJECTED",
        source_id: null,
        source_hash: null,
        media_type: "image/png",
        error_code: "OCR_ADAPTER_REQUIRED",
      },
      review_payloads: [],
      facade_results: [],
    });

    const file = new File([new Uint8Array([1])], "specifica.png", {
      type: "image/png",
    });

    Object.defineProperty(file, "arrayBuffer", {
      value: vi.fn().mockResolvedValue(
        new Uint8Array([1]).buffer
      ),
    });

    render(<ArticleSpecificationAcquisitionPage />);

    fireEvent.change(
      screen.getByLabelText(/immagine della specifica/i),
      {
        target: { files: [file] },
      }
    );

    fireEvent.click(
      screen.getByRole("button", { name: /^acquisisci$/i })
    );

    expect(
      await screen.findByRole("heading", {
        name: /acquisizione rifiutata/i,
      })
    ).toBeDefined();

    expect(
      screen.getByText("OCR_ADAPTER_REQUIRED")
    ).toBeDefined();

    expect(
      screen.getByText("ACQUISITION_NOT_EXTRACTED")
    ).toBeDefined();

    expect(
      screen.getByText(/nessun payload disponibile/i)
    ).toBeDefined();
  });
});
