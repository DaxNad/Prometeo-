import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import React from "react";

const fetchProductionBoard = vi.fn();
const fetchProductionLoad = vi.fn();
const fetchProductionSequence = vi.fn();

vi.mock("../services/production", () => ({
  fetchProductionBoard,
  fetchProductionLoad,
  fetchProductionSequence,
  fetchProductionTurnPlan: vi.fn(),
}));

import ProductionDashboard from "./ProductionDashboard";

describe("TL Board page", () => {
  beforeEach(() => {
    vi.clearAllMocks();

    fetchProductionBoard.mockResolvedValue({
      ok: true,
      items: [
        {
          order_id: "ORD-1",
          codice: "ABC",
          postazione: "ZAW-1",
          qta: 5,
          semaforo: "ROSSO",
          stato: "bloccato",
          note: "",
        },
      ],
    });
    fetchProductionLoad.mockResolvedValue({ ok: true, items: [] });
    fetchProductionSequence.mockResolvedValue({ ok: true, items: [] });
  });

  it("renders core sections and table headers with valid data", async () => {
    render(<ProductionDashboard />);

    expect(await screen.findByText(/TL Board/i)).toBeDefined();
    expect(await screen.findByText(/attenzione immediata/i)).toBeDefined();
    expect(await screen.findByText(/carico postazioni/i)).toBeDefined();
    expect(await screen.findByText(/sequenza consigliata/i)).toBeDefined();

    expect(await screen.findByText(/codice/i)).toBeDefined();
    expect(await screen.findByText(/postazione/i)).toBeDefined();
    expect(await screen.findByText(/qta totale/i)).toBeDefined();
    expect(await screen.findByText(/righe/i)).toBeDefined();
    expect(await screen.findByText(/prio/i)).toBeDefined();
    expect(await screen.findByText(/aggiorna ora/i)).toBeDefined();
    expect(await screen.findByText(/ultimo aggiornamento/i)).toBeDefined();
  });

  it("shows readable error and avoids crash when initial load fails", async () => {
    fetchProductionBoard.mockRejectedValueOnce(new Error("boom"));

    render(<ProductionDashboard />);

    expect(await screen.findByRole("alert")).toHaveTextContent(/impossibile aggiornare la dashboard/i);
    expect(screen.getByText(/TL Board/i)).toBeDefined();
    expect(screen.getByRole("button", { name: /aggiorna ora/i })).toBeDefined();
  });
});
