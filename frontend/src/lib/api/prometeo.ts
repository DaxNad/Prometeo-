import type { BoardItem, BoardResponse } from "../../types/production";

const API_BASE =
  import.meta.env.VITE_PROMETEO_API_BASE?.replace(/\/+$/, "") ||
  "https://prometeo-railway-bootstrap-production.up.railway.app";

async function apiGet<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "GET",
    headers: { Accept: "application/json" },
  });

  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`GET ${path} failed: ${res.status} ${text}`);
  }

  return res.json() as Promise<T>;
}

export type MachineLoadItem = {
  station: string;
  orders_total: number;
  blocked_total: number;
  red_total: number;
  yellow_total: number;
  green_total: number;
  quantity_total: number;
  open_events_total?: number;
  event_titles?: string;
};

export type MachineLoadResponse = {
  ok: boolean;
  items: MachineLoadItem[];
  warnings?: string[];
};

export type AgentRuntimeOperationalSummary = {
  line_id: string | null;
  orders_total: number;
  orders_monitor: number;
  orders_investigate: number;
  orders_ok: number;
  orders_blocked: number;
  orders_overdue: number;
  orders_urgent: number;
  legacy_bootstrap_count: number;
  domain_order_count: number;
};

export async function getProductionBoardState() {
  return apiGet<BoardResponse>("/production/board-state");
}

export async function updateOrder(order: Omit<BoardItem, "updated_at">) {
  const res = await fetch(`${API_BASE}/production/order`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify(order),
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`POST /production/order failed: ${res.status} ${text}`);
  }
  return res.json() as Promise<{ ok: boolean; order_id: string }>;
}

export async function getProductionMachineLoad() {
  return apiGet<MachineLoadResponse>("/production/machine-load");
}

export async function getAgentRuntimeOperationalSummary(lineId?: string | null) {
  const query = lineId ? `?line_id=${encodeURIComponent(lineId)}` : "";
  return apiGet<AgentRuntimeOperationalSummary>(
    `/agent-runtime/summary/operational${query}`
  );
}
