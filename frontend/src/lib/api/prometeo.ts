const API_BASE =
  import.meta.env.VITE_PROMETEO_API_BASE?.replace(/\/+$/, "") ||
  "https://prometeo-railway-bootstrap-production.up.railway.app";

async function apiGet<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "GET",
    headers: {
      Accept: "application/json",
    },
  });

  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`GET ${path} failed: ${res.status} ${text}`);
  }

  return res.json() as Promise<T>;
}


function getApiKey(): string {
  if (typeof window === "undefined") return "";
  return window.localStorage.getItem("PROMETEO_API_KEY") || "";
}

async function apiPost<T>(path: string, body: unknown): Promise<T> {
  const apiKey = getApiKey();

  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
      ...(apiKey ? { "X-API-Key": apiKey } : {}),
    },
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`POST ${path} failed: ${res.status} ${text}`);
  }

  return res.json() as Promise<T>;
}

export type TLChatRequest = {
  question: string;
  context?: {
    article?: string;
    station?: string;
    drawing?: string;
    [key: string]: unknown;
  };
};

export type TLChatResponse = {
  ok: boolean;
  mode: string;
  answer: string;
  confidence: string;
  risk: string | null;
  recommended_action: string | null;
  requires_confirmation: boolean;
  technical_details_hidden: boolean;
};

export async function tlChat(payload: TLChatRequest) {
  return apiPost<TLChatResponse>("/tl/chat", payload);
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

export async function getProductionBoard<T = unknown>() {
  return apiGet<T>("/production/board");
}

export async function getProductionDelays<T = unknown>() {
  return apiGet<T>("/production/delays");
}

export async function getProductionLoad<T = unknown>() {
  return apiGet<T>("/production/load");
}

export async function getProductionSequence<T = unknown>() {
  return apiGet<T>("/production/sequence");
}

export async function getProductionTurnPlan<T = unknown>() {
  return apiGet<T>("/production/turn-plan");
}

export async function getProductionMachineLoad() {
  return apiGet<MachineLoadResponse>("/production/machine-load");
}

export async function getAgentRuntimeOperationalSummary(lineId: string) {
  const safeLineId = encodeURIComponent(lineId);
  return apiGet<AgentRuntimeOperationalSummary>(
    `/agent-runtime/summary/operational?line_id=${safeLineId}`
  );
}
