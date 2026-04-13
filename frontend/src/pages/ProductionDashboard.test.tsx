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

import Dashboard from "./Dashboard";

describe("PROMETEO TL dashboard", () => {
  it("renders core sections with valid data", async () => {
    render(<Dashboard />);

    // Title and sections
    expect(await screen.findByText(/PROMETEO TL/i)).toBeDefined();
    expect(await screen.findByText(/Sequence radar/i)).toBeDefined();
    expect(await screen.findByText(/ZAW status/i)).toBeDefined();
    expect(await screen.findByText(/Board segnali/i)).toBeDefined();
    expect(await screen.findByText(/Turn plan/i)).toBeDefined();

    // Table headers
    expect(await screen.findByText(/segnale/i)).toBeDefined();
    expect(await screen.findByText(/codice/i)).toBeDefined();
    expect(await screen.findByText(/postazione/i)).toBeDefined();
    expect(await screen.findByText(/qta/i)).toBeDefined();
    expect(await screen.findByText(/righe/i)).toBeDefined();
  });
});
