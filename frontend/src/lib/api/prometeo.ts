const configuredApiBase =
  import.meta.env.VITE_PROMETEO_API_BASE?.replace(/\/+$/, "") || "";

const isLocalFrontend =
  typeof window !== "undefined" &&
  ["localhost", "127.0.0.1"].includes(window.location.hostname);

const API_BASE = isLocalFrontend ? "" : configuredApiBase;

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

export type ArticleSpecificationAcquisitionRequest = {
  image_base64: string;
};

export type ArticleSpecificationAcquisitionDetails = {
  ok: boolean;
  status: string;
  source_id: string | null;
  source_hash: string | null;
  media_type: string | null;
  error_code: string | null;
};

export type ArticleSpecificationFacadeResult = {
  ok: boolean;
  status: string;
  writer_called: boolean;
  source_id: string | null;
  error_code: string | null;
};

export type ArticleSpecificationAcquisitionResponse = {
  ok: boolean;
  status: string;
  source_id: string | null;
  semantic_status: string | null;
  writer_called: boolean;
  persisted: boolean;
  requires_review: boolean;
  error_code: string | null;
  acquisition: ArticleSpecificationAcquisitionDetails;
  review_payloads: Record<string, unknown>[];
  facade_results: ArticleSpecificationFacadeResult[];
};

export async function acquireArticleSpecification(
  payload: ArticleSpecificationAcquisitionRequest
) {
  return apiPost<ArticleSpecificationAcquisitionResponse>(
    "/article-specification/acquire",
    payload
  );
}

export type ArticleSpecificationConfirmationRequest = {
  article: string;
  operational_class: string;
  planner_eligible: boolean;
  tl_confirmation_required: boolean;
  authority_role: string;
  audit_note: string;
  source_id?: string;
  confirmed_at?: string;
  material?: string;
  drawing?: string;
  description?: string;
};

export type ArticleSpecificationConfirmationResponse = {
  ok: boolean;
  status: string;
  source_id: string;
  writer_called: boolean;
  persisted: boolean;
  created: boolean;
  updated: boolean;
  error_code: string | null;
};

export async function confirmArticleSpecification(
  payload: ArticleSpecificationConfirmationRequest
) {
  return apiPost<ArticleSpecificationConfirmationResponse>(
    "/article-specification/confirm",
    payload
  );
}

export type ProductionProgramImageOCRAcquisitionRequest = {
  image_base64: string;
};

export type ProductionProgramImageOCRAcquisitionResponse = {
  ok: boolean;
  status: string;
  source_id: string | null;
  source_hash: string | null;
  media_type: string | null;
  provider: string | null;
  error_code: string | null;
  requires_confirmation: boolean;
  semantic_status: string;
  persisted: boolean;
  writer_called: boolean;
  planner_called: boolean;
  pattern_learning_called: boolean;
  observed_text: string | null;
  normalized_lines: string[];
  snapshot_preview: Record<string, unknown> | null;
};

export async function acquireProductionProgramImageOCR(
  payload: ProductionProgramImageOCRAcquisitionRequest
) {
  return apiPost<ProductionProgramImageOCRAcquisitionResponse>(
    "/production-program/image-ocr/acquire",
    payload
  );
}

export type ProductionProgramSnapshotConfirmationRequest = {
  source_id: string;
  source_hash: string;
  observed_text: string;
  snapshot_preview: Record<string, unknown>;
  actor_id: string;
  authority_role: "RESPONSABILE_PRODUZIONE";
  confirmed_at: string;
  audit_note: string;
};

export type ProductionProgramSnapshotConfirmationResponse = {
  ok: boolean;
  error_code: string | null;
  status: string;
  semantic_status: string;
  requires_confirmation: boolean;
  persisted: boolean;
  write_performed: boolean;
  registry_id: string | null;
  snapshot_id: string | null;
  version: number | null;
  source: string | null;
  source_id: string | null;
  source_hash: string | null;
  confirmed_by: {
    actor_id: string;
    authority_role: string;
  } | null;
  confirmed_at: string | null;
};

export async function confirmProductionProgramSnapshot(
  payload: ProductionProgramSnapshotConfirmationRequest
) {
  return apiPost<ProductionProgramSnapshotConfirmationResponse>(
    "/production-program-snapshot/confirm",
    payload
  );
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
