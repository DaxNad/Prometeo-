import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";

// Hoist shared mock fns to avoid TDZ with vi.mock hoisting
const {
  fetchProductionBoard,
  fetchProductionLoad,
  fetchProductionSequence,
  fetchProductionSequenceAtlasMerge,
  fetchProductionTurnPlan,
} = vi.hoisted(() => ({
  fetchProductionBoard: vi.fn(),
  fetchProductionLoad: vi.fn(),
  fetchProductionSequence: vi.fn(),
  fetchProductionSequenceAtlasMerge: vi.fn(),
  fetchProductionTurnPlan: vi.fn(),
}));

vi.mock("../services/production", () => ({
  fetchProductionBoard,
  fetchProductionLoad,
  fetchProductionSequence,
  fetchProductionSequenceAtlasMerge,
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
    fetchProductionSequence.mockResolvedValue({
      ok: true,
      items: [{ rank: 1, article: "ABC", critical_station: "ZAW-1", quantity: 5 }],
    });
    fetchProductionSequenceAtlasMerge.mockResolvedValue({
      ok: true,
      items: [{
        article: "ABC",
        atlas_merge: {
          final_outcome: "PROCEED",
          final_score: 0.98,
          reasons: [],
          active_constraints: [],
          conflicts: [],
          consensus: {},
          explain_brief: "ok",
        },
      }],
    });
    fetchProductionTurnPlan.mockResolvedValue({ ok: true, items: [] });
  });

  it("renders core sections and table headers with valid data", async () => {
    render(<ProductionDashboard />);

    expect(await screen.findByText(/TL Board/i)).toBeDefined();
    expect(await screen.findByText(/attenzione immediata/i)).toBeDefined();
    expect(await screen.findByText(/carico postazioni/i)).toBeDefined();
    expect(await screen.findByText(/sequenza consigliata/i)).toBeDefined();

    expect(await screen.findByRole("columnheader", { name: /codice/i })).toBeDefined();
    expect(await screen.findByRole("columnheader", { name: /^postazione$/i })).toBeDefined();
    expect(await screen.findByRole("columnheader", { name: /qta totale/i })).toBeDefined();
    expect(await screen.findByRole("columnheader", { name: /righe/i })).toBeDefined();
    expect(await screen.findByRole("columnheader", { name: /prio/i })).toBeDefined();

    expect(await screen.findByText(/PROCEED/i)).toBeDefined();
  });

  it("does not crash on initial load error and shows safe fallbacks", async () => {
    fetchProductionBoard.mockResolvedValue({
      ok: false,
      error: "Errore nel caricamento iniziale",
      items: [],
    });

    render(<ProductionDashboard />);

    expect((await screen.findAllByText(/nessun blocco immediato/i)).length).toBeGreaterThan(0);
    expect((await screen.findAllByText(/nessuna sequenza disponibile/i)).length).toBeGreaterThan(0);
  });
});
