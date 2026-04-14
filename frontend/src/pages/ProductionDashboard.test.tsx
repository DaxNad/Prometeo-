import { describe, it, expect } from "vitest";
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
  fetchProductionSequence: async () => ({ ok: true, items: [] }),
  fetchProductionTurnPlan: async () => ({ ok: true, items: [] }),
}));

import ProductionDashboard from "./ProductionDashboard";

describe("TL Board page", () => {
  it("renders core sections with valid data", async () => {
    render(<ProductionDashboard />);

    // Title and sections
    expect(await screen.findByText(/TL Board/i)).toBeDefined();
    expect(await screen.findByText(/attenzione immediata/i)).toBeDefined();
    expect(await screen.findByText(/carico postazioni/i)).toBeDefined();
    expect(await screen.findByText(/sequenza consigliata/i)).toBeDefined();
    expect(await screen.findByText(/ordini visibili/i)).toBeDefined();
    expect(await screen.findByText(/ultimo aggiornamento/i)).toBeDefined();

    // Table headers
    expect(await screen.findByText(/codice/i)).toBeDefined();
    expect(await screen.findByText(/postazione/i)).toBeDefined();
    expect(await screen.findByText(/qta totale/i)).toBeDefined();
    expect(await screen.findByText(/righe/i)).toBeDefined();
    expect(await screen.findByText(/prio/i)).toBeDefined();
  });
});
