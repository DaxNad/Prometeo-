import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import React from "react";

// Mock the services used by the page to provide valid data
vi.mock("../services/production", () => ({
  fetchProductionBoard: async () => ({
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
  }),
  fetchProductionLoad: async () => ({ ok: true, items: [] }),
  fetchProductionSequence: async () => ({
    ok: true,
    items: [
      {
        rank: 1,
        article: "ABC",
        critical_station: "ZAW-1",
        quantity: 5,
      },
    ],
  }),
  fetchProductionAtlasMerge: async () => ({
    ok: true,
    items: [
      {
        article: "ABC",
        critical_station: "ZAW-1",
        rank: 1,
        atlas_merge: {
          final_outcome: "PROCEED",
          final_score: 0.78,
          reasons: ["capacity free"],
          active_constraints: [],
          conflicts: [],
          consensus: { modules_considered: 3, agreement_ratio: 0.66, outcome_votes: { PROCEED: 2 } },
          explain_brief: "ATLAS merge v1 => PROCEED",
        },
      },
    ],
  }),
  fetchProductionTurnPlan: async () => ({ ok: true, items: [] }),
}));

import ProductionDashboard from "./ProductionDashboard";

describe("TL Board page", () => {
  it("renders core sections and table headers with valid data", async () => {
    render(<ProductionDashboard />);

    // Title and sections
    expect(await screen.findByText(/TL Board/i)).toBeDefined();
    expect(await screen.findByText(/attenzione immediata/i)).toBeDefined();
    expect(await screen.findByText(/carico postazioni/i)).toBeDefined();
    expect(await screen.findByText(/sequenza consigliata/i)).toBeDefined();
    expect(await screen.findByText(/ATLAS PROCEED/i)).toBeDefined();
    expect(await screen.findByText(/score 0.78/i)).toBeDefined();
    expect(await screen.findByText(/ATLAS merge v1 => PROCEED/i)).toBeDefined();

    // Table headers
    expect(await screen.findByText(/codice/i)).toBeDefined();
    expect((await screen.findAllByText(/postazione/i)).length).toBeGreaterThan(0);
    expect(await screen.findByText(/qta totale/i)).toBeDefined();
    expect(await screen.findByText(/righe/i)).toBeDefined();
    expect(await screen.findByText(/prio/i)).toBeDefined();
  });
});
