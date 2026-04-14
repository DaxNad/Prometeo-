import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import React from "react";

// Hoist shared mock fns to avoid TDZ with vi.mock hoisting
const {
  fetchProductionBoard,
  fetchProductionLoad,
  fetchProductionSequence,
  fetchProductionTurnPlan,
} = vi.hoisted(() => ({
  fetchProductionBoard: vi.fn(),
  fetchProductionLoad: vi.fn(),
  fetchProductionSequence: vi.fn(),
  fetchProductionTurnPlan: vi.fn(),
}));

vi.mock("../services/production", () => ({
  fetchProductionBoard,
  fetchProductionLoad,
  fetchProductionSequence,
  fetchProductionTurnPlan,
}));

import ProductionDashboard from "./ProductionDashboard";

describe("TL Board page", () => {
  beforeEach(() => {
    vi.resetAllMocks();
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
    fetchProductionTurnPlan.mockResolvedValue({ ok: true, items: [] });
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
  });

  it("shows readable error and avoids crash when initial load fails", async () => {
    fetchProductionBoard.mockResolvedValue({
      ok: false,
      error: "Errore nel caricamento iniziale",
      items: [],
    });

    render(<ProductionDashboard />);

    expect(await screen.findByText(/errore nel caricamento iniziale/i)).toBeDefined();
  });
});
