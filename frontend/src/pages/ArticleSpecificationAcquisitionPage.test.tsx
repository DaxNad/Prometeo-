import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { cleanup, fireEvent, render, screen } from "@testing-library/react";

const { acquireArticleSpecification } = vi.hoisted(() => ({
  acquireArticleSpecification: vi.fn(),
}));

vi.mock("../lib/api/prometeo", () => ({
  acquireArticleSpecification,
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
